import React from 'react';
import { formatPrix, toast } from '../api.js';
import { modifierQuantite, supprimerDuPanier } from '../panierStore.js';

// Liste d'articles du panier, partagée entre le tiroir de la navbar
// et la page « Mon panier ». Reprend le markup .drawer-* du thème.
export default function ListeArticles({ items, onNaviguer }) {
  async function changer(item, action) {
    const res = await modifierQuantite(item.produit_id, action);
    if (!res.ok) toast(res.message, 'error');
  }

  async function definirQuantite(item, valeur) {
    const cible = Math.max(1, Math.min(item.stock || 1, Number(valeur) || 1));
    if (cible === item.quantite) return;
    const res = await modifierQuantite(item.produit_id, 'set', cible);
    if (!res.ok) toast(res.message, 'error');
  }

  async function retirer(item) {
    const res = await supprimerDuPanier(item.produit_id);
    if (res.ok) {
      toast('Article retiré du panier.', 'info');
    } else {
      toast(res.message, 'error');
    }
  }

  return (
    <div className="drawer-list">
      {items.map((item) => (
        <div className="drawer-item" key={item.produit_id}>
          <a
            href={item.url}
            className="drawer-item-img"
            onClick={onNaviguer}
            aria-label={item.nom}
          >
            {item.image_url ? <img src={item.image_url} alt={item.nom} /> : null}
          </a>

          <div className="drawer-item-info">
            <a href={item.url} onClick={onNaviguer}>{item.nom}</a>
            <small>{formatPrix(item.prix)} l'unité</small>
          </div>

          <div className="drawer-item-actions">
            <button
              type="button"
              className="qty-btn"
              aria-label={'Diminuer la quantité de ' + item.nom}
              onClick={() => changer(item, 'diminuer')}
              disabled={item.quantite <= 1}
            >
              −
            </button>
            <input
              className="qty-num"
              type="number"
              min="1"
              max={item.stock || 1}
              value={item.quantite}
              aria-label={'Quantité de ' + item.nom}
              onChange={(e) => definirQuantite(item, e.target.value)}
            />
            <button
              type="button"
              className="qty-btn"
              aria-label={'Augmenter la quantité de ' + item.nom}
              onClick={() => changer(item, 'augmenter')}
              disabled={item.stock > 0 && item.quantite >= item.stock}
            >
              +
            </button>
          </div>

          <strong className="drawer-item-price">{formatPrix(item.sous_total)}</strong>

          <button
            type="button"
            className="drawer-remove"
            title="Retirer du panier"
            aria-label={'Retirer ' + item.nom + ' du panier'}
            onClick={() => retirer(item)}
          >
            <i className="fa-solid fa-trash"></i>
          </button>
        </div>
      ))}
    </div>
  );
}
