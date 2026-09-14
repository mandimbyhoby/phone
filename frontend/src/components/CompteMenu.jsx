import React from 'react';

// Menu latéral du compte client, partagé par les pages « Mon compte »
// et « Mes commandes ».
export default function CompteMenu({ active, nomComplet, email, photoUrl, username }) {
  const initiale = (username || '?').charAt(0).toUpperCase();

  return (
    <aside className="account-menu">
      <div className="account-avatar">
        {photoUrl ? <img src={photoUrl} alt="Photo de profil" /> : initiale}
      </div>
      <h3>{nomComplet || username || 'Mon compte'}</h3>
      {email ? <p className="account-email">{email}</p> : null}
      <nav>
        <a href="/profil/" className={active === 'profil' ? 'active' : ''}>Mes informations</a>
        <a href="/profil/mot-de-passe/" className={active === 'mdp' ? 'active' : ''}>
          Changer mon mot de passe
        </a>
        <a href="/mes-commandes/" className={active === 'commandes' ? 'active' : ''}>Mes commandes</a>
        <a href="/deconnexion/">Se déconnecter</a>
      </nav>
    </aside>
  );
}
