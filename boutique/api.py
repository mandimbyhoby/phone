from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Avis, Categorie, Produit, Reaction
from .reactions import (
    cle_reacteur,
    mes_reactions_par_produit,
    oublier_cache_reactions,
    resume_reactions,
)


class ProduitPagination(PageNumberPagination):
    """Pagination de l'API. `page_size` est paramétrable pour permettre au
    catalogue React de récupérer tout le catalogue en une seule requête."""
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 500


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ('id', 'nom', 'slug')


class AvisSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avis
        fields = ('id', 'produit', 'nom', 'note', 'commentaire', 'date')
        read_only_fields = ('id', 'date')


class ProduitSerializer(serializers.ModelSerializer):
    categorie = CategorieSerializer(read_only=True)
    prix_actuel = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    reduction_pourcentage = serializers.IntegerField(read_only=True)
    note_moyenne = serializers.FloatField(read_only=True)
    economie = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image_url = serializers.SerializerMethodField()
    image_2_url = serializers.SerializerMethodField()
    image_3_url = serializers.SerializerMethodField()
    image_4_url = serializers.SerializerMethodField()
    nombre_reactions = serializers.SerializerMethodField()
    ma_reaction = serializers.SerializerMethodField()

    class Meta:
        model = Produit
        fields = (
            'id', 'nom', 'marque', 'description', 'categorie', 'prix',
            'prix_promo', 'prix_actuel', 'reduction_pourcentage', 'economie',
            'stock', 'disponible', 'note_moyenne', 'image_url', 'image_2_url',
            'image_3_url', 'image_4_url', 'nombre_reactions', 'ma_reaction',
            'date_ajout',
        )

    def get_nombre_reactions(self, obj):
        # `nb_reactions` provient de l'annotation de la vue : une seule requête
        # pour tout le catalogue. Hors de ce contexte, on retombe sur un
        # comptage direct pour que le sérialiseur reste utilisable partout.
        nb = getattr(obj, 'nb_reactions', None)
        return nb if nb is not None else obj.reactions.count()

    def get_ma_reaction(self, obj):
        """Cœur déjà choisi par le visiteur, ou None (carte non remplie)."""
        request = self.context.get('request')
        if request is None:
            return None
        return mes_reactions_par_produit(request).get(obj.id)

    def _absolutise(self, image_field):
        if not image_field:
            return None
        url = image_field.url
        request = self.context.get('request')
        return request.build_absolute_uri(url) if request else url

    def get_image_url(self, obj):
        return self._absolutise(obj.image)

    def get_image_2_url(self, obj):
        return self._absolutise(obj.image_2)

    def get_image_3_url(self, obj):
        return self._absolutise(obj.image_3)

    def get_image_4_url(self, obj):
        return self._absolutise(obj.image_4)


class ProduitDetailSerializer(ProduitSerializer):
    """Sérialiseur enrichi pour la fiche produit : avis et détail des réactions."""
    avis = AvisSerializer(many=True, read_only=True)
    reactions_resume = serializers.SerializerMethodField()

    class Meta(ProduitSerializer.Meta):
        fields = ProduitSerializer.Meta.fields + ('avis', 'reactions_resume')

    def get_reactions_resume(self, obj):
        request = self.context.get('request')
        if request is None:
            return {'total': 0, 'par_type': {}, 'ma_reaction': None}
        return resume_reactions(obj, request)


class CategorieViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Categorie.objects.all().order_by('nom')
    serializer_class = CategorieSerializer
    pagination_class = ProduitPagination


class ProduitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Produit.objects.select_related('categorie').filter(disponible=True)
    serializer_class = ProduitSerializer
    pagination_class = ProduitPagination

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProduitDetailSerializer
        return ProduitSerializer

    def get_queryset(self):
        # L'annotation évite une requête de comptage par produit dans le
        # catalogue (500 produits = 1 requête au lieu de 501).
        queryset = super().get_queryset().annotate(nb_reactions=Count('reactions'))
        categorie = self.request.query_params.get('categorie')
        recherche = self.request.query_params.get('q')

        if categorie:
            queryset = queryset.filter(categorie__slug=categorie)
        if recherche:
            queryset = queryset.filter(
                Q(nom__icontains=recherche)
                | Q(marque__icontains=recherche)
                | Q(description__icontains=recherche)
            )
        return queryset.order_by('-date_ajout')


class AvisViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Liste et création d'avis clients (soumission sans rechargement de page)."""
    queryset = Avis.objects.select_related('produit').all().order_by('-date')
    serializer_class = AvisSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        produit = self.request.query_params.get('produit')
        if produit:
            queryset = queryset.filter(produit_id=produit)
        return queryset


class ReactionProduitAPIView(APIView):
    """Enregistre (ou retire) la réaction « cœur » du visiteur sur un produit.

    Un re-clic sur le MÊME cœur retire la réaction ; cliquer sur un AUTRE cœur
    remplace simplement le type choisi. La réponse renvoie toujours le résumé à
    jour, afin que l'interface React n'ait rien à recalculer elle-même.

    Aucune connexion n'est exigée : un visiteur non connecté réagit via sa
    session, ce qui lève toute barrière à l'engagement.
    """
    permission_classes = [AllowAny]

    def post(self, request, produit_id):
        produit = get_object_or_404(Produit, pk=produit_id)
        type_demande = str(request.data.get('type') or 'aime').lower()

        if type_demande not in dict(Reaction.TYPES):
            return Response(
                {'detail': "Cette réaction n'existe pas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        cle = cle_reacteur(request)
        existante = produit.reactions.filter(cle_reacteur=cle).first()

        if existante and existante.type_reaction == type_demande:
            existante.delete()
        else:
            Reaction.objects.update_or_create(
                produit=produit,
                cle_reacteur=cle,
                defaults={
                    'type_reaction': type_demande,
                    'utilisateur': request.user if request.user.is_authenticated else None,
                },
            )

        # Le résumé doit refléter l'écriture qui vient d'avoir lieu.
        oublier_cache_reactions(request)
        return Response(resume_reactions(produit, request))