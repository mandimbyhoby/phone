import React, { useEffect, useRef, useState } from 'react';
import { fetchJson, formatPrix, messageErreur, postJson, toast } from '../api.js';
import CompteMenu from './CompteMenu.jsx';

// Page « Mon compte » : informations personnelles + photo + factures.
export default function Profil() {
  const [profil, setProfil] = useState(null);
  const [commandes, setCommandes] = useState([]);
  const [form, setForm] = useState({});
  const [erreurs, setErreurs] = useState({});
  const [chargement, setChargement] = useState(true);
  const [envoi, setEnvoi] = useState(false);
  const [apercu, setApercu] = useState(null);
  const fichierRef = useRef(null);

  useEffect(() => {
    let actif = true;
    Promise.all([
      fetchJson('/api/profil/'),
      fetchJson('/api/commandes/').catch(() => ({ commandes: [] })),
    ])
      .then(([profilData, commandesData]) => {
        if (!actif) return;
        const p = profilData.profil || {};
        setProfil(p);
        setForm({
          nom_complet: p.nom_complet || '',
          email: p.email || '',
          telephone: p.telephone || '',
          ville: p.ville || '',
          adresse: p.adresse || '',
        });
        setCommandes(commandesData.commandes || []);
        setChargement(false);
      })
      .catch(() => {
        if (!actif) return;
        toast('Impossible de charger votre profil.', 'error');
        setChargement(false);
      });
    return () => {
      actif = false;
    };
  }, []);

  function majChamp(nom, valeur) {
    setForm((actuel) => ({ ...actuel, [nom]: valeur }));
    setErreurs((actuel) => ({ ...actuel, [nom]: undefined }));
  }

  function onPhoto(e) {
    const fichier = e.target.files && e.target.files[0];
    if (!fichier) {
      setApercu(null);
      return;
    }
    setApercu(URL.createObjectURL(fichier));
  }

  async function enregistrer(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreurs({});

    const donnees = new FormData();
    Object.entries(form).forEach(([cle, valeur]) => {
      if (valeur != null) donnees.append(cle, valeur);
    });
    const fichier = fichierRef.current && fichierRef.current.files[0];
    if (fichier) donnees.append('photo', fichier);

    const res = await postJson('/api/profil/', donnees);
    setEnvoi(false);

    if (!res.ok) {
      if (res.data && res.data.erreurs) setErreurs(res.data.erreurs);
      toast(messageErreur(res.data, 'Impossible d’enregistrer vos informations.'), 'error');
      return;
    }

    setProfil(res.data.profil);
    setApercu(null);
    if (fichierRef.current) fichierRef.current.value = '';
    toast(res.data.detail || 'Informations mises à jour.', 'success');
  }

  async function supprimerPhoto() {
    if (!window.confirm('Supprimer votre photo de profil ?')) return;
    const donnees = new FormData();
    donnees.append('photo_clear', 'true');
    const res = await postJson('/api/profil/', donnees);
    if (res.ok) {
      setProfil(res.data.profil);
      setApercu(null);
      if (fichierRef.current) fichierRef.current.value = '';
      toast('Photo supprimée.', 'success');
    } else {
      toast(messageErreur(res.data, 'Impossible de supprimer la photo.'), 'error');
    }
  }

  if (chargement) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#94a3b8' }}>
        <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
      </p>
    );
  }

  const photoAffichee = apercu || (profil && profil.photo_url);
  const champErreur = (nom) =>
    erreurs[nom] && erreurs[nom].length ? (
      <small className="form-error">{erreurs[nom].join(' ')}</small>
    ) : null;
  const classeInput = (nom) => 'form-input' + (erreurs[nom] ? ' is-invalid' : '');

  return (
    <div className="account-layout">
      <CompteMenu
        active="profil"
        username={profil ? profil.username : ''}
        nomComplet={profil ? profil.nom_complet : ''}
        email={profil ? profil.email : ''}
        photoUrl={profil ? profil.photo_url : null}
      />

      <div className="account-content">
        <div className="account-card" id="infos">
          <h3><i className="fa-solid fa-address-card"></i> Mes informations personnelles</h3>
          <form onSubmit={enregistrer} encType="multipart/form-data">
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="id_nom_complet">Nom complet</label>
                <input
                  id="id_nom_complet"
                  className={classeInput('nom_complet')}
                  type="text"
                  value={form.nom_complet || ''}
                  onChange={(e) => majChamp('nom_complet', e.target.value)}
                />
                {champErreur('nom_complet')}
              </div>
              <div className="form-group">
                <label htmlFor="id_email">Email</label>
                <input
                  id="id_email"
                  className={classeInput('email')}
                  type="email"
                  value={form.email || ''}
                  onChange={(e) => majChamp('email', e.target.value)}
                  required
                />
                {champErreur('email')}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="id_telephone">Téléphone</label>
                <input
                  id="id_telephone"
                  className={classeInput('telephone')}
                  type="tel"
                  value={form.telephone || ''}
                  onChange={(e) => majChamp('telephone', e.target.value)}
                />
                {champErreur('telephone')}
              </div>
              <div className="form-group">
                <label htmlFor="id_ville">Ville</label>
                <input
                  id="id_ville"
                  className={classeInput('ville')}
                  type="text"
                  value={form.ville || ''}
                  onChange={(e) => majChamp('ville', e.target.value)}
                />
                {champErreur('ville')}
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="id_adresse">Adresse</label>
              <textarea
                id="id_adresse"
                className={classeInput('adresse')}
                rows={2}
                value={form.adresse || ''}
                onChange={(e) => majChamp('adresse', e.target.value)}
              ></textarea>
              {champErreur('adresse')}
            </div>

            <div className="form-group photo-group">
              <label>Photo de profil</label>
              <div className="photo-upload">
                <div className="photo-preview" id="photo-preview">
                  {photoAffichee ? (
                    <img src={photoAffichee} alt="Aperçu photo de profil" />
                  ) : (
                    <i className="fa-solid fa-user"></i>
                  )}
                </div>
                <div className="photo-upload-actions">
                  <input
                    ref={fichierRef}
                    id="photo-input"
                    className="form-input"
                    type="file"
                    accept="image/*"
                    onChange={onPhoto}
                  />
                  {champErreur('photo')}
                  {profil && profil.photo_url && !apercu && (
                    <label className="photo-remove-label">
                      <button
                        type="button"
                        className="photo-clear-btn"
                        onClick={supprimerPhoto}
                      >
                        <i className="fa-solid fa-trash"></i> Supprimer ma photo
                      </button>
                    </label>
                  )}
                  <small className="form-hint">JPG, PNG ou WebP — max 2 Mo</small>
                </div>
              </div>
            </div>

            <button type="submit" className="buy-btn submit-order" disabled={envoi}>
              <i className="fa-solid fa-floppy-disk"></i>{' '}
              {envoi ? 'Enregistrement…' : 'Enregistrer mes modifications'}
            </button>
          </form>
        </div>

        <div className="account-card" id="factures">
          <h3><i className="fa-solid fa-file-invoice"></i> Mes factures</h3>
          {commandes.filter((c) => c.statut !== 'annulee').length > 0 ? (
            <div className="orders-list">
              {commandes
                .filter((c) => c.statut !== 'annulee')
                .map((commande) => (
                  <div className="order-row" key={commande.id}>
                    <div className="order-row-head">
                      <div>
                        <strong>Commande #{commande.id}</strong>
                        <small className="order-date">
                          {new Date(commande.date).toLocaleDateString('fr-FR')}
                        </small>
                      </div>
                      <strong className="order-total">{formatPrix(commande.total)}</strong>
                    </div>
                    <a href={commande.facture_url} className="order-invoice-btn">
                      <i className="fa-solid fa-file-pdf"></i> Télécharger la facture PDF
                    </a>
                  </div>
                ))}
            </div>
          ) : (
            <p className="form-hint">
              Vos factures apparaîtront ici après un paiement confirmé.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
