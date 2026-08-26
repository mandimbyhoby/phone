"""
paiements.py — Intégration des passerelles de paiement
=======================================================
Méthodes gérées :
  * carte        → Stripe Checkout (Visa, Mastercard, Amex, Apple Pay, Google Pay)
  * paypal       → PayPal Checkout (REST API v2)
  * orange_money → Orange Money (API marchand, configurable)
  * especes      → Paiement à la livraison (traité directement dans les vues)

MODE DÉMO :
  Si les clés API ne sont pas configurées (vide), le paiement est SIMULÉ :
  la commande est marquée payée automatiquement pour permettre de tester
  tout le parcours sans compte marchand.

DEVISE :
  L'Ariary (MGA) n'est pas supporté par Stripe/PayPal → le montant est converti
  en EUR avec le taux configurable PAIEMENT_TAUX_EUR (défaut 1 EUR = 5000 Ar).
"""
from __future__ import annotations

import logging
import uuid
from decimal import Decimal

import requests
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from .factures import envoyer_facture

logger = logging.getLogger(__name__)


# ============================================================
# UTILITAIRES
# ============================================================

def en_mode_demo() -> bool:
    """Vrai si aucune clé n'est configurée → paiement simulé."""
    return not settings.STRIPE_SECRET_KEY and not settings.PAYPAL_CLIENT_ID


def convertir_en_eur(montant_ar: Decimal) -> int:
    """Convertit un montant en Ariary vers EUR (centimes) pour Stripe/PayPal."""
    taux = Decimal(str(settings.PAIEMENT_TAUX_EUR))
    centimes = (Decimal(montant_ar) / taux) * 100
    return int(centimes.quantize(Decimal("1")))


def generer_reference() -> str:
    return f"PAY-{uuid.uuid4().hex[:12].upper()}"


def marquer_paye(paiement, transaction_id="", email=""):
    """Marque un paiement comme payé et la commande comme confirmée."""
    if paiement.statut != "paye":
        paiement.statut = "paye"
        paiement.transaction_id = transaction_id or paiement.transaction_id
        if email:
            paiement.email_payeur = email
        paiement.date_paiement = timezone.now()
        paiement.save()
        commande = paiement.commande
        if commande.statut == "en_attente":
            commande.statut = "confirmee"
            commande.save()
        try:
            envoyer_facture(commande)
        except Exception:
            logger.exception("Erreur lors de l'envoi de la facture de la commande #%s", commande.id)
    return paiement


# ============================================================
# STRIPE (cartes bancaires)
# ============================================================

def creer_paiement_stripe(paiement, request) -> str:
    """Crée une session Stripe Checkout. Retourne l'URL de redirection.

    En mode démo, marque le paiement payé et retourne l'URL de succès.
    """
    if not settings.STRIPE_SECRET_KEY:
        logger.info("Stripe non configuré → mode démo")
        marquer_paye(paiement)
        return reverse("commande_succes", args=[paiement.commande_id])

    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    commande = paiement.commande
    montant_eur = convertir_en_eur(commande.total)

    base_url = request.build_absolute_uri("/").rstrip("/")
    session = stripe.checkout.Session.create(
        mode="payment",
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": f"Commande #{commande.id} — Phone Store",
                    "description": (
                        f"{len(commande.lignes.all())} article(s) — {commande.nom}"
                    ),
                },
                "unit_amount": montant_eur,
            },
            "quantity": 1,
        }],
        customer_email=commande.email,
        metadata={"commande_id": str(commande.id), "paiement_reference": paiement.reference},
        success_url=base_url + reverse("paiement_succes", args=[commande.id]),
        cancel_url=base_url + reverse("paiement_annule", args=[commande.id]),
    )

    paiement.transaction_id = session.id
    paiement.save()
    return session.url


def verifier_paiement_stripe(paiement) -> bool:
    """Vérifie l'état d'une session Stripe et marque payé si complet."""
    if not settings.STRIPE_SECRET_KEY:
        return True
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(paiement.transaction_id)
        if session.payment_status == "paid":
            marquer_paye(paiement, transaction_id=session.payment_intent or session.id)
            return True
    except Exception as exc:  # pragma: no cover
        logger.error("Erreur vérification Stripe : %s", exc)
    return False


# ============================================================
# PAYPAL
# ============================================================

