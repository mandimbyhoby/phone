"""API JSON « client » consommée par les composants React.

Ce module complète `api.py` (catalogue public) avec les parcours qui touchent
à la session et au compte utilisateur : panier, commandes, profil, contact et
authentification. Toutes les réponses sont en JSON afin que l'interface React
puisse mettre à jour la page sans rechargement.
"""
from django.conf import settings
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import paiements as paiements_module
from .forms import (
    ChangerMotDePasseForm,
    CommandeForm,
    ContactForm,
    InscriptionForm,
    ProfilForm,
    methodes_paiement_disponibles,
)
from .models import Commande, LigneCommande, Paiement, Produit, Profil
from .panier import nombre_articles, recuperer_panier


# ============================================================
# S E R I A L I S A T I O N
# ============================================================

def _image_url(request, image_field):
    if not image_field:
        return None
    try:
        url = image_field.url
    except ValueError:
        return None
    return request.build_absolute_uri(url) if request else url


def serialiser_panier(request):
    """Représentation JSON du panier (session) pour React."""
    items, total = recuperer_panier(request)
    return {
        'items': [
            {
                'produit_id': item['produit'].id,
                'nom': item['produit'].nom,
                'marque': item['produit'].marque,
                'prix': float(item['prix']),
                'quantite': item['quantite'],
                'sous_total': float(item['sous_total']),
                'stock': item['produit'].stock,
                'image_url': _image_url(request, item['produit'].image),
                'url': f"/produit/{item['produit'].id}/",
            }
            for item in items
        ],
        'total': float(total),
        'nombre': nombre_articles(request),
    }


def serialiser_commande(commande):
    paiement = getattr(commande, 'paiement', None)
    return {
        'id': commande.id,
        'date': commande.date_commande.isoformat(),
        'statut': commande.statut,
        'statut_display': commande.get_statut_display(),
        'total': float(commande.total),
        'nom': commande.nom,
        'ville': commande.ville,
        'annulable': commande.statut in ('en_attente', 'confirmee'),
        'facture_url': f"/commande/{commande.id}/facture/",
        'lignes': [
            {
                'produit_id': ligne.produit_id,
                'nom': ligne.produit.nom,
                'quantite': ligne.quantite,
                'prix_unitaire': float(ligne.prix_unitaire),
                'sous_total': float(ligne.sous_total),
                'url': f"/produit/{ligne.produit_id}/",
            }
            for ligne in commande.lignes.all()
        ],
        'paiement': (
            {
                'methode': paiement.methode,
                'methode_display': paiement.get_methode_display(),
                'statut': paiement.statut,
                'statut_display': paiement.get_statut_display(),
            }
            if paiement
            else None
        ),
    }


def serialiser_profil(request):
    profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
    return {
        'nom_complet': profil.nom_complet,
        'email': request.user.email,
        'telephone': profil.telephone,
        'ville': profil.ville,
        'adresse': profil.adresse,
        'photo_url': _image_url(request, profil.photo),
        'username': request.user.username,
    }


def _erreurs_form(form):
    return {champ: [str(e) for e in erreurs] for champ, erreurs in form.errors.items()}


# ============================================================
# P A N I E R
# ============================================================

class PanierAPIView(APIView):
    """Lecture du panier courant."""
    permission_classes = [AllowAny]

    def get(self, request):
        return Response(serialiser_panier(request))


