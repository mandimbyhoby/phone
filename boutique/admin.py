from django.contrib import admin
from django.utils.html import mark_safe
from .models import Categorie, Produit, Avis, Commande, LigneCommande, MessageContact, Paiement, Profil


@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'nom_complet', 'telephone', 'ville', 'photo_preview', 'date_inscription']
    search_fields = ['utilisateur__username', 'utilisateur__email', 'nom_complet', 'telephone']

    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="44" height="44" style="border-radius:50%; object-fit:cover;" />')
        return "—"

    photo_preview.short_description = "Photo"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'slug']
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = [
        'nom',
        'marque',
        'prix',
        'stock',
        'disponible',
        'date_ajout',
        'image_preview'
    ]

    list_filter = ['disponible', 'categorie', 'marque']
    list_editable = ['prix', 'stock', 'disponible']
    search_fields = ['nom', 'marque']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'categorie', 'marque')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_3', 'image_4')
        }),
        ('Prix & Stock', {
            'fields': ('prix', 'prix_promo', 'stock', 'disponible')
        }),
        ('Description', {
            'fields': ('description',)
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(
                f'<img src="{obj.image.url}" width="60" style="border-radius:8px;" />'
            )
        return "Pas d'image"

    image_preview.short_description = "Image"


@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display = ['produit', 'nom', 'note', 'date']
    list_filter = ['note', 'produit']
    search_fields = ['nom', 'commentaire']


class LigneCommandeInline(admin.TabularInline):
    model = LigneCommande
    extra = 0
    readonly_fields = ['produit', 'quantite', 'prix_unitaire']


class PaiementInline(admin.StackedInline):
    model = Paiement
    extra = 0
    readonly_fields = ['methode', 'montant', 'reference', 'transaction_id', 'telephone', 'email_payeur', 'date_paiement']


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'nom', 'ville', 'total', 'statut', 'date_commande']
    list_filter = ['statut', 'ville']
    list_editable = ['statut']
    search_fields = ['nom', 'email', 'telephone', 'utilisateur__username']
    inlines = [LigneCommandeInline, PaiementInline]
    readonly_fields = ['total', 'date_commande']


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ['commande', 'methode', 'montant', 'statut', 'reference', 'date_creation']
    list_filter = ['methode', 'statut']
    search_fields = ['reference', 'transaction_id', 'telephone', 'commande__nom']
    readonly_fields = ['commande', 'methode', 'montant', 'reference', 'transaction_id', 'telephone', 'email_payeur', 'date_paiement', 'date_creation']


@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ['sujet', 'nom', 'email', 'date', 'traite']
    list_editable = ['traite']
    list_filter = ['traite']
    search_fields = ['sujet', 'nom', 'email', 'message']