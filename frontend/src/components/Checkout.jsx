import React, { useEffect, useState } from 'react';
import { fetchJson, formatPrix, messageErreur, postJson, toast } from '../api.js';
import { viderPanierLocal } from '../panierStore.js';

function IconePaiement({ value }) {
  // Les logos image sont optionnels : si le fichier manque, on retombe
  // sur l'icône Font Awesome (comme le faisait le template Django).
  const [imageOk, setImageOk] = useState(true);

  if (value === 'carte') {
    return imageOk ? (
      <img
        src="/static/images/stripe-logo.png"
        alt="Stripe"
        className="payment-brand-img"
        onError={() => setImageOk(false)}
      />
    ) : (
      <i className="fa-solid fa-credit-card payment-fallback" style={{ display: 'inline-flex' }}></i>
    );
  }
  if (value === 'paypal') {
    return imageOk ? (
      <img
        src="/static/images/paypal-logo.png"
        alt="PayPal"
        className="payment-brand-img"
        onError={() => setImageOk(false)}
      />
    ) : (
      <i className="fa-brands fa-paypal payment-fallback" style={{ display: 'inline-flex' }}></i>
    );
  }
  if (value === 'orange_money') {
    return <i className="fa-solid fa-mobile-screen-button"></i>;
  }
  return <i className="fa-solid fa-hand-holding-dollar"></i>;
}

function SousTitrePaiement({ value }) {
  if (value === 'carte') return <small>Visa · Mastercard · Amex</small>;
  if (value === 'orange_money') return <small>Paiement mobile Mvola/OM</small>;
  if (value === 'paypal') return <small>Compte PayPal</small>;
  return <small>Payez à la réception</small>;
}