class PanierAjouterAPIView(APIView):
    """Ajoute un produit au panier (ou incrémente sa quantité)."""
    permission_classes = [AllowAny]

    def post(self, request, id):
        produit = get_object_or_404(Produit, id=id, disponible=True)
        if produit.stock <= 0:
            return Response(
                {'detail': f"« {produit.nom} » est en rupture de stock."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            quantite = max(1, int(request.data.get('quantite', 1)))
        except (TypeError, ValueError):
            quantite = 1

        cart = request.session.get('cart', {})
        key = str(produit.id)
        if key in cart:
            cart[key]['quantite'] = min(cart[key]['quantite'] + quantite, produit.stock)
        else:
            cart[key] = {'quantite': min(quantite, produit.stock)}
        request.session['cart'] = cart

        data = serialiser_panier(request)
        data['detail'] = f"« {produit.nom} » ajouté au panier."
        return Response(data)


class PanierModifierAPIView(APIView):
    """Modifie la quantité d'une ligne du panier (set / augmenter / diminuer)."""
    permission_classes = [AllowAny]

    def post(self, request, id):
        produit = get_object_or_404(Produit, id=id)
        cart = request.session.get('cart', {})
        key = str(produit.id)
        if key not in cart:
            return Response(
                {'detail': "Ce produit n'est plus dans votre panier."},
                status=status.HTTP_404_NOT_FOUND,
            )

        action = request.data.get('action', 'set')
        actuelle = int(cart[key].get('quantite', 1))
        if action == 'augmenter':
            cart[key]['quantite'] = min(actuelle + 1, produit.stock)
        elif action == 'diminuer':
            cart[key]['quantite'] = max(actuelle - 1, 1)
        else:
            try:
                cible = int(request.data.get('quantite', actuelle))
            except (TypeError, ValueError):
                cible = actuelle
            cart[key]['quantite'] = max(1, min(cible, produit.stock))
        request.session['cart'] = cart
        return Response(serialiser_panier(request))


class PanierSupprimerAPIView(APIView):
    """Retire un produit du panier."""
    permission_classes = [AllowAny]

    def post(self, request, id):
        cart = request.session.get('cart', {})
        cart.pop(str(id), None)
        request.session['cart'] = cart
        return Response(serialiser_panier(request))


# ============================================================
# C O M M A N D E S
# ============================================================

class MesCommandesAPIView(APIView):
    """Historique des commandes du client connecté."""
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)
        commandes = request.user.commandes.prefetch_related('lignes__produit', 'paiement')
        return Response({'commandes': [serialiser_commande(c) for c in commandes]})


class AnnulerCommandeAPIView(APIView):
    """Annule une commande encore modifiable et remet le stock en place."""
    permission_classes = [AllowAny]

    def post(self, request, commande_id):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)

        commande = get_object_or_404(Commande, id=commande_id, utilisateur=request.user)
        if commande.statut not in ('en_attente', 'confirmee'):
            return Response(
                {'detail': "Cette commande ne peut plus être annulée."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            for ligne in commande.lignes.select_related('produit').all():
                produit = Produit.objects.select_for_update().get(pk=ligne.produit_id)
                produit.stock += ligne.quantite
                produit.save(update_fields=['stock'])
            commande.statut = 'annulee'
            commande.save(update_fields=['statut'])
            paiement = getattr(commande, 'paiement', None)
            if paiement and paiement.statut == 'paye':
                paiement.statut = 'echoue'
                paiement.save(update_fields=['statut'])

        try:
            from .factures import envoyer_email_annulation
            envoyer_email_annulation(commande)
        except Exception:  # pragma: no cover - l'email ne doit pas bloquer l'annulation
            pass

        return Response({
            'detail': f"La commande #{commande.id} a été annulée.",
            'commande': serialiser_commande(commande),
        })


class CommandeCheckoutAPIView(APIView):
    """Enregistre la commande du panier et renvoie l'URL de redirection."""
    permission_classes = [AllowAny]

    def get(self, request):
        """Pré-remplit le formulaire de commande avec les infos du client."""
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)
        profil = Profil.objects.filter(utilisateur=request.user).first()
        initial = {}
        if profil:
            initial = {
                'nom': profil.nom_complet or request.user.username,
                'email': request.user.email,
                'telephone': profil.telephone,
                'adresse': profil.adresse,
                'ville': profil.ville,
            }
        return Response({
            'initial': initial,
            'methode_paiement': 'especes',
            'methodes': [{'value': v, 'label': l} for v, l in methodes_paiement_disponibles()],
            'mode_demo': paiements_module.en_mode_demo(),
            'panier': serialiser_panier(request),
        })

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)

        items, total = recuperer_panier(request)
        if not items:
            return Response({'detail': 'Votre panier est vide.'}, status=status.HTTP_400_BAD_REQUEST)

        form = CommandeForm(request.data)
        if not form.is_valid():
            return Response({'erreurs': _erreurs_form(form)}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            produits_verrouilles = {}
            for item in items:
                produit = Produit.objects.select_for_update().get(
                    pk=item['produit'].pk,
                    disponible=True,
                )
                produits_verrouilles[produit.pk] = produit
                if item['quantite'] > produit.stock:
                    return Response(
                        {
                            'detail': (
                                f"Le stock de « {produit.nom} » est insuffisant. "
                                f"Il reste {produit.stock} article(s)."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            commande = form.save(commit=False)
            commande.utilisateur = request.user
            commande.total = total
            commande.save()
            for item in items:
                produit = produits_verrouilles[item['produit'].pk]
                LigneCommande.objects.create(
                    commande=commande,
                    produit=produit,
                    quantite=item['quantite'],
                    prix_unitaire=produit.prix_actuel,
                )
                produit.stock -= item['quantite']
                produit.save(update_fields=['stock'])
        request.session['cart'] = {}

        methode = form.cleaned_data['methode_paiement']
        paiement = Paiement.objects.create(
            commande=commande,
            methode=methode,
            montant=total,
            reference=paiements_module.generer_reference(),
        )

        if methode == 'especes':
            paiements_module.marquer_paye(paiement)
            return Response({
                'redirect': f"/commande/succes/{commande.id}/",
                'detail': "Commande enregistrée. Paiement à la livraison.",
            })

        try:
            if methode == 'carte':
                return Response({'redirect': paiements_module.creer_paiement_stripe(paiement, request)})
            if methode == 'paypal':
                return Response({'redirect': paiements_module.creer_paiement_paypal(paiement, request)})
            if methode == 'orange_money':
                return Response({'redirect': f"/paiement/orange-money/{commande.id}/"})
        except paiements_module.ConfigurationPaiementError:
            return Response(
                {
                    'detail': "Ce moyen de paiement n'est pas encore disponible.",
                    'redirect': f"/paiement/annule/{commande.id}/",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'redirect': f"/commande/succes/{commande.id}/"})


# ============================================================
# P R O F I L
# ============================================================

class ProfilAPIView(APIView):
    """Lecture et mise à jour du profil client (multipart accepté)."""
    permission_classes = [AllowAny]

    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'profil': serialiser_profil(request)})

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)

        profil, _ = Profil.objects.get_or_create(utilisateur=request.user)

        if request.data.get('photo_clear') in (True, 'true', 'True', '1', 'on'):
            if profil.photo:
                profil.photo.delete(save=False)
                profil.photo = None
                profil.save(update_fields=['photo'])
            return Response({'detail': 'Photo supprimée.', 'profil': serialiser_profil(request)})

        form = ProfilForm(request.data, request.FILES, instance=profil)
        if not form.is_valid():
            return Response({'erreurs': _erreurs_form(form)}, status=status.HTTP_400_BAD_REQUEST)
        form.save()
        return Response({'detail': 'Informations mises à jour.', 'profil': serialiser_profil(request)})


class ChangerMotDePasseAPIView(APIView):
    """Changement de mot de passe du client connecté."""
    permission_classes = [AllowAny]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentification requise.'}, status=status.HTTP_403_FORBIDDEN)
        form = ChangerMotDePasseForm(request.user, request.data)
        if not form.is_valid():
            return Response({'erreurs': _erreurs_form(form)}, status=status.HTTP_400_BAD_REQUEST)
        user = form.save()
        update_session_auth_hash(request, user)
        return Response({'detail': 'Mot de passe modifié avec succès.'})


# ============================================================
# C O N T A C T
# ============================================================

class ContactAPIView(APIView):
    """Réception du formulaire de contact sans rechargement de page."""
    permission_classes = [AllowAny]

    def post(self, request):
        form = ContactForm(request.data)
        if not form.is_valid():
            return Response({'erreurs': _erreurs_form(form)}, status=status.HTTP_400_BAD_REQUEST)

        message_contact = form.save()
        try:
            send_mail(
                subject=f"[Phone Store] {message_contact.sujet}",
                message=(
                    "Nouveau message reçu depuis le formulaire de contact du site.\n\n"
                    f"Nom : {message_contact.nom}\n"
                    f"Email : {message_contact.email}\n"
                    f"Sujet : {message_contact.sujet}\n"
                    f"Date : {message_contact.date:%d/%m/%Y à %H:%M}\n\n"
                    f"Message :\n{message_contact.message}\n"
                ),
                from_email=None,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
        except Exception:  # pragma: no cover - le message est déjà enregistré
            pass

        return Response({'detail': 'Votre message a bien été envoyé, merci !'})


# ============================================================
# A U T H E N T I F I C A T I O N
# ============================================================

class InscriptionAPIView(APIView):
    """Création de compte client en AJAX."""
    permission_classes = [AllowAny]

    def post(self, request):
        form = InscriptionForm(request.data)
        if not form.is_valid():
            return Response({'erreurs': _erreurs_form(form)}, status=status.HTTP_400_BAD_REQUEST)
        user = form.save()
        login(request, user)
        return Response({
            'detail': "Compte créé ! Bienvenue chez Phone Store.",
            'redirect': '/',
        }, status=status.HTTP_201_CREATED)


class ConnexionAPIView(APIView):
    """Connexion client en AJAX."""
    permission_classes = [AllowAny]

    def post(self, request):
        identifiant = (request.data.get('username') or '').strip()
        password = request.data.get('password') or ''

        # On accepte le nom d'utilisateur ou l'adresse email.
        username = identifiant
        if '@' in identifiant:
            user_obj = User.objects.filter(email__iexact=identifiant).first()
            if user_obj:
                username = user_obj.username

        user = authenticate(request, username=username, password=password)
        if user is None:
            return Response(
                {'detail': "Identifiants incorrects. Vérifiez votre saisie."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        login(request, user)
        return Response({
            'detail': f"Bonjour {user.get_full_name() or user.username} !",
            'redirect': '/',
        })


class DeconnexionAPIView(APIView):
    """Déconnexion du client."""
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Vous êtes déconnecté.', 'redirect': '/'})


class SessionAPIView(APIView):
    """État de session : utile pour adapter l'interface React."""
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user
        return Response({
            'authentifie': user.is_authenticated,
            'username': user.username if user.is_authenticated else None,
            'panier': nombre_articles(request),
        })
