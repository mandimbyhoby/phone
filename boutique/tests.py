from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from .forms import CommandeForm
from .models import Avis, Categorie, Produit


class ProduitTests(TestCase):
	def setUp(self):
		self.categorie = Categorie.objects.create(nom='Téléphones', slug='telephones')
		self.produit = Produit.objects.create(
			categorie=self.categorie,
			nom='Phone Test',
			marque='Test',
			description='Produit de test',
			prix='100000.00',
			stock=2,
			image='produits/test.jpg',
		)

	def test_note_moyenne_sans_avis(self):
		self.assertEqual(self.produit.note_moyenne, 0)

	def test_note_moyenne_arrondie(self):
		Avis.objects.create(produit=self.produit, nom='A', note=5, commentaire='Très bien')
		Avis.objects.create(produit=self.produit, nom='B', note=4, commentaire='Bien')
		self.assertEqual(self.produit.note_moyenne, 4.5)


@override_settings(STORAGES={
	'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
	'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class CommandeStockTests(TestCase):
	def test_paiement_livraison_seul_par_defaut(self):
		self.assertEqual(
			list(CommandeForm().fields['methode_paiement'].choices),
			[('especes', 'Paiement à la livraison')],
		)

	def test_commande_refusee_si_stock_insuffisant(self):
		user = User.objects.create_user(username='client', password='motdepasse-test')
		categorie = Categorie.objects.create(nom='Accessoires', slug='accessoires')
		produit = Produit.objects.create(
			categorie=categorie,
			nom='Chargeur',
			marque='Test',
			description='Chargeur de test',
			prix='50000.00',
			stock=1,
			image='produits/chargeur.jpg',
		)
		self.client.force_login(user)
		session = self.client.session
		session['cart'] = {str(produit.pk): {'quantite': 2}}
		session.save()

		response = self.client.post('/commande/', {
			'nom': 'Client Test',
			'email': 'client@example.com',
			'telephone': '+261340000000',
			'adresse': 'Adresse test',
			'ville': 'Antananarivo',
			'methode_paiement': 'especes',
		})

		self.assertEqual(response.status_code, 200)
		self.assertEqual(produit.__class__.objects.get(pk=produit.pk).stock, 1)

# Create your tests here.
