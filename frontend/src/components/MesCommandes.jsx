import React, { useEffect, useState } from 'react';
import { fetchJson, formatPrix, messageErreur, postJson, toast } from '../api.js';
import CompteMenu from './CompteMenu.jsx';

function CarteCommande({ commande, onAnnuler, annulationEnCours }) {
  const date = new Date(commande.date).toLocaleString('fr-FR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="order-row">
      <div className="order-row-head">
        <div>
          <strong>Commande #{commande.id}</strong>
          <small className="order-date">{date}</small>
        </div>
        <div className="order-row-right">
          <span className={'order-status status-' + commande.statut}>
            {commande.statut_display}
          </span>
          <strong className="order-total">{formatPrix(commande.total)}</strong>
        </div>
      </div>

      <div className="order-row-items">
        {commande.lignes.map((ligne) => (
          <div className="order-row-item" key={ligne.produit_id}>
            <span>
              {ligne.quantite} × <a href={ligne.url}>{ligne.nom}</a>
            </span>
            <span>{formatPrix(ligne.sous_total)}</span>
          </div>
        ))}
      </div>

      {commande.paiement && (
        <div className="order-row-pay">
          <i className="fa-solid fa-wallet"></i> {commande.paiement.methode_display}
          {' — '}
          <span className={commande.paiement.statut === 'paye' ? 'pay-ok' : 'pay-wait'}>
            {commande.paiement.statut_display}
          </span>
        </div>
      )}

      {commande.statut !== 'annulee' && (
        <a href={commande.facture_url} className="order-invoice-btn">
          <i className="fa-solid fa-file-pdf"></i> Télécharger la facture
        </a>
      )}

      {commande.annulable && (
        <div className="order-cancel-form">
          <button
            type="button"
            className="order-cancel-btn"
            disabled={annulationEnCours}
            onClick={() => {
              if (window.confirm('Annuler cette commande ?')) {
                onAnnuler(commande.id);
              }
            }}
          >
            <i className="fa-solid fa-xmark"></i>{' '}
            {annulationEnCours ? 'Annulation…' : 'Annuler la commande'}
          </button>
        </div>
      )}
    </div>
  );
}

// Historique des commandes du client, avec annulation sans rechargement.
export default function MesCommandes() {
  const [commandes, setCommandes] = useState([]);
  const [profil, setProfil] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);
  const [annulationId, setAnnulationId] = useState(null);

  useEffect(() => {
    let actif = true;
    Promise.all([
      fetchJson('/api/commandes/').catch(() => ({ commandes: [] })),
      fetchJson('/api/profil/').catch(() => ({ profil: null })),
    ])
      .then(([commandesData, profilData]) => {
        if (!actif) return;
        setCommandes(commandesData.commandes || []);
        setProfil(profilData.profil || null);
        setChargement(false);
      })
      .catch(() => {
        if (!actif) return;
        setErreur('Impossible de charger vos commandes.');
        setChargement(false);
      });
    return () => {
      actif = false;
    };
  }, []);

  async function annuler(id) {
    setAnnulationId(id);
    const res = await postJson(`/api/commandes/${id}/annuler/`, {});
    setAnnulationId(null);

    if (!res.ok) {
      toast(messageErreur(res.data, "Impossible d'annuler cette commande."), 'error');
      return;
    }

    setCommandes((liste) =>
      liste.map((c) => (c.id === id ? res.data.commande : c))
    );
    toast(res.data.detail || 'Commande annulée.', 'success');
  }

  return (
    <div className="account-layout">
      <CompteMenu
        active="commandes"
        username={profil ? profil.username : ''}
        nomComplet={profil ? profil.nom_complet : ''}
        email={profil ? profil.email : ''}
        photoUrl={profil ? profil.photo_url : null}
      />

      <div className="account-content">
        <div className="account-card" id="orders">
          <h3><i className="fa-solid fa-receipt"></i> Historique des commandes</h3>

          {chargement && (
            <p style={{ textAlign: 'center', padding: '40px 0', color: '#94a3b8' }}>
              <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
            </p>
          )}

          {erreur && (
            <p style={{ textAlign: 'center', padding: '40px 0', color: '#ef4444' }}>{erreur}</p>
          )}

          {!chargement && !erreur && commandes.length === 0 && (
            <div className="empty-cart">
              <i className="fa-solid fa-box-open"></i>
              <h3>Aucune commande pour le moment</h3>
              <p>Votre historique de commandes apparaîtra ici.</p>
              <a href="/#products" className="btn-primary">Découvrir les produits</a>
            </div>
          )}

          {!chargement && commandes.length > 0 && (
            <div className="orders-list">
              {commandes.map((commande) => (
                <CarteCommande
                  key={commande.id}
                  commande={commande}
                  onAnnuler={annuler}
                  annulationEnCours={annulationId === commande.id}
                />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