// Page de finalisation de commande (checkout) rendue par React.
export default function Checkout() {
  const [panier, setPanier] = useState(null);
  const [methodes, setMethodes] = useState([]);
  const [modeDemo, setModeDemo] = useState(false);
  const [form, setForm] = useState({ methode_paiement: 'especes' });
  const [erreurs, setErreurs] = useState({});
  const [chargement, setChargement] = useState(true);
  const [erreurGlobale, setErreurGlobale] = useState(null);
  const [envoi, setEnvoi] = useState(false);

  useEffect(() => {
    fetchJson('/api/commande/')
      .then((data) => {
        setPanier(data.panier);
        setMethodes(data.methodes || []);
        setModeDemo(Boolean(data.mode_demo));
        setForm((actuel) => ({
          ...actuel,
          ...(data.initial || {}),
          methode_paiement: data.methode_paiement || 'especes',
        }));
        setChargement(false);
      })
      .catch(() => {
        setErreurGlobale('Impossible de charger votre commande. Réessayez.');
        setChargement(false);
      });
  }, []);

  function majChamp(nom, valeur) {
    setForm((actuel) => ({ ...actuel, [nom]: valeur }));
    setErreurs((actuel) => ({ ...actuel, [nom]: undefined }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreurs({});
    setErreurGlobale(null);

    const res = await postJson('/api/commande/', form);
    if (res.ok && res.data && res.data.redirect) {
      viderPanierLocal();
      toast(res.data.detail || 'Commande enregistrée !', 'success');
      window.location.href = res.data.redirect;
      return;
    }

    if (res.data && res.data.erreurs) {
      setErreurs(res.data.erreurs);
      setErreurGlobale('Veuillez corriger les champs signalés.');
    } else {
      setErreurGlobale(messageErreur(res.data, 'Impossible de finaliser la commande.'));
    }
    setEnvoi(false);
  }

  if (chargement) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#94a3b8' }}>
        <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
      </p>
    );
  }

  if (erreurGlobale && !panier) {
    return <p style={{ textAlign: 'center', padding: '48px 0', color: '#ef4444' }}>{erreurGlobale}</p>;
  }

  const items = (panier && panier.items) || [];
  const total = (panier && panier.total) || 0;

  if (items.length === 0) {
    return (
      <div className="empty-cart">
        <i className="fa-solid fa-cart-arrow-down"></i>
        <h3>Votre panier est vide</h3>
        <p>Ajoutez des produits avant de passer commande.</p>
        <a href="/#products" className="btn-primary">Découvrir les produits</a>
      </div>
    );
  }

  const champErreur = (nom) =>
    erreurs[nom] && erreurs[nom].length ? (
      <small className="form-error">{erreurs[nom].join(' ')}</small>
    ) : null;

  const classeInput = (nom) => 'form-input' + (erreurs[nom] ? ' is-invalid' : '');

  return (
    <div className="checkout-layout">
      <div className="checkout-form">
        <h3><i className="fa-solid fa-user"></i> Informations de livraison</h3>
        <form method="post" id="checkout-form" onSubmit={onSubmit}>
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="id_nom">Nom complet</label>
              <input
                id="id_nom"
                className={classeInput('nom')}
                type="text"
                placeholder="Nom complet"
                value={form.nom || ''}
                onChange={(e) => majChamp('nom', e.target.value)}
                required
              />
              {champErreur('nom')}
            </div>
            <div className="form-group">
              <label htmlFor="id_telephone">Téléphone</label>
              <input
                id="id_telephone"
                className={classeInput('telephone')}
                type="tel"
                placeholder="+261 34 00 000 00"
                value={form.telephone || ''}
                onChange={(e) => majChamp('telephone', e.target.value)}
                required
              />
              {champErreur('telephone')}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="id_email">Email</label>
            <input
              id="id_email"
              className={classeInput('email')}
              type="email"
              placeholder="email@exemple.com"
              value={form.email || ''}
              onChange={(e) => majChamp('email', e.target.value)}
              required
            />
            {champErreur('email')}
          </div>

          <div className="form-group">
            <label htmlFor="id_adresse">Adresse</label>
            <textarea
              id="id_adresse"
              className={classeInput('adresse')}
              rows={2}
              placeholder="Adresse de livraison"
              value={form.adresse || ''}
              onChange={(e) => majChamp('adresse', e.target.value)}
              required
            ></textarea>
            {champErreur('adresse')}
          </div>

          <div className="form-group">
            <label htmlFor="id_ville">Ville</label>
            <input
              id="id_ville"
              className={classeInput('ville')}
              type="text"
              placeholder="Ville"
              value={form.ville || ''}
              onChange={(e) => majChamp('ville', e.target.value)}
              required
            />
            {champErreur('ville')}
          </div>

          <div className="payment-methods">
            <h3><i className="fa-solid fa-wallet"></i> Méthode de paiement</h3>
            <div className="payment-grid">
              {methodes.map((m) => (
                <label
                  key={m.value}
                  className={
                    'payment-option' + (form.methode_paiement === m.value ? ' selected' : '')
                  }
                  data-payment-method={m.value}
                >
                  <input
                    type="radio"
                    name="methode_paiement"
                    value={m.value}
                    checked={form.methode_paiement === m.value}
                    onChange={() => majChamp('methode_paiement', m.value)}
                  />
                  <span className="payment-logo">
                    <IconePaiement value={m.value} />
                  </span>
                  <span className="payment-text">
                    <strong>{m.label}</strong>
                    <SousTitrePaiement value={m.value} />
                  </span>
                </label>
              ))}
            </div>
            {champErreur('methode_paiement')}
            {modeDemo && (
              <div className="demo-note">
                <i className="fa-solid fa-hand-holding-dollar"></i>
                <span>Le paiement en ligne est en attente de configuration.</span>
              </div>
            )}
          </div>

          {erreurGlobale && (
            <div className="form-error form-error-box">{erreurGlobale}</div>
          )}

          <button type="submit" className="buy-btn submit-order" disabled={envoi}>
            <i className="fa-solid fa-circle-check"></i>{' '}
            {envoi ? 'Enregistrement…' : `Confirmer ma commande — ${formatPrix(total)}`}
          </button>
        </form>
      </div>

      <aside className="checkout-summary">
        <h3>Ma commande ({items.length})</h3>
        <div className="order-items">
          {items.map((item) => (
            <div className="order-item" key={item.produit_id}>
              <div className="order-item-img">
                {item.image_url ? <img src={item.image_url} alt={item.nom} /> : null}
                <span className="order-qty">{item.quantite}</span>
              </div>
              <div className="order-item-info">
                <strong>{item.nom}</strong>
                <small>{item.quantite} × {formatPrix(item.prix)}</small>
              </div>
              <strong>{formatPrix(item.sous_total)}</strong>
            </div>
          ))}
        </div>
        <div className="summary-line total-line">
          <span>Total à payer</span>
          <strong>{formatPrix(total)}</strong>
        </div>
        <div className="summary-secure">
          {modeDemo ? (
            <>
              <i className="fa-solid fa-hand-holding-dollar"></i> Paiement à la réception
              <span>Vous ne payez pas en ligne</span>
            </>
          ) : (
            <>
              <i className="fa-solid fa-shield-halved"></i> Paiement sécurisé
              <span>Choisissez votre moyen de paiement</span>
            </>
          )}
        </div>
      </aside>
    </div>
  );
}
