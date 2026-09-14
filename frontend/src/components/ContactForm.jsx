import React, { useState } from 'react';
import { messageErreur, postJson, toast } from '../api.js';

const CHAMPS_INITIAUX = {
  nom: '',
  email: '',
  sujet: '',
  message: '',
};

// Formulaire de contact dynamique (soumission AJAX, validation des champs).
export default function ContactForm() {
  const [form, setForm] = useState(CHAMPS_INITIAUX);
  const [erreurs, setErreurs] = useState({});
  const [envoi, setEnvoi] = useState(false);
  const [envoye, setEnvoye] = useState(false);

  function majChamp(nom, valeur) {
    setForm((actuel) => ({ ...actuel, [nom]: valeur }));
    setErreurs((actuel) => ({ ...actuel, [nom]: undefined }));
  }

  async function onSubmit(e) {
    e.preventDefault();
    setEnvoi(true);
    setErreurs({});

    const res = await postJson('/api/contact/', form);
    setEnvoi(false);

    if (!res.ok) {
      if (res.data && res.data.erreurs) {
        setErreurs(res.data.erreurs);
        toast('Veuillez corriger les champs signalés.', 'error');
      } else {
        toast(messageErreur(res.data, "Impossible d'envoyer le message."), 'error');
      }
      return;
    }

    setForm(CHAMPS_INITIAUX);
    setEnvoye(true);
    toast(res.data.detail || 'Message envoyé, merci !', 'success');
  }

  const champErreur = (nom) =>
    erreurs[nom] && erreurs[nom].length ? (
      <small className="form-error">{erreurs[nom].join(' ')}</small>
    ) : null;
  const classeInput = (nom) => 'form-input' + (erreurs[nom] ? ' is-invalid' : '');

  return (
    <div className="contact-form-box" id="react-contact">
      <h3><i className="fa-solid fa-paper-plane"></i> Envoyez-nous un message</h3>

      {envoye && (
        <div className="form-success form-success-box">
          <i className="fa-solid fa-circle-check"></i> Votre message a bien été envoyé, merci !
        </div>
      )}

      <form onSubmit={onSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="id_nom">Nom</label>
            <input
              id="id_nom"
              className={classeInput('nom')}
              type="text"
              placeholder="Votre nom"
              value={form.nom}
              onChange={(e) => majChamp('nom', e.target.value)}
              required
            />
            {champErreur('nom')}
          </div>
          <div className="form-group">
            <label htmlFor="id_email">Email</label>
            <input
              id="id_email"
              className={classeInput('email')}
              type="email"
              placeholder="email@exemple.com"
              value={form.email}
              onChange={(e) => majChamp('email', e.target.value)}
              required
            />
            {champErreur('email')}
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="id_sujet">Sujet</label>
          <input
            id="id_sujet"
            className={classeInput('sujet')}
            type="text"
            placeholder="Objet du message"
            value={form.sujet}
            onChange={(e) => majChamp('sujet', e.target.value)}
            required
          />
          {champErreur('sujet')}
        </div>

        <div className="form-group">
          <label htmlFor="id_message">Message</label>
          <textarea
            id="id_message"
            className={classeInput('message')}
            rows={5}
            placeholder="Votre message..."
            value={form.message}
            onChange={(e) => majChamp('message', e.target.value)}
            required
          ></textarea>
          {champErreur('message')}
        </div>

        <button type="submit" className="buy-btn submit-order" disabled={envoi}>
          <i className="fa-solid fa-paper-plane"></i>{' '}
          {envoi ? 'Envoi…' : 'Envoyer le message'}
        </button>
      </form>
    </div>
  );
}
