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
path = '/home/VOTRE-NOM/phone'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'phone_store.settings'
os.environ['DJANGO_DEBUG'] = 'False'
os.environ['DJANGO_ALLOWED_HOSTS'] = 'VOTRE-NOM.pythonanywhere.com'

# ⚠️ Remplacez par une clé secrète unique (générez-en une à https://djecrety.ir)
os.environ['DJANGO_SECRET_KEY'] = 'COLLEZ-VOTRE-CLE-ICI'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

Remplacez `VOTRE-NOM` par votre vrai nom d'utilisateur PythonAnywhere.

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

## 📍 Après le déploiement

1. **Mettre à jour le QR code** du site :
   ```bash
   python generer_qr.py https://VOTRE-NOM.pythonanywhere.com
   ```
   puis re-pusher sur GitHub (ou copier `static/images/qr-site.png` directement).

2. **Régénérer la bannière LinkedIn** avec la vraie URL si besoin.

3. **Paiements réels** : configurez les clés Stripe/PayPal/Orange Money
   (voir `README_PAIEMENTS.md`). Les webhooks devront pointer vers
   `https://VOTRE-NOM.pythonanywhere.com/webhook/stripe/` etc.

4. **Emails de réinitialisation** : remplacez `EMAIL_BACKEND` par un vrai
   SMTP dans les réglages (ex. Gmail App Password).

5. **Mettre le dépôt GitHub en privé** si vous ne voulez pas partager le code :
   GitHub → Settings → Danger Zone → Change visibility.
