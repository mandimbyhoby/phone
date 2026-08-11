from .models import Produit


def recuperer_panier(request):
    """Retourne la liste des articles du panier avec quantités et total."""
    cart = request.session.get('cart', {})
    items = []
    total = 0
    for produit_id, data in cart.items():
        produit = Produit.objects.filter(id=produit_id).first()
        if not produit:
            continue
        quantite = int(data.get('quantite', 1))
        prix = float(produit.prix_actuel)
        sous_total = prix * quantite
        total += sous_total
        items.append({
            'produit': produit,
            'quantite': quantite,
            'prix': prix,
            'sous_total': sous_total,
        })
    return items, total


def nombre_articles(request):
    cart = request.session.get('cart', {})
    return sum(int(d.get('quantite', 1)) for d in cart.values())
