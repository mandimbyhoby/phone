from django.contrib import admin
from django.utils.html import mark_safe
from .models import Categorie, Produit


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