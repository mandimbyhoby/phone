from django.urls import path
from rest_framework.routers import DefaultRouter

from .api import AvisViewSet, CategorieViewSet, ProduitViewSet, ReactionProduitAPIView
from .api_compte import (
    AnnulerCommandeAPIView,
    ChangerMotDePasseAPIView,
    CommandeCheckoutAPIView,
    ConnexionAPIView,
    ContactAPIView,
    DeconnexionAPIView,
    InscriptionAPIView,
    MesCommandesAPIView,
    PanierAjouterAPIView,
    PanierAPIView,
    PanierModifierAPIView,
    PanierSupprimerAPIView,
    ProfilAPIView,
    SessionAPIView,
)
from .views import dashboard_stats_api


router = DefaultRouter()
router.register('categories', CategorieViewSet, basename='api-categorie')
router.register('produits', ProduitViewSet, basename='api-produit')
router.register('avis', AvisViewSet, basename='api-avis')

urlpatterns = router.urls + [
    path('dashboard/', dashboard_stats_api, name='api-dashboard'),

    # Réactions « cœur » sur les produits (une par personne et par produit)
    path('produits/<int:produit_id>/reaction/', ReactionProduitAPIView.as_view(), name='api-produit-reaction'),

    # Panier (session)
    path('panier/', PanierAPIView.as_view(), name='api-panier'),
    path('panier/ajouter/<int:id>/', PanierAjouterAPIView.as_view(), name='api-panier-ajouter'),
    path('panier/modifier/<int:id>/', PanierModifierAPIView.as_view(), name='api-panier-modifier'),
    path('panier/supprimer/<int:id>/', PanierSupprimerAPIView.as_view(), name='api-panier-supprimer'),

    # Commandes
    path('commandes/', MesCommandesAPIView.as_view(), name='api-commandes'),
    path('commandes/<int:commande_id>/annuler/', AnnulerCommandeAPIView.as_view(), name='api-commande-annuler'),
    path('commande/', CommandeCheckoutAPIView.as_view(), name='api-commande'),

    # Profil
    path('profil/', ProfilAPIView.as_view(), name='api-profil'),
    path('profil/mot-de-passe/', ChangerMotDePasseAPIView.as_view(), name='api-profil-mot-de-passe'),

    # Contact
    path('contact/', ContactAPIView.as_view(), name='api-contact'),

    # Authentification
    path('session/', SessionAPIView.as_view(), name='api-session'),
    path('inscription/', InscriptionAPIView.as_view(), name='api-inscription'),
    path('connexion/', ConnexionAPIView.as_view(), name='api-connexion'),
    path('deconnexion/', DeconnexionAPIView.as_view(), name='api-deconnexion'),
]
