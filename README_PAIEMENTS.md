# 💳 Système de paiement — Guide de configuration

> **Configuration actuelle :** le paiement à la livraison est toujours disponible.
> PayPal apparaît après configuration de ses identifiants et activation de
> `PAIEMENTS_EN_LIGNE=True`.

Le site gère **4 méthodes de paiement** :

| Méthode | Passerelle | Statut |
|---|---|---|
| 💳 Carte bancaire (Visa, Mastercard, Amex, Apple Pay, Google Pay) | **Stripe** | selon configuration |
| 🅿️ PayPal | **PayPal Checkout** | selon configuration |
| 📱 Orange Money | **API marchand Orange** | selon configuration |
| 💵 Paiement à la livraison | — | ✅ intégré |

## 🧪 Mode actuel

Les commandes sont confirmées avec paiement à la livraison. Aucun paiement en
ligne n'est simulé, afin de ne pas présenter une fausse confirmation au client.

Pour activer les options en ligne après configuration des comptes marchands,
définissez `PAIEMENTS_EN_LIGNE=True` dans l'environnement du serveur. Chaque
moyen n'est affiché que lorsque ses propres identifiants sont renseignés.

## 🔑 Activer les vrais paiements

Remplissez les clés via des **variables d'environnement** (recommandé) ou
directement dans `phone_store/settings.py` (section « PAIEMENTS »).

### 1. Stripe (cartes)

1. Créez un compte sur [stripe.com](https://stripe.com)
2. Récupérez les clés dans le dashboard : **Développeurs → Clés API**
   (clés de test `pk_test_...` / `sk_test_...` disponibles immédiatement)
3. Configurez :
   ```
   STRIPE_PUBLIC_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```
4. (Optionnel) Webhook : créez un endpoint dans Stripe → `/webhook/stripe/`
   et récupérez `STRIPE_WEBHOOK_SECRET` (signature vérifiée).
   ⚠️ En développement local, l'outil `stripe listen` fait le relais.

### 2. PayPal

1. Créez un compte sur [developer.paypal.com](https://developer.paypal.com)
2. Dans **Apps & Credentials**, créez une app sandbox pour obtenir
   `Client ID` et `Secret`
3. Configurez :
   ```
   PAYPAL_CLIENT_ID=...
   PAYPAL_CLIENT_SECRET=...
   PAYPAL_ENV=sandbox          # 'live' quand tout est prêt
   ```

### 3. Orange Money (API marchand)

1. Faites une demande d'accès API marchand auprès d'Orange (programme
   « Orange Money API » pour les développeurs)
2. Récupérez `client_id`, `client_secret` et votre `merchant_number`
3. Configurez :
   ```
   ORANGE_MONEY_CLIENT_ID=...
   ORANGE_MONEY_CLIENT_SECRET=...
   ORANGE_MONEY_MERCHANT_NUMBER=...
   ORANGE_MONEY_BASE_URL=https://api.orange.com
   ```
4. Le webhook `/webhook/orange-money/` reçoit les notifications de statut.

## 💱 Devise

L'Ariary (MGA) n'est **pas accepté** par Stripe/PayPal. Les paiements carte et
PayPal sont donc facturés en **EUR**, convertis depuis l'Ariary avec le taux :
```
PAIEMENT_TAUX_EUR=5000      # 1 EUR = 5000 Ar (ajustez selon le cours)
```
Le montant en Ariary reste la référence affichée sur le site ; la conversion
n'apparaît que sur le reçu Stripe/PayPal.

Orange Money facture directement en **MGA** (Ariary), sans conversion.

## 🧪 Tester Stripe en mode test

- Carte de test : `4242 4242 4242 4242` (valide, date future, CVC quelconque)
- Carte refusée : `4000 0000 0000 0002`

## 📁 Structure

- `boutique/paiements.py` — logique des passerelles (Stripe, PayPal, OM, démo)
- `boutique/views.py` — vues checkout, retours, webhooks
- `boutique/models.py` — modèle `Paiement`
- `/admin/` — gestion des paiements (filtres méthode/statut, recherche)
