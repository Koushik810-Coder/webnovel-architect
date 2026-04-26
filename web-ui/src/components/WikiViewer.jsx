import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Download, Sparkles, Loader } from 'lucide-react';
import { useToast } from './Toast';
import { API_BASE } from '../config';

export default function WikiViewer() {
  const { uuid, characterId } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [wiki, setWiki] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enriching, setEnriching] = useState(false);

  const fetchWiki = () => {
    fetch(`${API_BASE}/api/stories/${uuid}/wiki/${characterId}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d => { setWiki(d); setLoading(false); })
      .catch(() => { addToast("Failed to load wiki.", "error"); setLoading(false); });
  };

  useEffect(() => { fetchWiki(); }, [uuid, characterId]);

  const handleEnrich = async () => {
    setEnriching(true);
    addToast("Enriching wiki with AI...", "info");
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/wiki/${characterId}/enrich`, { method: 'POST' });
      if (res.ok) { addToast("Wiki enriched!", "success"); fetchWiki(); }
      else addToast("Enrichment failed.", "error");
    } catch { addToast("Network error.", "error"); }
    finally { setEnriching(false); }
  };

  const renderList = (items, empty) => {
    if (!items?.length) return <p className="text-dim">{empty}</p>;
    return <ul style={{ paddingLeft: '1.2rem', color: 'var(--text-muted)', lineHeight: 1.7 }}>{items.map((t,i) => <li key={i}>{t}</li>)}</ul>;
  };

  if (loading) return <div style={{ padding: '3rem' }}><div className="skeleton" style={{ height: 400 }} /></div>;
  if (!wiki) return <div className="text-muted" style={{ textAlign: 'center', padding: '3rem' }}>Character not found.</div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '0.5rem' }}>
        <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}/cast`)}><ArrowLeft size={18} /> Cast</button>
        <div style={{ display: 'flex', gap: '0.5rem' }}>
          <button onClick={handleEnrich} disabled={enriching} style={{ background: 'var(--accent)' }}>
            {enriching ? <><Loader size={14} className="spin" /> Enriching...</> : <><Sparkles size={14} /> Improve with AI</>}
          </button>
          <button className="btn-ghost" onClick={() => {
            const blob = new Blob([JSON.stringify(wiki, null, 2)], { type: 'application/json' });
            const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
            a.download = `${characterId}.json`; a.click();
          }}><Download size={14} /> Export</button>
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'flex-start', marginBottom: '2rem', flexWrap: 'wrap' }}>
        <div className="char-avatar" style={{ background: '#8b5cf6', width: 64, height: 64, fontSize: '1.6rem' }}>
          {(wiki.display_name || characterId)[0].toUpperCase()}
        </div>
        <div>
          <h1 style={{ fontSize: '1.6rem', marginBottom: '0.25rem' }}>{wiki.display_name}</h1>
          <p className="text-muted" style={{ fontSize: '0.9rem', maxWidth: 500 }}>{wiki.short_description}</p>
          <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.5rem', flexWrap: 'wrap' }}>
            {wiki.gender && <span className="badge badge-muted">{wiki.gender}</span>}
            {wiki.species && <span className="badge badge-muted">{wiki.species}</span>}
            {wiki.role && <span className="badge badge-primary">{wiki.role}</span>}
            {wiki.status && <span className="badge badge-success">{wiki.status}</span>}
            {wiki.voice_id && <span className="badge badge-primary">🎙 {wiki.voice_id}</span>}
          </div>
        </div>
      </div>

      <div className="wiki-content">
        {wiki.long_description && <div className="wiki-section"><h3>📖 Biography</h3><p style={{ lineHeight: 1.7, color: 'var(--text-muted)' }}>{wiki.long_description}</p></div>}
        {wiki.appearance && <div className="wiki-section"><h3>👁️ Appearance</h3><p style={{ lineHeight: 1.7, color: 'var(--text-muted)' }}>{wiki.appearance}</p></div>}
        <div className="wiki-section"><h3>🧠 Personality</h3>{renderList(wiki.personality_traits, 'Not yet documented.')}</div>
        <div className="wiki-section"><h3>🎭 Quirks</h3>{renderList(wiki.notable_quirks, 'None documented.')}</div>
        {wiki.affiliations?.length > 0 && (
          <div className="wiki-section"><h3>🏛️ Affiliations</h3>
            <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>{wiki.affiliations.map((a,i) => <span key={i} className="badge badge-muted">{a}</span>)}</div>
          </div>
        )}
        {wiki.relationships?.length > 0 && (
          <div className="wiki-section"><h3>🕸️ Relationships</h3>
            {wiki.relationships.map((r,i) => (
              <div key={i} style={{ padding: '0.5rem 0', borderBottom: '1px solid var(--card-border)', fontSize: '0.9rem' }}>
                <strong style={{ color: 'var(--primary)' }}>{r.target_id}</strong> — <span className="text-muted">{r.relation}</span>
                {r.context && <span className="text-dim"> · {r.context}</span>}
              </div>
            ))}
          </div>
        )}
        {wiki.timeline?.length > 0 && (
          <div className="wiki-section"><h3>📜 Timeline</h3>
            {wiki.timeline.map((ev,i) => (
              <div key={i} style={{ padding: '0.4rem 0', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                <span className="badge badge-muted" style={{ marginRight: '0.5rem' }}>Ch. {ev.chapter}</span> {ev.event}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
