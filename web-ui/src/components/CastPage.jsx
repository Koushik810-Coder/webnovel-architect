import { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, Shield, User } from 'lucide-react';
import { useToast } from './Toast';
import EmptyState from './EmptyState';
import { API_BASE } from '../config';
const COLORS = ['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#ef4444','#06b6d4','#f97316'];

export default function CastPage() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [cast, setCast] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    fetch(`${API_BASE}/api/stories/${uuid}/cast`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d => { setCast(Array.isArray(d) ? d : []); setLoading(false); })
      .catch(() => { addToast("Failed to load characters.", "error"); setLoading(false); });
  }, [uuid]);

  const filtered = cast.filter(c => {
    if (filter === 'main') return c.graduated;
    if (filter === 'bg') return !c.graduated;
    return true;
  }).sort((a, b) => b.confidence_score - a.confidence_score);

  return (
    <div className="fade-in">
      <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}`)} style={{ marginBottom: '1.5rem' }}>
        <ArrowLeft size={18} /> Back to Book
      </button>
      <header><h1>Character Cast</h1><p>Characters discovered from the story</p></header>

      <div className="tabs">
        {['all','main','bg'].map(f => (
          <button key={f} className={`tab ${filter === f ? 'active' : ''}`} onClick={() => setFilter(f)}>
            {f === 'all' ? 'All' : f === 'main' ? 'Main Cast' : 'Background'}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="grid">{Array.from({length:6}).map((_,i) => <div key={i} className="skeleton skeleton-card" style={{height:160}} />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon="book" title="No characters yet" message="Process some chapters to discover characters." />
      ) : (
        <div className="grid">
          {filtered.map((c, i) => (
            <Link key={c.character_id} to={`/story/${uuid}/wiki/${c.character_id}`} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <div className="char-avatar" style={{ background: COLORS[i % COLORS.length] }}>
                  {(c.display_name || c.character_id)[0].toUpperCase()}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div className="truncate" style={{ fontWeight: 600, marginBottom: '0.25rem' }}>{c.display_name || c.character_id}</div>
                  {c.short_description && <p className="text-muted" style={{ fontSize: '0.8rem', lineHeight: 1.4, marginBottom: '0.5rem' }}>{c.short_description}</p>}
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                    {c.graduated ? (
                      <span className="badge badge-success"><Shield size={10} /> Main Cast</span>
                    ) : (
                      <span className="badge badge-muted"><User size={10} /> Background</span>
                    )}
                    {c.voice_id && <span className="badge badge-primary">🎙 {c.voice_id}</span>}
                    <span className="badge badge-muted">Ch. {c.first_seen}–{c.last_seen}</span>
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
