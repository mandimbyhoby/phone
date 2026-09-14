"""Réactions « cœur » des visiteurs sur les produits.

Ce module centralise l'identification du visiteur et le calcul du résumé des
réactions. Il est utilisé par l'API JSON (`api.py`) et par les pages rendues
côté serveur (`views.py`), afin qu'un seul jeu de règles s'applique partout.
"""
from django.db.models import Count

from .models import Reaction

# Nom de l'attribut où l'on mémorise le résultat sur l'objet `request`.
_CACHE = '_mes_reactions_par_produit'


def cle_reacteur(request):
    """Identifie le visiteur qui réagit.

    Un client connecté est identifié par son compte (« u:<id> ») ; les autres
    le sont par leur session (« s:<clé> »). Cela leur permet de réagir sans
    créer de compte, comme pour le panier : aucun mur de connexion.
    """
    if request.user.is_authenticated:
        return f'u:{request.user.id}'
    if not request.session.session_key:
        request.session.create()
    return f's:{request.session.session_key}'


def mes_reactions_par_produit(request):
    """Dictionnaire `{produit_id: type de réaction}` du visiteur.

    Le résultat est mémorisé sur la requête. Une liste de 500 produits
    n'entraîne donc qu'UNE seule requête SQL, au lieu d'une par produit.
    """
    cache = getattr(request, _CACHE, None)
    if cache is None:
        cache = dict(
            Reaction.objects
            .filter(cle_reacteur=cle_reacteur(request))
            .values_list('produit_id', 'type_reaction')
        )
        setattr(request, _CACHE, cache)
    return cache


def mes_reactions_ids(request):
    """Identifiants des produits déjà réagis par le visiteur."""
    return set(mes_reactions_par_produit(request))


def oublier_cache_reactions(request):
    """Invalide le cache après une écriture, dans la même requête."""
    if hasattr(request, _CACHE):
        delattr(request, _CACHE)


def resume_reactions(produit, request):
    """Résumé JSON complet des réactions d'un produit, pour l'interface React.

    Renvoie le total, le détail par type de cœur et la réaction personnelle du
    visiteur (`None` s'il n'a pas encore réagi).
    """
    par_type = {cle: 0 for cle, _ in Reaction.TYPES}
    detail = (
        produit.reactions
        .values('type_reaction')
        .annotate(nombre=Count('id'))
        .order_by()
    )
    for ligne in detail:
        par_type[ligne['type_reaction']] = ligne['nombre']

    return {
        'total': sum(par_type.values()),
        'par_type': par_type,
        'ma_reaction': mes_reactions_par_produit(request).get(produit.id),
    }
