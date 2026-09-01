from django.db import models
from django.db.models import Avg
from django.conf import settings


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

    @property
    def prix_actuel(self):
        return self.prix_promo if self.prix_promo else self.prix

    @property
    def reduction_pourcentage(self):
        if self.prix_promo:
            return round((1 - self.prix_promo / self.prix) * 100)
        return 0

    @property
    def economie(self):
        if self.prix_promo:
            return self.prix - self.prix_promo
        return 0

    @property
    def note_moyenne(self):
        moyenne = self.avis.aggregate(moyenne=Avg('note'))['moyenne']
        return round(moyenne, 1) if moyenne is not None else 0


class Avis(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='avis')
    nom = models.CharField(max_length=100)
    note = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    commentaire = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.nom} — {self.produit.nom} ({self.note}★)"


class Profil(models.Model):
    """Données clients supplémentaires, reliées au compte utilisateur."""
    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profil',
    )
    nom_complet = models.CharField(max_length=150, blank=True, default='')
    telephone = models.CharField(max_length=20, blank=True, default='')
    adresse = models.TextField(blank=True, default='')
    ville = models.CharField(max_length=100, blank=True, default='')
    photo = models.ImageField(upload_to='profils/', null=True, blank=True)
    est_pilote_principal = models.BooleanField(default=False, help_text='Accès réservé au dashboard administrateur principal.')
    date_inscription = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"


class Commande(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmee', 'Confirmée'),
        ('expediee', 'Expédiée'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='commandes',
    )
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    telephone = models.CharField(max_length=20)
    adresse = models.TextField()
    ville = models.CharField(max_length=100)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_commande = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande #{self.id} — {self.nom}"

    def get_total(self):
        return sum(ligne.sous_total for ligne in self.lignes.all())


class LigneCommande(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def sous_total(self):
        return self.prix_unitaire * self.quantite

    def __str__(self):
        return f"{self.quantite} × {self.produit.nom}"


class Paiement(models.Model):
    METHODE_CHOICES = [
        ('carte', 'Carte bancaire (Visa, Mastercard)'),
        ('paypal', 'PayPal'),
        ('orange_money', 'Orange Money'),
        ('especes', 'Paiement à la livraison'),
    ]
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('echoue', 'Échoué'),
        ('rembourse', 'Remboursé'),
    ]

    commande = models.OneToOneField(Commande, on_delete=models.CASCADE, related_name='paiement')
    methode = models.CharField(max_length=20, choices=METHODE_CHOICES)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    transaction_id = models.CharField(max_length=200, blank=True, default='')
    telephone = models.CharField(max_length=20, blank=True, default='')
    email_payeur = models.EmailField(blank=True, default='')
    date_paiement = models.DateTimeField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_methode_display()} — {self.commande} ({self.get_statut_display()})"


class MessageContact(models.Model):
    nom = models.CharField(max_length=100)
    email = models.EmailField()
    sujet = models.CharField(max_length=200)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    traite = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.sujet} — {self.nom}"