def _token_paypal() -> str:
    """Récupère un access token PayPal (OAuth2 client_credentials)."""
    url = (
        "https://api-m.sandbox.paypal.com/v1/oauth2/token"
        if settings.PAYPAL_ENV != "live"
        else "https://api-m.paypal.com/v1/oauth2/token"
    )
    resp = requests.post(
        url,
        data={"grant_type": "client_credentials"},
        auth=(settings.PAYPAL_CLIENT_ID, settings.PAYPAL_CLIENT_SECRET),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def creer_paiement_paypal(paiement, request) -> str:
    """Crée une commande PayPal (orders v2). Retourne l'URL d'approbation.

    En mode démo, marque le paiement payé et retourne l'URL de succès.
    """
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        logger.info("PayPal non configuré → mode démo")
        marquer_paye(paiement)
        return reverse("commande_succes", args=[paiement.commande_id])

    commande = paiement.commande
    montant_eur = float(convertir_en_eur(commande.total)) / 100.0
    base_url = request.build_absolute_uri("/").rstrip("/")

    headers = {
        "Authorization": f"Bearer {_token_paypal()}",
        "Content-Type": "application/json",
    }
    payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "reference_id": paiement.reference,
            "amount": {"currency_code": "EUR", "value": f"{montant_eur:.2f}"},
            "description": f"Commande #{commande.id} — Phone Store",
        }],
        "application_context": {
            "brand_name": "Phone Store",
            "user_action": "PAY_NOW",
            "return_url": base_url + reverse("paiement_succes", args=[commande.id]),
            "cancel_url": base_url + reverse("paiement_annule", args=[commande.id]),
        },
    }
    url = (
        "https://api-m.sandbox.paypal.com/v2/checkout/orders"
        if settings.PAYPAL_ENV != "live"
        else "https://api-m.paypal.com/v2/checkout/orders"
    )
    resp = requests.post(url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    paiement.transaction_id = data["id"]
    paiement.save()

    for lien in data.get("links", []):
        if lien.get("rel") == "approve":
            return lien["href"]
    raise RuntimeError("PayPal : lien d'approbation introuvable")


def capturer_paiement_paypal(paiement) -> bool:
    """Capture la commande PayPal après approbation. Retourne True si payé."""
    if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
        return True
    headers = {
        "Authorization": f"Bearer {_token_paypal()}",
        "Content-Type": "application/json",
    }
    url = (
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{paiement.transaction_id}/capture"
        if settings.PAYPAL_ENV != "live"
        else f"https://api-m.paypal.com/v2/checkout/orders/{paiement.transaction_id}/capture"
    )
    resp = requests.post(url, headers=headers, timeout=30)
    if resp.status_code in (200, 201):
        data = resp.json()
        marquer_paye(paiement, transaction_id=data.get("id", paiement.transaction_id))
        return True
    logger.error("PayPal capture échouée : %s", resp.text)
    return False


# ============================================================
# ORANGE MONEY
# ============================================================

def payer_orange_money(paiement, telephone: str, request) -> str:
    """Déclenche un paiement Orange Money.

    API marchand Orange (à configurer dans settings) :
      ORANGE_MONEY_CLIENT_ID / ORANGE_MONEY_CLIENT_SECRET /
      ORANGE_MONEY_MERCHANT_NUMBER / ORANGE_MONEY_BASE_URL

    En mode démo, marque le paiement payé et retourne l'URL de succès.
    """
    paiement.telephone = telephone
    paiement.save()

    if not (settings.ORANGE_MONEY_CLIENT_ID and settings.ORANGE_MONEY_MERCHANT_NUMBER):
        logger.info("Orange Money non configuré → mode démo")
        marquer_paye(paiement)
        return reverse("commande_succes", args=[paiement.commande_id])

    # --- Exemple d'implémentation avec l'API marchand Orange Money ---
    # 1. Token OAuth2
    token_url = f"{settings.ORANGE_MONEY_BASE_URL}/oauth/v2/token"
    token_resp = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": settings.ORANGE_MONEY_CLIENT_ID,
            "client_secret": settings.ORANGE_MONEY_CLIENT_SECRET,
        },
        timeout=30,
    )
    token_resp.raise_for_status()
    token = token_resp.json()["access_token"]

    # 2. Demande de paiement (OrangeMoneyWebPayment)
    commande = paiement.commande
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "merchant_key": settings.ORANGE_MONEY_MERCHANT_NUMBER,
        "currency": "MGA",
        "order_id": paiement.reference,
        "amount": float(commande.total),
        "return_url": request.build_absolute_uri(reverse("paiement_succes", args=[commande.id])),
        "cancel_url": request.build_absolute_uri(reverse("paiement_annule", args=[commande.id])),
        "notif_url": request.build_absolute_uri(reverse("webhook_orange_money")),
        "lang": "fr",
    }
    pay_url = f"{settings.ORANGE_MONEY_BASE_URL}/orangerestservice/v1.1/webpayment"
    resp = requests.post(pay_url, json=payload, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    paiement.transaction_id = data.get("payment_url", "")
    paiement.save()
    return data.get("payment_url", reverse("paiement_annule", args=[commande.id]))


def verifier_paiement_orange_money(paiement) -> bool:
    """Vérifie le statut d'un paiement Orange Money (statut commande marchand)."""
    if not settings.ORANGE_MONEY_CLIENT_ID:
        return True
    # Selon l'API Orange, l'état est transmis via le webhook notif_url.
    # En l'absence d'un webhook reçu, on considère le paiement en attente.
    return paiement.statut == "paye"
