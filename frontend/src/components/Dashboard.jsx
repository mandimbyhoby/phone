import React, { useEffect, useState } from 'react';
import { fetchJson, formatPrix } from '../api.js';

const PERIODES = [
  { id: '7d', label: '7 derniers jours' },
  { id: '30d', label: '30 derniers jours' },
  { id: '12m', label: '12 derniers mois' },
];

function BarChart({ data, empty }) {
  if (!data || data.length === 0) {
    return <p>{empty || 'Aucune donnée sur la période.'}</p>;
  }
  return (
    <div className="bar-chart">
      {data.map((item, i) => (
        <div className="bar-col" key={i}>
          <span className="bar-value">{formatPrix(item.value)}</span>
          <div className="bar" style={{ height: item.height + '%' }}></div>
          <small>{item.label}</small>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard() {
  const [period, setPeriod] = useState('30d');
  const [stats, setStats] = useState(null);
  const [chargement, setChargement] = useState(true);
  const [erreur, setErreur] = useState(null);

  useEffect(() => {
    let actif = true;
    setChargement(true);
    setErreur(null);
    fetchJson('/api/dashboard/?period=' + period)
      .then((data) => {
        if (actif) {
          setStats(data);
          setChargement(false);
        }
      })
      .catch(() => {
        if (actif) {
          setErreur('Impossible de charger les statistiques.');
          setChargement(false);
        }
      });
    return () => {
      actif = false;
    };
  }, [period]);

  return (
    <>
      <div className="dashboard-filters">
        {PERIODES.map((p) => (
          <button
            key={p.id}
            type="button"
            className={'filter-btn' + (period === p.id ? ' active' : '')}
            onClick={() => setPeriod(p.id)}
          >
            {p.label}
          </button>
        ))}
      </div>

      {chargement && (
        <p style={{ textAlign: 'center', padding: '40px 0', color: '#94a3b8' }}>
          <i className="fa-solid fa-spinner fa-spin"></i> Chargement…
        </p>
      )}

      {erreur && (
        <p style={{ textAlign: 'center', padding: '40px 0', color: '#ef4444' }}>{erreur}</p>
      )}

      {stats && !chargement && (
        <>
          <div className="dashboard-stats">
            <div className="stat-card">
              <span>CA sur {stats.tempo_label}</span>
              <strong>{formatPrix(stats.ca_selectionne)}</strong>
            </div>
            <div className="stat-card">
              <span>CA total</span>
              <strong>{formatPrix(stats.ca_total)}</strong>
            </div>
            <div className="stat-card">
              <span>Commandes</span>
              <strong>{stats.nb_commandes}</strong>
            </div>
            <div className="stat-card">
              <span>Produits vendus</span>
              <strong>{stats.produits_vendus}</strong>
            </div>
            <div className="stat-card">
              <span>Panier moyen</span>
              <strong>{formatPrix(stats.panier_moyen)}</strong>
            </div>
            <div className="stat-card">
              <span>Nouveaux clients</span>
              <strong>{stats.nouveaux_clients}</strong>
            </div>
            <div className="stat-card">
              <span>Stock total</span>
              <strong>{stats.stock_total}</strong>
            </div>
            <div className="stat-card">
              <span>Commandes en attente</span>
              <strong>{stats.commandes_en_attente}</strong>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>CA par jour</h3>
              <BarChart data={stats.revenue_by_day} empty="Aucune donnée sur les 30 derniers jours." />
            </div>
            <div className="chart-card">
              <h3>CA par mois</h3>
              <BarChart data={stats.revenue_by_month} empty="Aucune donnée sur 12 mois." />
            </div>
            <div className="chart-card">
              <h3>Produits les plus populaires</h3>
              <ul className="top-products">
                {stats.produits_populaires.map((p, i) => (
                  <li key={p.id || i}>
                    <span>{i + 1}. {p.nom}</span>
                    <strong>{p.quantite} vendus</strong>
                  </li>
                ))}
                {stats.produits_populaires.length === 0 && (
                  <li>Aucun achat pour le moment.</li>
                )}
              </ul>
            </div>
            <div className="chart-card">
              <h3>Statut des commandes</h3>
              <div className="mini-metrics">
                <div>
                  <span>Confirmées</span>
                  <strong>{stats.commandes_confirmees}</strong>
                </div>
                <div>
                  <span>En attente</span>
                  <strong>{stats.commandes_en_attente}</strong>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
