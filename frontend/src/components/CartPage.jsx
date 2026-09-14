import React from 'react';
import { formatPrix } from '../api.js';
import { usePanier } from '../panierStore.js';
import ListeArticles from './ListeArticles.jsx';

// Page « Mon panier » complète, pilotée par le store partagé.
export default function CartPage() {
  const { items, total, nombre, pret, chargement } = usePanier();

  if (!pret && (chargement || items.length === 0)) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#94a3b8' }}>
        <i className="fa-solid fa-spinner fa-spin"></i> Chargement de votre panier…
      </p>
    );
  }

  if (items.length === 0) {
    return (
      <div className="empty-cart">
        <i className="fa-solid fa-cart-arrow-down"></i>
        <h3>Votre panier est vide</h3>
        <p>Découvrez notre sélection de téléphones au meilleur prix.</p>
        <a href="/#products" className="btn-primary">Découvrir les produits</a>
      </div>
    );
  }

  return (
    <div className="cart-layout">
      <div className="cart-table" id="cart-page-items">
        <ListeArticles items={items} />
        <div className="drawer-total">
          <span>Total</span>
          <strong>{formatPrix(total)}</strong>
        </div>
      </div>

      <aside className="cart-summary">
        <span className="summary-kicker">RÉCAPITULATIF</span>
        <h3>Récapitulatif</h3>
        <div className="summary-line">
          <span>Articles</span>
          <strong>{nombre}</strong>
        </div>
        <div className="summary-line">
          <span>Sous-total</span>
          <strong>{formatPrix(total)}</strong>
        </div>
        <div className="summary-line">
          <span>Livraison</span>
          <strong>Gratuite</strong>
        </div>
        <div className="summary-line total-line">
          <span>Total</span>
          <strong>{formatPrix(total)}</strong>
        </div>
        <a href="/commande/" className="buy-btn checkout-btn">
          <span><i className="fa-solid fa-lock"></i> Passer la commande</span>
          <i className="fa-solid fa-arrow-right"></i>
        </a>
        <a href="/#products" className="continue-link">
          <i className="fa-solid fa-arrow-left"></i>
          <span>Continuer mes achats</span>
        </a>
        <div className="summary-note">
          <i className="fa-solid fa-shield-halved"></i>
          Paiement à la livraison — vous ne payez qu'à la réception.
        </div>
      </aside>
    </div>
  );
}
