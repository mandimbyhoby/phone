from django.contrib import admin
import csv
from django.http import HttpResponse
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
        'stock_alerte',
        'disponible',
        'date_ajout',
        'image_preview'
    ]

    list_filter = ['disponible', 'categorie', 'marque']
    list_editable = ['prix', 'stock', 'disponible']
    search_fields = ['nom', 'marque']
    actions = ['exporter_csv']

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

    @admin.display(description='Alerte stock', ordering='stock')
    def stock_alerte(self, obj):
        if obj.stock == 0:
            return 'Rupture'
        if obj.stock <= 3:
            return 'Stock faible'
        return 'OK'

    @admin.action(description='Exporter les produits en CSV')
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="produits.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['Nom', 'Marque', 'Catégorie', 'Prix', 'Prix promo', 'Stock', 'Disponible'])
        for produit in queryset.select_related('categorie'):
            writer.writerow([
                produit.nom, produit.marque, produit.categorie.nom,
                produit.prix, produit.prix_promo or '', produit.stock,
                'Oui' if produit.disponible else 'Non',
            ])
        return response


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
    actions = ['exporter_csv']
    inlines = [LigneCommandeInline, PaiementInline]
    readonly_fields = ['total', 'date_commande']

    @admin.action(description='Exporter les commandes en CSV')
    def exporter_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="commandes.csv"'
        response.write('\ufeff')
        writer = csv.writer(response)
        writer.writerow(['N°', 'Client', 'Email', 'Téléphone', 'Ville', 'Total', 'Statut', 'Date'])
        for commande in queryset:
            writer.writerow([
                commande.id, commande.nom, commande.email, commande.telephone,
                commande.ville, commande.total, commande.get_statut_display(),
                commande.date_commande.strftime('%Y-%m-%d %H:%M'),
            ])
        return response


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