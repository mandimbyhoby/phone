import React, { useEffect, useState } from 'react';
import { messageErreur, postJson, toast } from '../api.js';

// ------------------------------------------------------------
// Réactions « cœurs »
//
// Trois réactions sont proposées. Toutes utilisent le glyphe
// Font Awesome « heart » : seules les TEINTES diffèrent, ce qui
// répond à la demande « format cœurs ». Les clés ci-dessous
// doivent rester synchronisées avec `Reaction.TYPES` côté Django
// (`boutique/models.py`), faute de quoi le serveur refusera la
// réaction avec un code 400.
// ------------------------------------------------------------

export const TYPES_REACTION = [
  { cle: 'aime', libelle: "J'aime", classe: 'is-aime' },
  { cle: 'adore', libelle: "J'adore", classe: 'is-adore' },
  { cle: 'wow', libelle: 'Wow !', classe: 'is-wow' },
];

function classeDe(cle) {
  const type = TYPES_REACTION.find((t) => t.cle === cle);
  return type ? type.classe : '';
}

function libelleDe(cle) {
  const type = TYPES_REACTION.find((t) => t.cle === cle);
  return type ? type.libelle : '';
}

function pluriel(nombre) {
  return nombre > 1 ? 's' : '';
}

// Envoie la réaction au serveur. Le serveur renvoie toujours le résumé à jour
// (total, détail par cœur, réaction du visiteur) : l'interface n'a donc rien à
// recalculer, ce qui évite toute désynchronisation entre les deux.
async function envoyerReaction(produitId, type) {
  const reponse = await postJson('/api/produits/' + produitId + '/reaction/', { type });
  if (!reponse.ok) {
    return {
      ok: false,
      message: messageErreur(reponse.data, "Impossible d'enregistrer votre réaction."),
    };
  }
  return { ok: true, resume: reponse.data };
}

// ============================================================
// Bouton cœur compact — un par carte produit
// ============================================================

export function BoutonReaction({ produitId, total = 0, actif = null }) {
  const [nombre, setNombre] = useState(total);
  const [maReaction, setMaReaction] = useState(actif);
  const [envoi, setEnvoi] = useState(false);

  // Le catalogue peut être rechargé (filtre, tri, recherche) : on resynchronise
  // l'affichage sur les valeurs reçues du serveur.
  useEffect(() => {
    setNombre(total || 0);
  }, [total]);

  useEffect(() => {
    setMaReaction(actif || null);
  }, [actif]);

  async function basculer() {
    if (envoi) return;
    setEnvoi(true);

    // Re-cliquer sur le cœur déjà choisi le retire ; sinon on enregistre
    // « J'aime ». C'est le serveur qui applique cette règle, ici on ne fait
    // que transmettre le type courant.
    const resultat = await envoyerReaction(produitId, maReaction || 'aime');

    if (resultat.ok) {
      setNombre(resultat.resume.total);
      setMaReaction(resultat.resume.ma_reaction);
    } else {
      toast(resultat.message, 'error');
    }
    setEnvoi(false);
  }

  const classes =
    'react-heart' +
    (maReaction ? ' is-active ' + classeDe(maReaction) : '') +
    (envoi ? ' is-busy' : '');

  return (
    <button
      type="button"
      className={classes}
      onClick={basculer}
      disabled={envoi}
      aria-pressed={maReaction ? 'true' : 'false'}
      title={maReaction ? 'Retirer ma réaction' : "J'aime ce produit"}
      aria-label={
        (maReaction ? 'Retirer ma réaction' : "J'aime ce produit") +
        ' — ' + nombre + ' réaction' + pluriel(nombre)
      }
    >
      <i
        className={maReaction ? 'fa-solid fa-heart' : 'fa-regular fa-heart'}
        aria-hidden="true"
      ></i>
      <span className="react-heart-count">{nombre}</span>
    </button>
  );
}

// ============================================================
// Interface de réaction — fiche produit
// ============================================================

export function InterfaceReaction({ produitId, resume = null, maReaction = null }) {
  const [parType, setParType] = useState((resume && resume.par_type) || {});
  const [total, setTotal] = useState((resume && resume.total) || 0);
  const [actif, setActif] = useState(maReaction || (resume && resume.ma_reaction) || null);
  const [envoi, setEnvoi] = useState(false);

  async function reagir(cle) {
    if (envoi) return;
    setEnvoi(true);

    const resultat = await envoyerReaction(produitId, cle);

    if (resultat.ok) {
      setParType(resultat.resume.par_type || {});
      setTotal(resultat.resume.total || 0);
      setActif(resultat.resume.ma_reaction);
      toast(
        resultat.resume.ma_reaction
          ? 'Merci pour votre réaction !'
          : 'Votre réaction a été retirée.',
        'success'
      );
    } else {
      toast(resultat.message, 'error');
    }
    setEnvoi(false);
  }

  return (
    <div className="reaction-interface">
      <div className="reaction-head">
        <strong>Votre réaction</strong>
        <span className="reaction-total">
          {total} réaction{pluriel(total)}
        </span>
      </div>

      <div className="reaction-picker" role="group" aria-label="Choisir une réaction">
        {TYPES_REACTION.map((type) => {
          const choisi = actif === type.cle;
          const nombre = parType[type.cle] || 0;

          return (
            <button
              key={type.cle}
              type="button"
              className={'reaction-choice ' + type.classe + (choisi ? ' is-active' : '')}
              onClick={() => reagir(type.cle)}
              disabled={envoi}
              aria-pressed={choisi ? 'true' : 'false'}
              title={type.libelle}
            >
              <i
                className={choisi ? 'fa-solid fa-heart' : 'fa-regular fa-heart'}
                aria-hidden="true"
              ></i>
              <span className="reaction-choice-label">{type.libelle}</span>
              <span className="reaction-choice-count">{nombre}</span>
            </button>
          );
        })}
      </div>

      <p className="reaction-hint">
        {actif
          ? 'Re-cliquez sur « ' + libelleDe(actif) + ' » pour retirer votre réaction.'
          : 'Dites aux autres ce que vous pensez de ce produit.'}
      </p>
    </div>
  );
}
