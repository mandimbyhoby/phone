import React, { useEffect, useState } from 'react';
import { fetchJson, formatPrix, postForm, toast } from '../api.js';
import { ajouterAuPanier as ajouterAuPanierAPI } from '../panierStore.js';

function Etoiles({ note }) {
  const pleines = Math.round(note);
  return (
    <span>
      {'★'.repeat(pleines)}
      {'☆'.repeat(5 - pleines)}
    </span>
  );
}

function AvisForm({ produitId, onAjoute }) {
  const [nom, setNom] = useState('');
  const [note, setNote] = useState(5);
  const [commentaire, setCommentaire] = useState('');
  const [envoi, setEnvoi] = useState(false);
  const [erreur, setErreur] = useState(null);

  async function onSubmit(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreur(null);
    try {
      const res = await postForm('/api/avis/', {
        produit: String(produitId),
        nom: nom.trim(),
        note: String(note),
        commentaire: commentaire.trim(),
      });
      if (res.ok) {
        const data = await res.json();
        onAjoute(data);
        setNom('');
        setCommentaire('');
        setNote(5);
        toast('Merci pour votre avis !', 'success');
      } else {
        setErreur("Impossible de publier l'avis. Vérifiez les champs.");
      }
    } catch {
      setErreur("Impossible de publier l'avis. Réessayez.");
    } finally {
      setEnvoi(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <div className="form-group">
        <label>Votre nom</label>
        <input
          type="text"
          className="form-input"
          value={nom}
          onChange={(e) => setNom(e.target.value)}
          placeholder="Votre nom"
          required
        />
      </div>
      <div className="form-group">
        <label>Votre note</label>
        <div className="review-stars review-stars-input">
          {[1, 2, 3, 4, 5].map((n) => (
            <button
              type="button"
              key={n}
              className={'star-btn' + (n <= note ? ' active' : '')}
              onClick={() => setNote(n)}
              aria-label={n + ' étoile(s)'}
            >
              {n <= note ? '★' : '☆'}
            </button>
          ))}
        </div>
      </div>
      <div className="form-group">
        <label>Votre commentaire</label>
        <textarea
          className="form-input"
          rows={3}
          value={commentaire}
          onChange={(e) => setCommentaire(e.target.value)}
          placeholder="Partagez votre expérience…"
          required
        />
      </div>
      {erreur && <small className="form-error">{erreur}</small>}
      <button type="submit" className="buy-btn" disabled={envoi}>
        {envoi ? 'Publication…' : 'Publier mon avis'}
      </button>
    </form>
  );
}

export default function ProductDetail() {
  const el = document.getElementById('react-detail');
  const produitId = el ? el.dataset.productId : null;

  const [produit, setProduit] = useState(null);
  const [avis, setAvis] = useState([]);
  const [imageActive, setImageActive] = useState(0);
  const [qte, setQte] = useState(1);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    if (!produitId) return;
    fetchJson('/api/produits/' + produitId + '/')
      .then((data) => {
        setProduit(data);
        setAvis(data.avis || []);
        setChargement(false);
      })
      .catch(() => {
        setErreur('Impossible de charger le produit.');
        setChargement(false);
      });
  }, [produitId]);

  if (chargement) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#94a3b8' }}>
        <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
      </p>
    );
  }

  if (erreur || !produit) {
    return <p style={{ textAlign: 'center', padding: '48px 0', color: '#ef4444' }}>{erreur}</p>;
  }

  const images = [
    produit.image_url,
    produit.image_2_url,
    produit.image_3_url,
    produit.image_4_url,
  ].filter(Boolean);
  const imagePrincipale = images[imageActive] || '/static/images/iphone.jpg';
  const enPromo = produit.prix_promo != null;

  async function ajouterAuPanier() {
    const res = await ajouterAuPanierAPI(produit.id, qte);
    if (res.ok) {
      toast('Produit ajouté au panier !', 'success');
    } else {
      toast(res.message || "Erreur lors de l'ajout au panier.", 'error');
    }
  }

  return (
    <section className="detail-page">
      <div className="detail-circle-1"></div>
      <div className="detail-circle-2"></div>
      <div className="detail-dots"></div>
      <div className="detail-circle"></div>
      <div className="detail-lines"></div>

      <div className="detail-box">
        <div className="detail-circle-bg"></div>

        <div className="detail-container">
          <div className="detail-gallery">
            <div className="detail-main-image">
              <img src={imagePrincipale} alt={produit.nom} />
            </div>
            {images.length > 1 && (
              <div className="detail-thumbs">
                {images.map((src, i) => (
                  <div
                    key={i}
                    className={'thumb' + (i === imageActive ? ' active' : '')}
                    onClick={() => setImageActive(i)}
                  >
                    <img src={src} alt={produit.nom} />
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="detail-info">
            <span className="detail-badge">
              {(produit.categorie ? produit.categorie.nom : '').toUpperCase()} · {produit.marque}
            </span>
            <h1 className="detail-title">{produit.nom}</h1>

            <div className="detail-rating">
              <span><Etoiles note={produit.note_moyenne} /></span>
              <small>
                {produit.note_moyenne > 0
                  ? produit.note_moyenne + '/5 — ' + avis.length + ' avis'
                  : 'Très apprécié'}
              </small>
            </div>

            <div className="detail-price-box">
              {enPromo ? (
                <>
                  <span className="detail-old-price">{formatPrix(produit.prix)}</span>
                  <span className="detail-price">{formatPrix(produit.prix_promo)}</span>
                  <span className="detail-save">Économisez {formatPrix(produit.economie)}</span>
                </>
              ) : (
                <span className="detail-price">{formatPrix(produit.prix)}</span>
              )}
            </div>

            <div className="detail-stock">
              {produit.stock > 0 ? (
                <span className="in-stock">✔ En stock ({produit.stock} disponibles)</span>
              ) : (
                <span className="out-stock">
                  <i className="fa-solid fa-circle-exclamation"></i> Rupture de stock
                </span>
              )}
            </div>

            <div className="detail-description-box">
              <h3>Description</h3>
              <p>{produit.description}</p>
            </div>

            <div className="detail-features">
              <div className="feature-item">
                <strong><i className="fa-solid fa-shield-halved"></i> Garantie</strong>
                <span>12 mois</span>
              </div>
              <div className="feature-item">
                <strong><i className="fa-solid fa-truck-fast"></i> Livraison</strong>
                <span>24-72h partout à Madagascar</span>
              </div>
              <div className="feature-item">
                <strong><i className="fa-solid fa-hand-holding-dollar"></i> Paiement</strong>
                <span>À la livraison</span>
              </div>
            </div>

            {produit.stock > 0 && (
              <div className="detail-actions">
                <div className="qty-selector">
                  <button type="button" onClick={() => setQte(qte > 1 ? qte - 1 : 1)}>−</button>
                  <input
                    type="number"
                    min="1"
                    max={produit.stock}
                    value={qte}
                    onChange={(e) =>
                      setQte(Math.max(1, Math.min(produit.stock, Number(e.target.value) || 1)))
                    }
                  />
                  <button
                    type="button"
                    onClick={() => setQte(qte < produit.stock ? qte + 1 : produit.stock)}
                  >
                    +
                  </button>
                </div>
                <button className="buy-btn" onClick={ajouterAuPanier}>
                  <i className="fa-solid fa-cart-plus"></i> Ajouter au panier
                </button>
                <a href="/" className="back-btn">
                  <i className="fa-solid fa-arrow-left"></i> Retour
                </a>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="container reviews-section">
        <div className="reviews-grid">
          <div className="reviews-list">
            <h2><i className="fa-solid fa-comments"></i> Avis clients ({avis.length})</h2>
            {avis.map((a) => (
              <div className="review-card" key={a.id}>
                <div className="review-head">
                  <div className="author-avatar">{(a.nom || '?')[0].toUpperCase()}</div>
                  <div>
                    <strong>{a.nom}</strong>
                    <div className="review-stars"><Etoiles note={a.note} /></div>
                  </div>
                  <small>{new Date(a.date).toLocaleDateString('fr-FR')}</small>
                </div>
                <p>{a.commentaire}</p>
              </div>
            ))}
            {avis.length === 0 && (
              <p className="no-reviews">
                Aucun avis pour le moment. Soyez le premier à donner votre avis !
              </p>
            )}
          </div>

          <div className="reviews-form">
            <h2><i className="fa-solid fa-pen"></i> Donner mon avis</h2>
            <AvisForm produitId={produit.id} onAjoute={(nouvelAvis) => setAvis([nouvelAvis, ...avis])} />
          </div>
        </div>
      </div>
    </section>
  );
}
