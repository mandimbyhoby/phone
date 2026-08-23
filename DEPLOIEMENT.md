# 🚀 Déploiement gratuit — PythonAnywhere

Guide étape par étape pour mettre le site **Phone Store** en ligne gratuitement
sur **PythonAnywhere** (parfait pour Django + SQLite + fichiers médias, sans
carte bancaire).

> ⏱️ Durée : 20-30 minutes

---

## Étape 1 — Créer le compte

1. Rendez-vous sur **https://www.pythonanywhere.com/plans/** et cliquez sur
   **« Create a Beginner account »** (gratuit)
2. Remplissez le formulaire (email + mot de passe) et confirmez
3. Une fois connecté, notez votre **nom d'utilisateur** (ex. `mandimby`)

> ⚠️ Votre site sera accessible à : `https://VOTRE-NOM.pythonanywhere.com`

---

## Étape 2 — Cloner le projet depuis GitHub

Dans le **Dashboard** de PythonAnywhere, ouvrez l'onglet **Consoles** →
**Bash**, puis tapez :

```bash
git clone https://github.com/mandimbyhoby/phone.git
cd phone
```

Vérifiez que tout est là :

```bash
ls          # doit contenir manage.py, boutique/, phone_store/, templates/...
```

---

## Étape 3 — Créer l'environnement virtuel

Toujours dans la console Bash :

```bash
mkvirtualenv --python=python3.12 phone-env
pip install -r requirements.txt
```

---

## Étape 4 — Migrer et créer l'admin

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser   # nom + email + mot de passe
```

---

## Étape 5 — Configurer le site web

1. Retournez au **Dashboard** → onglet **Web**
2. Cliquez **« Add a new web app »** → **Next** → choisissez **Manual
   configuration** → **Python 3.12** → Next
3. Dans la section **Code** :
   - **Source code** : `/home/VOTRE-NOM/phone`
   - **Working directory** : `/home/VOTRE-NOM/phone`
4. Dans **Virtualenv** : cliquez sur l'icône 🚫 puis entrez :
   `/home/VOTRE-NOM/.virtualenvs/phone-env`

---

## Étape 6 — Le fichier WSGI

Cliquez sur **WSGI configuration file**, supprimez tout le contenu et collez :

```python
import os
import sys

# Ajoute le dossier du projet au chemin Python
path = '/home/hoby2108/phone'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'phone_store.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'phoneboutique.mg,www.phoneboutique.mg'

# URL officielle du site → c'est CETTE URL qui sera encodée dans le QR code
os.environ['DJANGO_SITE_URL'] = 'https://phoneboutique.mg'

# Numéro WhatsApp au format international, sans + ni espaces (optionnel)
os.environ['WHATSAPP_NUMBER'] = '261340000000'

# ⚠️ Remplacez par une clé secrète unique (générez-en une à https://djecrety.ir)
os.environ['DJANGO_SECRET_KEY'] = 'COLLEZ-VOTRE-CLE-ICI'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

> 📝 Si votre nom d'utilisateur PythonAnywhere change, remplacez `hoby2108` par
> votre nouveau nom (dans `path`, `DJANGO_ALLOWED_HOSTS` et `DJANGO_SITE_URL`).

---

## Étape 7 — Fichiers statiques

Dans la même page **Web**, section **Static files** :

| URL | Répertoire |
|---|---|
| `/static/` | `/home/VOTRE-NOM/phone/staticfiles/` |
| `/media/` | `/home/VOTRE-NOM/phone/media/` |

> 🎯 **Important** : PythonAnywhere sert `/media/` directement depuis votre
> dossier — vos images produits, photos de profil et la vidéo fonctionneront.

---

## Étape 8 — Redémarrer et tester

1. Cliquez sur le bouton vert **Reload** (en haut de la page Web)
2. Ouvrez `https://VOTRE-NOM.pythonanywhere.com` — le site est en ligne ! 🎉

---

## ⚠️ Problèmes courants

| Problème | Solution |
|---|---|
| `DisallowedHost` | Vérifiez `DJANGO_ALLOWED_HOSTS` dans le WSGI (votre domaine complet) |
| Erreur 500 | Regardez l'onglet **Web → Error log** de PythonAnywhere |
| Statiques cassées | Relancez `python manage.py collectstatic --noinput` |
| Base vide | Copiez votre `db.sqlite3` local vers `/home/VOTRE-NOM/phone/` |
| Médias manquants | Copiez votre dossier `media/` local vers `/home/VOTRE-NOM/phone/` |

---

## 🎯 QR code de la page Contact (scannable en ligne)

Le QR code n'est **plus une image statique** : il est généré automatiquement par
l'URL `/qr-code/` avec le **vrai domaine** du site. Rien à régénérer après
un déploiement. ✅

Pour qu'il fonctionne sur PythonAnywhere, vérifiez ces **4 points** :

1. **Dépendances installées** (le QR est créé avec `qrcode` + `Pillow`) :
   ```bash
   pip install -r requirements.txt
   ```

