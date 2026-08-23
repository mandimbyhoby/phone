# 📱 Phone Store — E-commerce Django

Boutique en ligne de téléphones à Madagascar, développée avec **Django 6**, **HTMX**, **Alpine.js** et **AOS**.

![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![HTMX](https://img.shields.io/badge/HTMX-1.9-3366CC)
![Alpine.js](https://img.shields.io/badge/Alpine.js-3.14-8BC0D0)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)

---

## ✨ Fonctionnalités

### 🛒 E-commerce
- Catalogue de téléphones avec images multiples
- **Recherche instantanée** (HTMX), filtres par catégorie, tri par prix/promo/nom
- **Panier** en session avec tiroir latéral animé (Alpine.js)
- **Frais de livraison** et paiement à la livraison

### 💳 Paiements en ligne
| Méthode | Passerelle | Devise |
|---|---|---|
| 💳 Carte bancaire (Visa, Mastercard, Amex) | **Stripe Checkout** | EUR (converti) |
| 🅿️ PayPal | **PayPal REST v2** | EUR (converti) |
| 📱 Orange Money | **API marchand Orange** | MGA |
| 💵 Paiement à la livraison | — | Ar |

> 💵 **Paiement à la livraison activé par défaut** ; les paiements en ligne sont prêts à être activés après configuration des comptes marchands. Voir [`README_PAIEMENTS.md`](README_PAIEMENTS.md).

### 👤 Comptes clients
- Inscription / connexion **obligatoire avant achat**
- Profil avec **photo de profil** (upload + aperçu)
- **Menu compte style Amazon** (« Bonjour, [nom] / Comptes et listes »)
- Historique des commandes, changement de mot de passe
- **Réinitialisation de mot de passe** par email

### 🎨 Expérience
- Fond animé (dégradé en mouvement, particules, lignes lumineuses) sur toutes les pages
- **Publicité vidéo** sur l'accueil (fichier local `media/videos/phone-ad.mp4` ou écran d'attente)
- **QR code** scannable sur la page contact
- Avis clients avec notes ★, produits similaires, promotions
- Animations au scroll (AOS), toasts de notification

### 🛠️ Administration
- Dashboard produits avec aperçu image
- Gestion des commandes (statuts) et **paiements** (méthode/statut)
- Gestion des avis, messages de contact, profils clients

---

## 🚀 Installation

```bash
# 1. Cloner le dépôt
git clone https://github.com/mandimbyhoby/phone.git
cd phone_store

# 2. Créer l'environnement virtuel
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate    # Linux/Mac

# 3. Installer les dépendances
pip install django pillow stripe requests qrcode

# 4. Migrer la base de données
python manage.py migrate

# 5. Créer le superutilisateur (admin)
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

🌐 Rendez-vous sur **http://127.0.0.1:8000/** — l'admin sur **/admin/**

---

## 🔑 Configuration des paiements (optionnel)

Toutes les clés se configurent via variables d'environnement ou dans `phone_store/settings.py` :

```python
# Stripe
STRIPE_PUBLIC_KEY = 'pk_test_...'
STRIPE_SECRET_KEY = 'sk_test_...'

# PayPal
PAYPAL_CLIENT_ID = '...'
PAYPAL_CLIENT_SECRET = '...'
PAYPAL_ENV = 'sandbox'  # ou 'live'

# Orange Money
ORANGE_MONEY_CLIENT_ID = '...'
ORANGE_MONEY_CLIENT_SECRET = '...'
ORANGE_MONEY_MERCHANT_NUMBER = '...'
```

📖 Guide détaillé : [`README_PAIEMENTS.md`](README_PAIEMENTS.md)

---

## 🏗️ Structure du projet

```
phone_store/
├── boutique/              # Application principale
│   ├── models.py          # Produit, Categorie, Avis, Commande, Paiement, Profil...
│   ├── views.py           # Vues (catalogue, panier, commandes, auth, webhooks)
│   ├── paiements.py       # Passerelles : Stripe, PayPal, Orange Money
│   ├── forms.py           # Formulaires (auth, avis, commande, contact)
│   ├── context_processors.py  # Panier global
│   └── panier.py          # Logique du panier (session)
├── phone_store/           # Configuration Django
├── templates/             # Templates (boutique/, registration/)
├── static/                # CSS, JS, images
├── media/                 # Uploads (produits, vidéos, profils)
└── db.sqlite3             # Base de données (non versionnée)
```

---

## 🛠️ Technologies

| Outil | Rôle |
|---|---|
| **Django 6** | Backend, ORM, admin, auth |
| **HTMX** | Interactions AJAX sans rechargement (filtres, panier) |
| **Alpine.js** | Tiroir panier, menus, interactions front |
| **AOS** | Animations au scroll |
| **Stripe / PayPal SDK** | Paiements en ligne |
| **Pillow** | Traitement d'images |
| **qrcode** | Génération du QR code du site |

---

## 📄 Licence

Projet personnel — tous droits réservés.
