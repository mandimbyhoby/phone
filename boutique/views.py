from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Produit, Categorie, Avis, Commande, LigneCommande, Paiement, Profil
from .forms import (
    AvisForm, CommandeForm, ContactForm, InscriptionForm, ConnexionForm,
    ProfilForm, ChangerMotDePasseForm,
)
from .panier import recuperer_panier, nombre_articles
from . import paiements as paiements_module

# ============================================================
# A U T H E N T I F I C A T I O N
# ============================================================

def inscription(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {form.cleaned_data['nom_complet']} ! Votre compte a été créé.")
            return redirect('accueil')
    else:
        form = InscriptionForm()
    return render(request, 'registration/register.html', {'form': form})


def connexion(request):
    if request.user.is_authenticated:
        return redirect('accueil')
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Bon retour, {user.username} !")
            prochaine = request.POST.get('next') or request.GET.get('next') or 'accueil'
            return redirect(prochaine)
        messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    else:
        form = ConnexionForm()
    return render(request, 'registration/login.html', {'form': form})


def deconnexion(request):
    logout(request)
    messages.success(request, "Vous êtes déconnecté. À bientôt !")
    return redirect('accueil')


@login_required
def profil(request):
    profil, _ = Profil.objects.get_or_create(utilisateur=request.user)
    if request.method == 'POST':
        # Suppression de la photo si la case est cochée
        if request.POST.get('photo_clear') and profil.photo:
            profil.photo.delete(save=False)
            profil.photo = None
            profil.save()
            messages.success(request, "Votre photo de profil a été supprimée.")
            return redirect('profil')
        form = ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Vos informations ont été mises à jour.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=profil, initial={
            'email': request.user.email,
        })
    commandes = request.user.commandes.all()[:10]
    return render(request, 'boutique/profil.html', {
        'form': form,
        'commandes': commandes,
        'profil': profil,
    })


@login_required
def changer_mot_de_passe(request):
    if request.method == 'POST':
        form = ChangerMotDePasseForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # garde la session active
            messages.success(request, "Votre mot de passe a été changé avec succès.")
            return redirect('profil')
    else:
        form = ChangerMotDePasseForm(request.user)
    return render(request, 'boutique/changer_mot_de_passe.html', {'form': form})


@login_required
def mes_commandes(request):
    commandes = request.user.commandes.prefetch_related('lignes__produit', 'paiement')
    return render(request, 'boutique/mes_commandes.html', {'commandes': commandes})

# ============================================================
# P A N I E R  (session)
# ============================================================

def ajouter_au_panier(request, id):
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=id, disponible=True)
        cart = request.session.get('cart', {})
        key = str(produit.id)
        quantite = int(request.POST.get('quantite', 1))
        if key in cart:
            cart[key]['quantite'] = min(cart[key]['quantite'] + quantite, produit.stock)
        else:
            cart[key] = {'quantite': min(quantite, produit.stock)}
        request.session['cart'] = cart
        # Réponse partielle HTMX : badge panier + mini panier
        items, total = recuperer_panier(request)
        return render(request, 'boutique/partials/cart_badge.html', {
            'nombre': nombre_articles(request),
            'items': items,
            'total': total,
        })
    return redirect('accueil')


def mettre_a_jour_panier(request, id):
    if request.method == 'POST':
        produit = get_object_or_404(Produit, id=id)
        cart = request.session.get('cart', {})
        key = str(produit.id)
        action = request.POST.get('action', 'set')
        if action == 'augmenter':
            cart[key]['quantite'] = min(cart[key].get('quantite', 1) + 1, produit.stock)
        elif action == 'diminuer':
            cart[key]['quantite'] = max(cart[key].get('quantite', 1) - 1, 1)
        else:
            q = int(request.POST.get('quantite', 1))
            cart[key]['quantite'] = max(1, min(q, produit.stock))
        request.session['cart'] = cart
        items, total = recuperer_panier(request)
        return render(request, 'boutique/partials/cart_update.html', {
            'items': items,
            'total': total,
            'nombre': nombre_articles(request),
        })
    return redirect('panier')