2. **URL officielle du site** : dans le fichier **WSGI configuration file**
   (onglet Web), ajoutez la ligne suivante avec **votre domaine exact** :
   ```python
   os.environ['DJANGO_SITE_URL'] = 'https://phoneboutique.mg'
   ```
   → C'est cette URL **exacte** qui sera encodée dans le QR code.
   (Sans cette ligne, le QR détecte automatiquement le domaine de la requête —
   ça marche aussi, mais c'est moins sûr.)

3. **Domaine autorisé** : dans le même fichier WSGI, `DJANGO_ALLOWED_HOSTS`
   doit contenir votre domaine exact :
   ```python
   os.environ['DJANGO_ALLOWED_HOSTS'] = 'phoneboutique.mg,www.phoneboutique.mg'
   ```
   Sinon : erreur `DisallowedHost` (HTTP 400) sur `/qr-code/` et tout le site.

4. **Forcer HTTPS** : sur l'onglet **Web** de PythonAnywhere, dans la section
   **Security**, activez **Force HTTPS** ✅. Ainsi le QR code encode bien
   `https://phoneboutique.mg/` (et non `http://`).
   (Django détecte le HTTPS via l'en-tête `X-Forwarded-Proto` — déjà configuré
   dans `settings.py`.)

5. **Recharger** : cliquez sur le bouton vert **Reload** en haut de l'onglet Web.

> 💡 Test rapide après déploiement : ouvrez
> `https://phoneboutique.mg/qr-code/` — vous devez voir le QR code
> noir & violet. Scannez-le avec votre téléphone : il doit ouvrir
> `https://phoneboutique.mg/`.

---

## 📍 Après le déploiement

1. ~~Mettre à jour le QR code~~ → **plus nécessaire** : le QR de la page Contact
   est généré dynamiquement avec le bon domaine (voir section ci-dessus).

2. **Régénérer la bannière LinkedIn** avec la vraie URL si besoin.

3. **Paiements réels** : configurez les clés Stripe/PayPal/Orange Money
   (voir `README_PAIEMENTS.md`). Les webhooks devront pointer vers
   `https://VOTRE-NOM.pythonanywhere.com/webhook/stripe/` etc.

4. **Emails (messages de contact + réinitialisation de mot de passe)** :
   les messages envoyés via le formulaire de contact sont reçus sur
   **rakotoarijaona04@yahoo.com** (configurable avec `CONTACT_EMAIL`).
   Pour un envoi réel, définissez les variables SMTP dans le fichier
   **WSGI configuration file** (voir la section « Emails » ci-dessous).

5. **Mettre le dépôt GitHub en privé** si vous ne voulez pas partager le code :
   GitHub → Settings → Danger Zone → Change visibility.

---

## 📧 Emails (messages de contact → votre boîte mail)

Le formulaire de contact enregistre les messages en base **et** les envoie par
email à `CONTACT_EMAIL` (par défaut `rakotoarijaona04@yahoo.com`).

### Option A — Relais SMTP de PythonAnywhere (le plus simple) ✅

PythonAnywhere fournit un relais SMTP gratuit pour les sites hébergés chez eux.

Dans le **WSGI configuration file** (onglet Web), ajoutez :

```python
os.environ['EMAIL_HOST'] = 'smtp.pythonanywhere.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_HOST_USER'] = 'hoby2108'   # VOTRE nom d'utilisateur PythonAnywhere
os.environ['EMAIL_HOST_PASSWORD'] = ''       # pas de mot de passe pour le relais
os.environ['EMAIL_USE_TLS'] = 'True'
os.environ['DEFAULT_FROM_EMAIL'] = 'Phone Store <hoby2108@pythonanywhere.com>'
```

> ⚠️ Avec ce relais, l'expéditeur (`From`) doit être `VOTRE-NOM@pythonanywhere.com`.
> Les emails partiront du domaine PythonAnywhere — vérifiez dans vos spams au début.

### Option B — Yahoo SMTP (votre adresse de réception)

Le destinataire étant une adresse Yahoo, vous pouvez envoyer depuis un compte
Yahoo (nécessite un **mot de passe d'application**) :

1. Allez sur https://login.yahoo.com/myaccount/security → **Generate app password**
2. Dans le WSGI, ajoutez :

```python
os.environ['EMAIL_HOST'] = 'smtp.mail.yahoo.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_HOST_USER'] = 'rakotoarijaona04@yahoo.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'VOTRE-MOT-DE-PASSE-APPLICATION'
os.environ['EMAIL_USE_TLS'] = 'True'
os.environ['DEFAULT_FROM_EMAIL'] = 'Phone Store <rakotoarijaona04@yahoo.com>'
```

### Option C — Gmail SMTP (recommandée si vous avez un compte Gmail)

1. Activez la **vérification en deux étapes** sur
   https://myaccount.google.com/security
2. Créez un **mot de passe d'application** : même page → *Mots de passe des
   applications* → **Autre (nom personnalisé)** → nommez-le « Phone Store »
3. Dans le WSGI, ajoutez :

```python
os.environ['EMAIL_HOST'] = 'smtp.gmail.com'
os.environ['EMAIL_PORT'] = '587'
os.environ['EMAIL_HOST_USER'] = 'VOTRE-ADRESSE@gmail.com'
os.environ['EMAIL_HOST_PASSWORD'] = 'VOTRE-MOT-DE-PASSE-16-CARACTERES'
os.environ['EMAIL_USE_TLS'] = 'True'
os.environ['DEFAULT_FROM_EMAIL'] = 'Phone Store <VOTRE-ADRESSE@gmail.com>'
```

> 💡 Le **From** sera votre Gmail, et les messages arrivent toujours sur
> `CONTACT_EMAIL` (rakotoarijaona04@yahoo.com).

### Vérification

1. Cliquez sur **Reload** dans l'onglet Web
2. Sur le site, page **Contact** → envoyez un message test
3. Vérifiez votre boîte mail (et les **spams** la première fois)
4. Le message est aussi visible dans l'**admin Django** → *Messages de contact*

> 💡 Sans configuration SMTP, les emails sont affichés dans la console du
> serveur (mode développement) — le site ne plante pas.
