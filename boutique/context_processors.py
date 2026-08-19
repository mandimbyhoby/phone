from .panier import recuperer_panier, nombre_articles
from .models import Commande


def panier_global(request):
    """Rend le panier accessible dans tous les templates."""
    items, total = recuperer_panier(request)
    return {
        'nombre_articles_panier': nombre_articles(request),
        'panier_items': items,
        'panier_total': total,
        'panier_session': request.session.get('cart', {}),
    }


def notifications_global(request):
    """
    Signal de notification pour le gérant : compte les nouvelles commandes
    (statut 'en_attente') et liste les 5 plus récentes. Seuls les membres du
    staff (admin) voient la cloche de notifications.
    """
    if not (request.user.is_authenticated and request.user.is_staff):
        return {
            'nombre_nouvelles_commandes': 0,
            'dernieres_commandes': [],
        }
    nouvelles = Commande.objects.filter(statut='en_attente').order_by('-date_commande')
    return {
        'nombre_nouvelles_commandes': nouvelles.count(),
        'dernieres_commandes': nouvelles[:5],
    }
