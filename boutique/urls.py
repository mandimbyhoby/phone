from django.urls import path
from . import views

urlpatterns = [
    path('', views.accueil, name='accueil'),
     path('produit/<int:id>/', views.detail_produit, name='detail_produit'),
]