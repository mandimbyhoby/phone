from .panier import recuperer_panier, nombre_articles


def panier_global(request):
    """Rend le panier accessible dans tous les templates."""
    items, total = recuperer_panier(request)
    return {
        'nombre_articles_panier': nombre_articles(request),
        'panier_items': items,
        'panier_total': total,
        'panier_session': request.session.get('cart', {}),
    }
