from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nom


class Produit(models.Model):
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    marque = models.CharField(max_length=100)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_promo = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    disponible = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    image = models.ImageField(upload_to='produits/')
    image_2 = models.ImageField(upload_to='produits/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='produits/', null=True, blank=True)
    image_4 = models.ImageField(upload_to='produits/', null=True, blank=True)

    def __str__(self):
        return self.nom