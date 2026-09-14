import React, { useEffect, useRef, useState } from 'react';
import { fetchJson } from '../api.js';

const ICON = '/static/images/icons/recherche.svg';

export default function SearchSuggestions() {
  const [q, setQ] = useState('');
  const [results, setResults] = useState([]);
  const [open, setOpen] = useState(false);
  const timer = useRef(null);
  const boxRef = useRef(null);

  useEffect(() => {
    function onClick(e) {
      if (boxRef.current && !boxRef.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', onClick);
    return () => document.removeEventListener('mousedown', onClick);
  }, []);

  function onChange(e) {
    const value = e.target.value;
    setQ(value);
    clearTimeout(timer.current);
    if (!value.trim()) {
      setResults([]);
      setOpen(false);
      return;
    }
    timer.current = setTimeout(async () => {
      try {
        const data = await fetchJson('/recherche-suggestions/?q=' + encodeURIComponent(value));
        setResults(data.produits || []);
        setOpen(true);
      } catch {
        setResults([]);
      }
    }, 180);
  }

  function onSubmit(e) {
    e.preventDefault();
    if (results.length) {
      window.location.href = results[0].url;
    } else if (q.trim()) {
      window.location.href = '/?q=' + encodeURIComponent(q.trim());
    }
  }

  return (
    <form
      ref={boxRef}
      action="/"
      method="get"
      className="search-box"
      role="search"
      onSubmit={onSubmit}
    >
      <img src={ICON} alt="" width="18" height="18" className="search-prefix-icon" />
      <input
        type="text"
        name="q"
        placeholder="Rechercher un téléphone..."
        value={q}
        onChange={onChange}
        aria-label="Rechercher un téléphone"
      />
      <button type="submit" aria-label="Rechercher">
        <img src={ICON} alt="" width="20" height="20" className="search-icon" />
      </button>

      {open && (
        <div className="search-results-preview" role="status" aria-live="polite">
          {results.length ? (
            results.map((p) => (
              <a
                key={p.id}
                href={p.url}
                className="search-result-item"
                onClick={() => setOpen(false)}
              >
                <span className="search-result-image">
                  <img src={p.image} alt={p.nom} />
                </span>
                <span className="search-result-copy">
                  <strong>{p.nom}</strong>
                  <small>{p.marque} · {p.prix} Ar</small>
                </span>
                <i className="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
              </a>
            ))
          ) : (
            <span className="search-result-empty">Aucun téléphone trouvé</span>
          )}
        </div>
      )}
    </form>
  );
}
