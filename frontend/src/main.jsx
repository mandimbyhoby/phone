import React from 'react';
import { createRoot } from 'react-dom/client';
import Catalog from './components/Catalog.jsx';
import SearchSuggestions from './components/SearchSuggestions.jsx';
import ProductDetail from './components/ProductDetail.jsx';
import Dashboard from './components/Dashboard.jsx';
import CartDrawer from './components/CartDrawer.jsx';
import CartPage from './components/CartPage.jsx';
import Checkout from './components/Checkout.jsx';
import MesCommandes from './components/MesCommandes.jsx';
import Profil from './components/Profil.jsx';
import ContactForm from './components/ContactForm.jsx';
import AuthForm from './components/AuthForm.jsx';
import ChangerMotDePasse from './components/ChangerMotDePasse.jsx';
import { BoutonReaction } from './components/Reactions.jsx';

// Montage conditionnel : chaque composant s'active uniquement si son
// conteneur est présent dans la page Django.
function mount(id, Component) {
  const el = document.getElementById(id);
  if (el) {
    createRoot(el).render(React.createElement(Component));
  }
}

// Catalogue & recherche
mount('react-catalog', Catalog);
mount('react-search', SearchSuggestions);
mount('react-detail', ProductDetail);
mount('react-dashboard', Dashboard);

// Panier & commande
mount('react-cart', CartDrawer);
mount('react-panier', CartPage);
mount('react-checkout', Checkout);

// Compte client
mount('react-commandes', MesCommandes);
mount('react-profil', Profil);
mount('react-mot-de-passe', ChangerMotDePasse);
mount('react-auth', AuthForm);

// Contact
mount('react-contact', ContactForm);

// Réactions « cœurs » des cartes produit rendues côté serveur (section
// « Vous aimerez aussi » de la fiche produit, repli <noscript> du catalogue).
// Chaque emplacement `[data-react-reaction]` devient un îlot React autonome :
// aucun marquage dupliqué, on réutilise le même composant que le catalogue.
document.querySelectorAll('[data-react-reaction]').forEach(function (emplacement) {
  createRoot(emplacement).render(
    React.createElement(BoutonReaction, {
      produitId: Number(emplacement.dataset.reactReaction),
      total: Number(emplacement.dataset.total || 0),
      actif: emplacement.dataset.actif || null,
    })
  );
});

