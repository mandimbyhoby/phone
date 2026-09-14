import React, { useEffect, useMemo, useState } from 'react';
import { fetchJson, formatPrix, toast } from '../api.js';
import { ajouterAuPanier as ajouterAuPanierAPI } from '../panierStore.js';

function Etoiles({ note }) {
  const pleines = Math.round(note);
  return (
    <span className="product-rating" title={'Note : ' + note}>
      {'★'.repeat(pleines)}
      {'☆'.repeat(5 - pleines)}
      <small>({note})</small>
    </span>
  );
}

function CarteProduit({ produit, onAjouter }) {
  const enStock = produit.stock > 0;
  const enPromo = produit.prix_promo != null;
  const image = produit.image_url || '/static/images/iphone.jpg';
  const url = '/produit/' + produit.id + '/';

  return (
    <div className="product-card">
      {enPromo && <span className="promo-badge">-{produit.reduction_pourcentage}%</span>}

      <a href={url} className="product-image">
        <img src={image} alt={produit.nom} loading="lazy" />
      </a>

      <div className="product-info">
        <span className="product-cat">{produit.categorie ? produit.categorie.nom : ''}</span>
        <h3><a href={url}>{produit.nom}</a></h3>
        <p className="brand">{produit.marque}</p>

        {produit.note_moyenne > 0 ? (
          <Etoiles note={produit.note_moyenne} />
        ) : (
          <div className="product-rating"><small>Nouveau produit</small></div>
        )}

        {enPromo ? (
          <p className="price-box">
            <span className="old-price">{formatPrix(produit.prix)}</span>
            <span className="price">{formatPrix(produit.prix_promo)}</span>
          </p>
        ) : (
          <p className="price">{formatPrix(produit.prix)}</p>
        )}

        <p className="stock">
          {enStock ? (
            <span className="in-stock">✔ En stock ({produit.stock})</span>
          ) : (
            <span className="out-stock">
              <i className="fa-solid fa-circle-exclamation"></i> Rupture de stock
            </span>
          )}
        </p>

        <div className="product-actions">
          <a href={url} className="product-btn">Voir détails</a>
          {enStock && (
            <button
              className="add-cart-btn"
              title="Ajouter au panier"
              onClick={() => onAjouter(produit)}
            >
              <i className="fa-solid fa-cart-plus"></i>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export default function Catalog() {
  const [produits, setProduits] = useState([]);
  const [categories, setCategories] = useState([]);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);
  const [recherche, setRecherche] = useState('');
  const [categorie, setCategorie] = useState('');
  const [tri, setTri] = useState('nouveaute');

  useEffect(() => {
    Promise.all([
      fetchJson('/api/categories/?page_size=100'),
      fetchJson('/api/produits/?page_size=500'),
    ])
      .then(([cats, prods]) => {
        setCategories(cats.results || cats || []);
        setProduits(prods.results || prods || []);
        setChargement(false);
      })
      .catch(() => {
        setErreur('Impossible de charger le catalogue. Réessayez dans un instant.');
        setChargement(false);
      });
  }, []);

  const produitsFiltres = useMemo(() => {
    let resultats = produits;

    if (recherche.trim()) {
      const q = recherche.trim().toLowerCase();
      resultats = resultats.filter((p) =>
        ((p.nom || '') + ' ' + (p.marque || '') + ' ' + (p.description || ''))
          .toLowerCase()
          .includes(q)
      );
    }

    if (categorie) {
      resultats = resultats.filter((p) => p.categorie && p.categorie.slug === categorie);
    }

    if (tri === 'promo') {
      resultats = resultats.filter((p) => p.prix_promo != null);
    }

    const tries = [...resultats];
    switch (tri) {
      case 'prix_asc':
        tries.sort((a, b) => Number(a.prix_actuel) - Number(b.prix_actuel));
        break;
      case 'prix_desc':
        tries.sort((a, b) => Number(b.prix_actuel) - Number(a.prix_actuel));
        break;
      case 'nom':
        tries.sort((a, b) => (a.nom || '').localeCompare(b.nom || ''));
        break;
      default:
        tries.sort((a, b) => new Date(b.date_ajout) - new Date(a.date_ajout));
        break;
    }

    return tries;
  }, [produits, recherche, categorie, tri]);

  async function ajouterAuPanier(produit) {
    const res = await ajouterAuPanierAPI(produit.id, 1);
    if (res.ok) {
      toast('Produit ajouté au panier !', 'success');
    } else {
      toast(res.message || "Erreur lors de l'ajout au panier.", 'error');
    }
  }

  if (chargement) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#94a3b8' }}>
        <i className="fa-solid fa-spinner fa-spin"></i> Chargement du catalogue…
      </p>
    );
  }

  if (erreur) {
    return (
      <p style={{ textAlign: 'center', padding: '48px 0', color: '#ef4444' }}>{erreur}</p>
    );
  }

  return (
    <>
      <div className="filters-bar">
        <div className="filter-search">
          <i className="fa-solid fa-magnifying-glass"></i>
          <input
            type="text"
            placeholder="Rechercher un téléphone..."
            value={recherche}
            onChange={(e) => setRecherche(e.target.value)}
            aria-label="Rechercher un téléphone"
          />
        </div>

        <div className="filter-pills">
          <button
            type="button"
            className={'filter-pill' + (categorie === '' ? ' active' : '')}
            onClick={() => setCategorie('')}
          >
            Tous
          </button>
          {categories.map((c) => (
            <button
              key={c.id}
              type="button"
              className={'filter-pill' + (categorie === c.slug ? ' active' : '')}
              onClick={() => setCategorie(c.slug)}
            >
              {c.nom}
            </button>
          ))}
        </div>

        <select
          className="filter-sort"
          aria-label="Trier les produits"
          value={tri}
          onChange={(e) => setTri(e.target.value)}
        >
          <option value="nouveaute">Nouveautés</option>
          <option value="prix_asc">Prix croissant</option>
          <option value="prix_desc">Prix décroissant</option>
          <option value="promo">Promotions</option>
          <option value="nom">Nom A → Z</option>
        </select>
      </div>

      {produitsFiltres.length === 0 ? (
        <p className="empty-message">Aucun téléphone ne correspond à votre recherche.</p>
      ) : (
        <div className="products-grid">
          {produitsFiltres.map((p) => (
            <CarteProduit key={p.id} produit={p} onAjouter={ajouterAuPanier} />
          ))}
        </div>
      )}
    </>
  );
}
