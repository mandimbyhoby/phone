// ============================================================
// Store partagé du panier (sans dépendance externe)
// ------------------------------------------------------------
// Le tiroir du panier (navbar), la page panier et la fiche produit
// partagent le même état : toute mutation est diffusée aux abonnés.
// ============================================================
import { useCallback, useEffect, useState } from 'react';
import { messageErreur, postJson } from './api.js';

const ETAT_INITIAL = { items: [], total: 0, nombre: 0, pret: false, chargement: false };

let etat = { ...ETAT_INITIAL };
const abonnes = new Set();

function diffuser(nouvelEtat) {
  etat = { ...etat, ...nouvelEtat };
  abonnes.forEach((fn) => fn(etat));
}

export function souscrire(fn) {
  abonnes.add(fn);
  fn(etat);
  return () => abonnes.delete(fn);
}

function normaliser(data) {
  return {
    items: data.items || [],
    total: data.total || 0,
    nombre: data.nombre || 0,
  };
}

// Charge le panier depuis le serveur (une seule fois au démarrage).
let chargementEnCours = null;
export async function chargerPanier(force = false) {
  if (etat.pret && !force) return etat;
  if (chargementEnCours) return chargementEnCours;

  chargementEnCours = fetch('/api/panier/', { headers: { Accept: 'application/json' } })
    .then((res) => (res.ok ? res.json() : null))
    .then((data) => {
      if (data) diffuser({ ...normaliser(data), pret: true });
      return etat;
    })
    .catch(() => etat)
    .finally(() => {
      chargementEnCours = null;
    });

  return chargementEnCours;
}

async function mutation(url, corps) {
  diffuser({ chargement: true });
  try {
    const { ok, data } = await postJson(url, corps);
    if (ok && data && data.items) {
      diffuser({ ...normaliser(data), pret: true, chargement: false });
      return { ok: true, detail: data.detail };
    }
    diffuser({ chargement: false });
    return { ok: false, message: messageErreur(data, "Impossible d'ajouter au panier.") };
  } catch {
    diffuser({ chargement: false });
    return { ok: false, message: 'Connexion au serveur impossible.' };
  }
}

export function ajouterAuPanier(produitId, quantite = 1) {
  return mutation(`/api/panier/ajouter/${produitId}/`, { quantite: String(quantite) });
}

export function modifierQuantite(produitId, action, quantite) {
  const corps = { action };
  if (quantite != null) corps.quantite = String(quantite);
  return mutation(`/api/panier/modifier/${produitId}/`, corps);
}

export function supprimerDuPanier(produitId) {
  return mutation(`/api/panier/supprimer/${produitId}/`, {});
}

export function viderPanierLocal() {
  diffuser({ ...normaliser({ items: [], total: 0, nombre: 0 }), pret: true });
}

// Hook React : abonne le composant à l'état global du panier.
export function usePanier() {
  const [snapshot, setSnapshot] = useState(etat);

  useEffect(() => {
    chargerPanier();
    return souscrire(setSnapshot);
  }, []);

  const rafraichir = useCallback(() => chargerPanier(true), []);

  return { ...snapshot, rafraichir, ajouterAuPanier, modifierQuantite, supprimerDuPanier };
}
