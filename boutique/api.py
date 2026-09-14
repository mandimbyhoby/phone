from django.db.models import Q
from rest_framework import serializers, viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny

from .models import Avis, Categorie, Produit


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

    class Meta:
        model = Produit
        fields = (
            'id', 'nom', 'marque', 'description', 'categorie', 'prix',
            'prix_promo', 'prix_actuel', 'reduction_pourcentage', 'economie',
            'stock', 'disponible', 'note_moyenne', 'image_url', 'image_2_url',
            'image_3_url', 'image_4_url', 'date_ajout',
        )

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
    """Sérialiseur enrichi pour la fiche produit : inclut les avis clients."""
    avis = AvisSerializer(many=True, read_only=True)

    class Meta(ProduitSerializer.Meta):
        fields = ProduitSerializer.Meta.fields + ('avis',)


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
        queryset = super().get_queryset()
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