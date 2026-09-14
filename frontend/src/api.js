// ============================================================
// Helpers partagés (API, CSRF, formatage)
// ============================================================

export function getCookie(name) {
  const value = '; ' + document.cookie;
  const parts = value.split('; ' + name + '=');
  if (parts.length === 2) return parts.pop().split(';').shift();
  return '';
}

// Formate un prix en Ariary (ex. 1250000 -> « 1 250 000 Ar »)
export function formatPrix(value) {
  const n = Number(value);
  if (Number.isNaN(n)) return String(value) + ' Ar';
  return n.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' Ar';
}

export function toast(message, type = 'info') {
  if (typeof window !== 'undefined' && typeof window.showToast === 'function') {
    window.showToast(message, type);
  }
}

export async function fetchJson(url, options = {}) {
  const res = await fetch(url, {
    headers: { Accept: 'application/json' },
    ...options,
  });
  if (!res.ok) throw new Error('HTTP ' + res.status);
  return res.json();
}

// Requête POST « formulaire » vers Django, avec jeton CSRF.
export async function postForm(url, data) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
      Accept: 'application/json',
    },
    body: data instanceof URLSearchParams ? data : new URLSearchParams(data),
  });
  return res;
}

// Requête POST JSON (ou multipart) vers l'API, avec jeton CSRF.
// Retourne { ok, status, data } — `data` contient le JSON de réponse ou null.
export async function postJson(url, data) {
  const estFormData = typeof FormData !== 'undefined' && data instanceof FormData;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest',
      Accept: 'application/json',
      ...(estFormData ? {} : { 'Content-Type': 'application/json' }),
    },
    body: estFormData ? data : JSON.stringify(data || {}),
  });

  let payload = null;
  try {
    payload = await res.json();
  } catch {
    payload = null;
  }
  return { ok: res.ok, status: res.status, data: payload };
}

// Aplatit une erreur DRF ({ champ: [messages] } ou { detail }) en texte lisible.
export function messageErreur(data, defaut = 'Une erreur est survenue.') {
  if (!data) return defaut;
  if (typeof data === 'string') return data;
  if (data.detail) return data.detail;
  if (data.erreurs) return messageErreur(data.erreurs, defaut);
  if (Array.isArray(data)) return data.join(' ');
  const premiere = Object.values(data)[0];
  if (Array.isArray(premiere)) return premiere.join(' ');
  if (typeof premiere === 'string') return premiere;
  return defaut;
}
