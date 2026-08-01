from django.shortcuts import render, get_object_or_404
from .models import Produit

def accueil(request):
    produits = Produit.objects.filter(disponible=True)
    return render(request, 'boutique/index.html', {'produits': produits})


def detail_produit(request, id):
    produit = get_object_or_404(Produit, id=id)
    return render(request, 'boutique/detail.html', {'produit': produit})