def supprimer_du_panier(request, id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        cart.pop(str(id), None)
        request.session['cart'] = cart
        items, total = recuperer_panier(request)
        return render(request, 'boutique/partials/cart_update.html', {
            'items': items,
            'total': total,
            'nombre': nombre_articles(request),
        })
    return redirect('panier')


def panier(request):
    items, total = recuperer_panier(request)
    return render(request, 'boutique/panier.html', {
        'items': items,
        'total': total,
    })


# ============================================================
# C O M M A N D E S  &  P A I E M E N T S
# ============================================================

@login_required
def passer_commande(request):
    items, total = recuperer_panier(request)
    if not items:
        return redirect('accueil')

    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.utilisateur = request.user
            commande.total = total
            commande.save()
            # Enregistre les lignes et décrémente le stock
            for item in items:
                LigneCommande.objects.create(
                    commande=commande,
                    produit=item['produit'],
                    quantite=item['quantite'],
                    prix_unitaire=item['produit'].prix_actuel,
                )
                produit = item['produit']
                produit.stock = max(0, produit.stock - item['quantite'])
                produit.save()
            request.session['cart'] = {}

            # Création du paiement associé
            methode = form.cleaned_data['methode_paiement']
            paiement = Paiement.objects.create(
                commande=commande,
                methode=methode,
                montant=total,
                reference=paiements_module.generer_reference(),
            )

            # Redirection selon la méthode choisie
            if methode == 'especes':
                paiements_module.marquer_paye(paiement)
                messages.success(request, "Votre commande a bien été enregistrée ! Paiement à la livraison.")
                return redirect('commande_succes', commande_id=commande.id)
            if methode == 'carte':
                url = paiements_module.creer_paiement_stripe(paiement, request)
                return redirect(url)
            if methode == 'paypal':
                url = paiements_module.creer_paiement_paypal(paiement, request)
                return redirect(url)
            if methode == 'orange_money':
                return redirect('paiement_orange_money', commande_id=commande.id)
    else:
        # Pré-remplit le formulaire avec les données du compte client
        initial = {}
        profil = Profil.objects.filter(utilisateur=request.user).first()
        if profil:
            initial = {
                'nom': profil.nom_complet or request.user.username,
                'email': request.user.email,
                'telephone': profil.telephone,
                'adresse': profil.adresse,
                'ville': profil.ville,
            }
        form = CommandeForm(initial=initial)

    return render(request, 'boutique/commande.html', {
        'form': form,
        'items': items,
        'total': total,
        'mode_demo': paiements_module.en_mode_demo(),
    })


@login_required
def paiement_orange_money(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    # Le client ne peut payer que ses propres commandes
    if commande.utilisateur != request.user:
        messages.error(request, "Cette commande ne vous appartient pas.")
        return redirect('accueil')
    paiement = getattr(commande, 'paiement', None)
    if not paiement or paiement.methode != 'orange_money':
        return redirect('commande_succes', commande_id=commande.id)
    if paiement.statut == 'paye':
        return redirect('commande_succes', commande_id=commande.id)

    if request.method == 'POST':
        telephone = request.POST.get('telephone', '').strip()
        if not telephone:
            messages.error(request, "Veuillez saisir votre numéro Orange Money.")
        else:
            url = paiements_module.payer_orange_money(paiement, telephone, request)
            if url:
                return redirect(url)
            messages.error(request, "Le paiement Orange Money a échoué. Réessayez.")

    return render(request, 'boutique/paiement_orange_money.html', {
        'commande': commande,
        'paiement': paiement,
        'mode_demo': paiements_module.en_mode_demo(),
    })


@login_required
def paiement_succes(request, commande_id):
    """Page de retour après un paiement en ligne (Stripe / PayPal / OM)."""
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.utilisateur != request.user:
        messages.error(request, "Cette commande ne vous appartient pas.")
        return redirect('accueil')
    paiement = getattr(commande, 'paiement', None)

    if paiement and paiement.statut == 'en_attente':
        if paiement.methode == 'carte':
            paiements_module.verifier_paiement_stripe(paiement)
        elif paiement.methode == 'paypal':
            paiements_module.capturer_paiement_paypal(paiement)
        else:
            paiements_module.verifier_paiement_orange_money(paiement)
        paiement.refresh_from_db()

    if paiement and paiement.statut == 'paye':
        messages.success(request, "Paiement confirmé, merci !")
        return redirect('commande_succes', commande_id=commande.id)

    messages.error(request, "Le paiement n'a pas abouti.")
    return redirect('paiement_annule', commande_id=commande.id)


@login_required
def paiement_annule(request, commande_id):
    """Page d'annulation : commande annulée + stock restauré."""
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.utilisateur != request.user:
        messages.error(request, "Cette commande ne vous appartient pas.")
        return redirect('accueil')
    paiement = getattr(commande, 'paiement', None)

    if paiement and paiement.statut == 'en_attente':
        # Restaure le stock
        for ligne in commande.lignes.all():
            produit = ligne.produit
            produit.stock += ligne.quantite
            produit.save()
        commande.statut = 'annulee'
        commande.save()
        paiement.statut = 'echoue'
        paiement.save()

    return render(request, 'boutique/paiement_annule.html', {'commande': commande})


@login_required
def commande_succes(request, commande_id):
    commande = get_object_or_404(Commande, id=commande_id)
    if commande.utilisateur != request.user:
        messages.error(request, "Cette commande ne vous appartient pas.")
        return redirect('accueil')
    return render(request, 'boutique/commande_succes.html', {'commande': commande})


# ============================================================
# W E B H O O K S  (appels serveur → serveur, sans CSRF)
# ============================================================

@csrf_exempt
def webhook_stripe(request):
    """Reçoit les événements Stripe (checkout.session.completed, ...)."""
    payload = request.body
    sig = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            import stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            event = stripe.Webhook.construct_event(payload, sig, settings.STRIPE_WEBHOOK_SECRET)
        except Exception:
            return JsonResponse({'statut': 'signature invalide'}, status=400)
    else:
        # Mode démo / développement : décodage simple du payload
        import json
        try:
            event = json.loads(payload)
        except Exception:
            return JsonResponse({'statut': 'payload invalide'}, status=400)

    if event.get('type') == 'checkout.session.completed':
        session = event['data']['object']
        commande_id = session.get('metadata', {}).get('commande_id')
        if commande_id:
            paiement = Paiement.objects.filter(commande_id=commande_id).first()
            if paiement:
                paiements_module.marquer_paye(
                    paiement,
                    transaction_id=session.get('payment_intent') or session.get('id'),
                    email=session.get('customer_email') or '',
                )
    return JsonResponse({'statut': 'ok'})


@csrf_exempt
def webhook_paypal(request):
    """Reçoit les webhooks PayPal (optionnel — la capture se fait au retour)."""
    if request.body:
        # En production : vérifier la signature PayPal (PAYMENT.CAPTURE.COMPLETED)
        import json
        try:
            event = json.loads(request.body)
            if event.get('event_type') == 'PAYMENT.CAPTURE.COMPLETED':
                # Le paiement est capturé au retour du client ; ici on logue
                pass
        except Exception:
            pass
    return JsonResponse({'statut': 'ok'})


@csrf_exempt
def webhook_orange_money(request):
    """Reçoit la notification de paiement Orange Money."""
    if request.body:
        import json
        try:
            data = json.loads(request.body)
            reference = data.get('order_id', '')
            statut = data.get('status', data.get('order_status', ''))
            paiement = Paiement.objects.filter(reference=reference).first()
            if paiement and str(statut).lower() in ('paid', 'success', 'successful', 'completed'):
                paiements_module.marquer_paye(paiement, transaction_id=data.get('txnid', ''))
        except Exception:
            pass
    return JsonResponse({'statut': 'ok'})


# ============================================================
# P A G E S   P U B L I Q U E S
# ============================================================

def accueil(request):
    produits = Produit.objects.filter(disponible=True)

    # Recherche
    q_values = [v for v in request.GET.getlist('q') if v.strip()]
    q = q_values[0] if q_values else ''
    if q:
        produits = produits.filter(
            Q(nom__icontains=q) | Q(marque__icontains=q) | Q(description__icontains=q)
        )

    # Filtre catégorie
    categorie_slug = request.GET.get('categorie', '')
    if categorie_slug:
        produits = produits.filter(categorie__slug=categorie_slug)

    # Tri
    tri = request.GET.get('tri', 'nouveaute')
    if tri == 'prix_asc':
        produits = produits.annotate(
            prix_effectif=Coalesce('prix_promo', 'prix')
        ).order_by('prix_effectif')
    elif tri == 'prix_desc':
        produits = produits.annotate(
            prix_effectif=Coalesce('prix_promo', 'prix')
        ).order_by('-prix_effectif')
    elif tri == 'promo':
        produits = produits.filter(prix_promo__isnull=False).order_by('-date_ajout')
    elif tri == 'nom':
        produits = produits.order_by('nom')
    else:
        produits = produits.order_by('-date_ajout')

    # Promotions pour la bannière
    promos = Produit.objects.filter(disponible=True, prix_promo__isnull=False)[:3]

    return render(request, 'boutique/index.html', {
        'produits': produits,
        'categories': Categorie.objects.all(),
        'q': q,
        'categorie_active': categorie_slug,
        'tri': tri,
        'promos': promos,
    })


def detail_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    avis = produit.avis.all()
    similaires = Produit.objects.filter(
        categorie=produit.categorie, disponible=True
    ).exclude(id=produit.id)[:4]

    if request.method == 'POST':
        form = AvisForm(request.POST)
        if form.is_valid():
            avis_obj = form.save(commit=False)
            avis_obj.produit = produit
            avis_obj.save()
            messages.success(request, "Merci pour votre avis !")
            return redirect('detail_produit', id=produit.id)
    else:
        form = AvisForm()

    return render(request, 'boutique/detail.html', {
        'produit': produit,
        'avis': avis,
        'similaires': similaires,
        'form': form,
    })


def apropos(request):
    return render(request, 'boutique/apropos.html', {
        'nombre_produits': Produit.objects.filter(disponible=True).count(),
        'nombre_commandes': Commande.objects.count(),
    })


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre message a bien été envoyé, merci !")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'boutique/contact.html', {'form': form})