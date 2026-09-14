import React, { useEffect, useRef, useState } from 'react';
import { createPortal } from 'react-dom';
import { formatPrix } from '../api.js';
import { usePanier } from '../panierStore.js';
import ListeArticles from './ListeArticles.jsx';

const ICON_PANIER = '/static/images/icons/panier.svg';

// Tiroir panier de la navbar. Remplace l'ancien rendu HTMX + Alpine :
// l'état vient du store partagé, donc le badge se met à jour partout.
export default function CartDrawer() {
  const { items, total, nombre, pret, chargement } = usePanier();
  const [ouvert, setOuvert] = useState(false);

  useEffect(() => {
    function onKey(e) {
      if (e.key === 'Escape') setOuvert(false);
    }
    document.addEventListener('keydown', onKey);
    return () => document.removeEventListener('keydown', onKey);
  }, []);

  useEffect(() => {
    document.body.style.overflow = ouvert ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [ouvert]);

  const fermer = () => setOuvert(false);

  // Fermeture par glissement vers la droite (mobile) : on compare la position
  // du doigt au début et à la fin du toucher.
  const toucheX = useRef(null);
  function onTouchStart(e) {
    toucheX.current = e.touches[0].clientX;
  }
  function onTouchEnd(e) {
    if (toucheX.current === null) return;
    const delta = e.changedTouches[0].clientX - toucheX.current;
    if (delta > 60) fermer();
    toucheX.current = null;
  }

  // Le bouton reste dans la barre de navigation.
  const boutonPanier = (
    <div className="cart-wrap">
      <button
        type="button"
        className="cart-btn"
        onClick={() => setOuvert(true)}
        aria-label="Ouvrir le panier"
        aria-expanded={ouvert}
      >
        <img src={ICON_PANIER} alt="" width="24" height="24" className="cart-icon" />
        <span className="cart-badge" id="cart-badge">{nombre}</span>
        <span className="cart-btn-label">Mon panier</span>
      </button>
    </div>
  );

  // Le voile et le tiroir sont rendus hors de la barre de navigation.
  const voileEtTiroir = (
    <>
      <div
        className={'drawer-overlay react-drawer' + (ouvert ? ' is-open' : '')}
        onClick={fermer}
        aria-hidden="true"
      ></div>

      <aside
        className={'cart-drawer react-cart-drawer' + (ouvert ? ' is-open' : '')}
        role="dialog"
        aria-label="Mon panier"
        aria-hidden={!ouvert}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <header className="drawer-header">
          <h3 className="drawer-title">
            <img
              src={ICON_PANIER}
              alt=""
              width="24"
              height="24"
              className="drawer-cart-icon"
            />
            Mon panier
          </h3>

          {nombre > 0 && (
            <span className="drawer-count">
              {nombre} article{nombre > 1 ? 's' : ''}
            </span>
          )}

          <button className="drawer-close" onClick={fermer} aria-label="Fermer le panier">
            <i className="fa-solid fa-xmark"></i>
          </button>
        </header>

        <div className="drawer-body">
          <div className="drawer-grabber" aria-hidden="true"></div>
          {!pret && chargement ? (
            <p style={{ textAlign: 'center', padding: '30px 0', color: '#94a3b8' }}>
              <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
            </p>
          ) : items.length === 0 ? (
            <div className="drawer-empty">
              <i className="fa-solid fa-cart-arrow-down"></i>
              <p>Votre panier est vide.</p>
              <a href="/" className="btn-primary" onClick={fermer}>
                Découvrir nos produits
              </a>
            </div>
          ) : (
            <>
              <ListeArticles items={items} onNaviguer={fermer} />
              <div className="drawer-total">
                <span>Total</span>
                <strong>{formatPrix(total)}</strong>
              </div>
            </>
          )}
        </div>

        {items.length > 0 && (
          <div className="drawer-cta">
            <a href="/panier/" className="btn-primary" onClick={fermer}>
              <span>Voir le panier</span>
              <i className="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
            <a href="/commande/" className="btn-checkout" onClick={fermer}>
              <span>Commander</span>
              <i className="fa-solid fa-arrow-right"></i>
            </a>
          </div>
        )}
      </aside>
    </>
  );

  // Le tiroir est monté dans <body> via un portail : la barre de navigation
  // porte un `backdrop-filter`, or cette propriété crée un containing block
  // pour les descendants `position: fixed`. Sans ce portail, le tiroir se
  // positionne par rapport à la barre (décalé de ~34 px vers le bas) et
  // déborde sous le bord inférieur de l'écran.
  return (
    <>
      {boutonPanier}
      {createPortal(voileEtTiroir, document.body)}
    </>
  );
}
