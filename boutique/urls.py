from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('produit/<int:id>/', views.detail_produit, name='detail_produit'),
    path('apropos/', views.apropos, name='apropos'),
    path('contact/', views.contact, name='contact'),
    path('qr-code/', views.qr_code, name='qr_code'),

    # ===== Compte client =====
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('profil/', views.profil, name='profil'),
    path('profil/mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),

    # ===== Mot de passe oublié =====
    path('mot-de-passe-oublie/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             subject_template_name='registration/password_reset_subject.txt',
             success_url=reverse_lazy('mot_de_passe_oublie_done'),
         ),
         name='mot_de_passe_oublie'),
    path('mot-de-passe-oublie/envoye/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html',
         ),
         name='mot_de_passe_oublie_done'),
    path('mot-de-passe-oublie/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('mot_de_passe_oublie_complet'),
         ),
         name='mot_de_passe_oublie_confirm'),
    path('mot-de-passe-oublie/termine/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html',
         ),
         name='mot_de_passe_oublie_complet'),

    # Panier
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/modifier/<int:id>/', views.mettre_a_jour_panier, name='mettre_a_jour_panier'),
    path('panier/supprimer/<int:id>/', views.supprimer_du_panier, name='supprimer_du_panier'),

    # Commandes
    path('commande/', views.passer_commande, name='passer_commande'),
    path('commande/succes/<int:commande_id>/', views.commande_succes, name='commande_succes'),

    # Paiements
    path('paiement/orange-money/<int:commande_id>/', views.paiement_orange_money, name='paiement_orange_money'),
    path('paiement/succes/<int:commande_id>/', views.paiement_succes, name='paiement_succes'),
    path('paiement/annule/<int:commande_id>/', views.paiement_annule, name='paiement_annule'),

    # Webhooks (appels serveur → serveur)
    path('webhook/stripe/', views.webhook_stripe, name='webhook_stripe'),
    path('webhook/paypal/', views.webhook_paypal, name='webhook_paypal'),
    path('webhook/orange-money/', views.webhook_orange_money, name='webhook_orange_money'),
]