import React, { useState } from 'react';
import { messageErreur, postJson, toast } from '../api.js';

function Champ({ id, label, erreur, children, hint }) {
  return (
    <div className="form-group">
      <label htmlFor={id}>{label}</label>
      {children}
      {erreur && erreur.length ? <small className="form-error">{erreur.join(' ')}</small> : null}
      {hint ? <small className="form-hint">{hint}</small> : null}
    </div>
  );
}

function ChampMotDePasse({ id, label, valeur, onChange, erreur, hint }) {
  const [visible, setVisible] = useState(false);
  return (
    <Champ id={id} label={label} erreur={erreur} hint={hint}>
      <div className="password-field">
        <input
          id={id}
          className={'form-input' + (erreur ? ' is-invalid' : '')}
          type={visible ? 'text' : 'password'}
          value={valeur}
          onChange={(e) => onChange(e.target.value)}
          placeholder={label}
          required
        />
        <button
          type="button"
          className="password-toggle"
          onClick={() => setVisible((v) => !v)}
          aria-label={(visible ? 'Masquer' : 'Afficher') + ' ' + label}
          aria-pressed={visible}
        >
          <i className={'fa-solid ' + (visible ? 'fa-eye-slash' : 'fa-eye')} aria-hidden="true"></i>
        </button>
      </div>
    </Champ>
  );
}

// Formulaires de connexion et d'inscription, montés selon data-mode.
export default function AuthForm() {
  const el = document.getElementById('react-auth');
  const mode = el && el.dataset.mode === 'inscription' ? 'inscription' : 'connexion';
  const nextUrl = (el && el.dataset.next) || '';

  const [form, setForm] = useState({
    username: '',
    password: '',
    nom_complet: '',
    email: '',
    telephone: '',
    ville: '',
    adresse: '',
    password1: '',
    password2: '',
  });
  const [erreurs, setErreurs] = useState({});
  const [envoi, setEnvoi] = useState(false);

  function maj(nom, valeur) {
    setForm((actuel) => ({ ...actuel, [nom]: valeur }));
    setErreurs((actuel) => ({ ...actuel, [nom]: undefined }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreurs({});

    const url = mode === 'inscription' ? '/api/inscription/' : '/api/connexion/';
    const res = await postJson(url, form);

    if (res.ok && res.data) {
      toast(res.data.detail || 'Bienvenue !', 'success');
      window.location.href = nextUrl || res.data.redirect || '/';
      return;
    }

    if (res.data && res.data.erreurs) {
      setErreurs(res.data.erreurs);
      toast('Veuillez corriger les champs signalés.', 'error');
    } else {
      toast(messageErreur(res.data, 'Connexion impossible.'), 'error');
    }
    setEnvoi(false);
  }

  if (mode === 'inscription') {
    return (
      <div className="auth-box auth-box-wide">
        <div className="auth-head">
          <div className="auth-logo"><i className="fa-solid fa-user-plus"></i></div>
          <h1>Créer mon compte</h1>
          <p>Inscrivez-vous pour commander et suivre vos achats</p>
        </div>

        <form className="auth-form" onSubmit={onSubmit}>
          <div className="form-row">
            <Champ id="id_username" label="Nom d'utilisateur" erreur={erreurs.username}>
              <input
                id="id_username"
                className={'form-input' + (erreurs.username ? ' is-invalid' : '')}
                type="text"
                placeholder="Nom d'utilisateur"
                value={form.username}
                onChange={(e) => maj('username', e.target.value)}
                required
              />
            </Champ>
            <Champ id="id_nom_complet" label="Nom complet" erreur={erreurs.nom_complet}>
              <input
                id="id_nom_complet"
                className={'form-input' + (erreurs.nom_complet ? ' is-invalid' : '')}
                type="text"
                placeholder="Votre nom et prénom"
                value={form.nom_complet}
                onChange={(e) => maj('nom_complet', e.target.value)}
                required
              />
            </Champ>
          </div>

          <div className="form-row">
            <Champ id="id_email" label="Email" erreur={erreurs.email}>
              <input
                id="id_email"
                className={'form-input' + (erreurs.email ? ' is-invalid' : '')}
                type="email"
                placeholder="email@exemple.com"
                value={form.email}
                onChange={(e) => maj('email', e.target.value)}
                required
              />
            </Champ>
            <Champ id="id_telephone" label="Téléphone" erreur={erreurs.telephone}>
              <input
                id="id_telephone"
                className={'form-input' + (erreurs.telephone ? ' is-invalid' : '')}
                type="tel"
                placeholder="+261 34 00 000 00"
                value={form.telephone}
                onChange={(e) => maj('telephone', e.target.value)}
              />
            </Champ>
          </div>

          <div className="form-row">
            <Champ id="id_ville" label="Ville" erreur={erreurs.ville}>
              <input
                id="id_ville"
                className={'form-input' + (erreurs.ville ? ' is-invalid' : '')}
                type="text"
                placeholder="Antananarivo"
                value={form.ville}
                onChange={(e) => maj('ville', e.target.value)}
              />
            </Champ>
            <Champ id="id_adresse" label="Adresse" erreur={erreurs.adresse}>
              <textarea
                id="id_adresse"
                className={'form-input' + (erreurs.adresse ? ' is-invalid' : '')}
                rows={2}
                placeholder="Adresse de livraison"
                value={form.adresse}
                onChange={(e) => maj('adresse', e.target.value)}
              ></textarea>
            </Champ>
          </div>

          <div className="form-row password-row">
            <ChampMotDePasse
              id="id_password1"
              label="Mot de passe"
              valeur={form.password1}
              onChange={(v) => maj('password1', v)}
              erreur={erreurs.password1}
            />
            <ChampMotDePasse
              id="id_password2"
              label="Confirmer le mot de passe"
              valeur={form.password2}
              onChange={(v) => maj('password2', v)}
              erreur={erreurs.password2}
            />
          </div>

          <button type="submit" className="buy-btn submit-order" disabled={envoi}>
            <i className="fa-solid fa-user-check"></i>{' '}
            {envoi ? 'Création…' : 'Créer mon compte'}
          </button>
        </form>

        <div className="auth-footer">
          <p>Déjà inscrit ? <a href="/connexion/">Se connecter</a></p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-box">
      <div className="auth-head">
        <div className="auth-logo"><i className="fa-solid fa-user-lock"></i></div>
        <h1>Connexion</h1>
        <p>Accédez à votre compte pour passer commande</p>
      </div>

      <form className="auth-form" onSubmit={onSubmit}>
        <Champ id="id_username" label="Nom d'utilisateur ou email" erreur={erreurs.username}>
          <input
            id="id_username"
            className={'form-input' + (erreurs.username ? ' is-invalid' : '')}
            type="text"
            placeholder="Votre nom d'utilisateur"
            value={form.username}
            onChange={(e) => maj('username', e.target.value)}
            required
          />
        </Champ>

        <ChampMotDePasse
          id="id_password"
          label="Mot de passe"
          valeur={form.password}
          onChange={(v) => maj('password', v)}
          erreur={erreurs.password}
        />

        <div className="auth-links">
          <a href="/mot-de-passe-oublie/"><i className="fa-solid fa-key"></i> Mot de passe oublié ?</a>
        </div>

        <button type="submit" className="buy-btn submit-order" disabled={envoi}>
          <i className="fa-solid fa-right-to-bracket"></i>{' '}
          {envoi ? 'Connexion…' : 'Se connecter'}
        </button>
      </form>

      <div className="auth-footer">
        <p>Pas encore de compte ? <a href="/inscription/">Créer un compte</a></p>
      </div>
    </div>
  );
}
