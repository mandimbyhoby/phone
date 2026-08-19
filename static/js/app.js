// ============================================================
// Phone Store — Script global
// Frameworks : HTMX, Alpine.js, AOS
// ============================================================

document.addEventListener('DOMContentLoaded', function () {
    // ---- Menu mobile ----
    const toggle = document.getElementById('menu-toggle');
    const menu = document.getElementById('nav-menu');
    if (toggle && menu) {
        toggle.addEventListener('click', function () {
            menu.classList.toggle('open');
            const icon = toggle.querySelector('i');
            if (menu.classList.contains('open')) {
                icon.className = 'fa-solid fa-xmark';
            } else {
                icon.className = 'fa-solid fa-bars';
            }
        });
    }

    // ---- Mode clair / sombre ----
    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem('ps-theme', theme); } catch (e) { /* ignore */ }
        const isDark = theme === 'dark';
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            const icon = btn.querySelector('i');
            const label = btn.querySelector('.nav-label');
            if (icon) icon.className = isDark ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
            if (label) label.textContent = isDark ? 'Mode clair' : 'Mode sombre';
            btn.setAttribute('aria-label', isDark ? 'Activer le mode clair' : 'Activer le mode sombre');
        });
    }

    document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            const current = document.documentElement.getAttribute('data-theme') || 'dark';
            applyTheme(current === 'dark' ? 'light' : 'dark');
        });
    });

    // ---- Aperçu photo de profil ----
    const photoInput = document.getElementById('photo-input');
    const photoPreview = document.getElementById('photo-preview');
    if (photoInput && photoPreview) {
        photoInput.addEventListener('change', function () {
            const file = this.files && this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function (e) {
                    photoPreview.innerHTML = '<img src="' + e.target.result + '" alt="Aperçu photo de profil">';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // ---- Case "supprimer ma photo" : désactive le champ fichier ----
    const photoClear = document.getElementById('photo-clear');
    if (photoClear && photoInput) {
        photoClear.addEventListener('change', function () {
            if (this.checked) {
                photoInput.disabled = true;
                photoInput.value = '';
                photoPreview.innerHTML = '<i class="fa-solid fa-user"></i>';
            } else {
                photoInput.disabled = false;
            }
        });
    }

    // ---- Publicité vidéo : affiche la vidéo si disponible, sinon écran d'attente ----
    const adVideo = document.getElementById('ad-video');
    const adPlaceholder = document.getElementById('ad-video-placeholder');
    if (adVideo && adPlaceholder) {
        const afficherVideo = function () {
            if (adVideo.hidden) {
                adVideo.hidden = false;
                adPlaceholder.hidden = true;
            }
        };

        // La vidéo est disponible si le navigateur réussit à charger ses métadonnées
        adVideo.addEventListener('loadedmetadata', afficherVideo);

        // Sécurité : après 3,5 s, si rien n'est chargé → on garde l'écran d'attente
        setTimeout(function () {
            if (adVideo.readyState < 1) {
                adPlaceholder.hidden = false;
                adVideo.hidden = true;
            }
        }, 3500);
    }
});

// ============================================================
// HTMX — événements globaux
// ============================================================

// Toast "ajouté au panier" après un hx-post réussi
document.body.addEventListener('htmx:afterRequest', function (event) {
    const elt = event.detail.elt;
    if (event.detail.successful && elt && elt.hasAttribute('hx-post')) {
        showToast('Produit ajouté au panier !', 'success');
    }
});

// Rafraîchir AOS après un swap HTMX (grille produits filtrée)
document.body.addEventListener('htmx:afterSwap', function () {
    if (window.AOS) {
        AOS.refreshHard();
    }
});

// Synchroniser le tableau du panier (page /panier/) avec le tiroir après un swap OOB
document.body.addEventListener('htmx:oobAfterSwap', function () {
    const pageItems = document.getElementById('cart-page-items');
    const drawerItems = document.getElementById('cart-widget-items');
    if (pageItems && drawerItems && pageItems !== drawerItems) {
        pageItems.innerHTML = drawerItems.innerHTML;
        // Met à jour le récapitulatif de la page panier
        const totalEl = pageItems.querySelector('.drawer-total strong');
        if (totalEl) {
            const total = totalEl.innerText;
            const count = pageItems.querySelectorAll('.drawer-item').length;
            const summaryTotal = document.querySelector('.cart-summary .total-line strong');
            const summarySub = document.querySelector('.cart-summary .summary-line:nth-of-type(2) strong');
            const summaryCount = document.querySelector('.cart-summary .summary-line:nth-of-type(1) strong');
            if (summaryTotal) summaryTotal.innerText = total;
            if (summarySub) summarySub.innerText = total;
            if (summaryCount) summaryCount.innerText = String(count);
        }
    }
});

// Petit indicateur de chargement global
document.body.addEventListener('htmx:beforeRequest', function () {
    document.body.classList.add('htmx-busy');
});
document.body.addEventListener('htmx:afterRequest', function () {
    document.body.classList.remove('htmx-busy');
});

// ============================================================
// CSRF — nécessaire pour les requêtes POST HTMX vers Django
// ============================================================
function getCookie(name) {
    const value = '; ' + document.cookie;
    const parts = value.split('; ' + name + '=');
    if (parts.length === 2) return parts.pop().split(';').shift();
}

document.body.addEventListener('htmx:configRequest', function (event) {
    const csrf = getCookie('csrftoken');
    if (csrf) {
        event.detail.headers['X-CSRFToken'] = csrf;
    }
});

// ============================================================
// Toast helper
// ============================================================
function showToast(message, type) {
    const stack = document.querySelector('.toast-stack');
    if (!stack) {
        // Crée le conteneur s'il n'existe pas
        const container = document.createElement('div');
        container.className = 'toast-stack';
        document.body.appendChild(container);
        showToast(message, type);
        return;
    }
    const toast = document.createElement('div');
    toast.className = 'toast toast-' + (type || 'info');
    const icons = {
        success: 'fa-circle-check',
        error: 'fa-circle-exclamation',
        info: 'fa-circle-info',
    };
    toast.innerHTML = '<i class="fa-solid ' + (icons[type] || icons.info) + '"></i> ' + message;
    stack.appendChild(toast);
    setTimeout(function () {
        toast.classList.add('hide');
        setTimeout(function () { toast.remove(); }, 350);
    }, 3500);
}
