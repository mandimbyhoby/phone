import React, { useEffect, useState } from 'react';
import { fetchJson, messageErreur, postJson, toast } from '../api.js';
import CompteMenu from './CompteMenu.jsx';

const CHAMPS = [
  { nom: 'old_password', label: 'Mot de passe actuel' },
  { nom: 'new_password1', label: 'Nouveau mot de passe' },
  { nom: 'new_password2', label: 'Confirmer le nouveau mot de passe' },
];

// Page « Changer mon mot de passe » rendue par React.
export default function ChangerMotDePasse() {
  const [profil, setProfil] = useState(null);
  const [form, setForm] = useState({});
  const [erreurs, setErreurs] = useState({});
  const [envoi, setEnvoi] = useState(false);

  useEffect(() => {
    fetchJson('/api/profil/')
      .then((data) => setProfil(data.profil))
      .catch(() => setProfil(null));
  }, []);

  function maj(nom, valeur) {
    setForm((actuel) => ({ ...actuel, [nom]: valeur }));
    setErreurs((actuel) => ({ ...actuel, [nom]: undefined }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreurs({});

    const res = await postJson('/api/profil/mot-de-passe/', form);
    setEnvoi(false);

    if (!res.ok) {
      if (res.data && res.data.erreurs) setErreurs(res.data.erreurs);
      toast(messageErreur(res.data, 'Impossible de changer le mot de passe.'), 'error');
      return;
    }

    setForm({});
    toast(res.data.detail || 'Mot de passe modifié.', 'success');
  }

  return (
    <div className="account-layout">
      <CompteMenu
        active="mdp"
        username={profil ? profil.username : ''}
        nomComplet={profil ? profil.nom_complet : ''}
        email={profil ? profil.email : ''}
        photoUrl={profil ? profil.photo_url : null}
      />

      <div className="account-content">
        <div className="account-card" id="pwd">
          <h3><i className="fa-solid fa-key"></i> Nouveau mot de passe</h3>
          <form onSubmit={onSubmit}>
            {CHAMPS.map((champ) => (
              <div className="form-group" key={champ.nom}>
                <label htmlFor={'id_' + champ.nom}>{champ.label}</label>
                <input
                  id={'id_' + champ.nom}
                  className={'form-input' + (erreurs[champ.nom] ? ' is-invalid' : '')}
                  type="password"
                  value={form[champ.nom] || ''}
                  onChange={(e) => maj(champ.nom, e.target.value)}
                  placeholder={champ.label}
                  required
                />
                {erreurs[champ.nom] && erreurs[champ.nom].length ? (
                  <small className="form-error">{erreurs[champ.nom].join(' ')}</small>
                ) : null}
              </div>
            ))}

            <button type="submit" className="buy-btn submit-order" disabled={envoi}>
              <i className="fa-solid fa-check"></i>{' '}
              {envoi ? 'Modification…' : 'Changer mon mot de passe'}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
