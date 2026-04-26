import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Minus, Plus, ChevronLeft, ChevronRight, Type } from 'lucide-react';
import { useToast } from './Toast';
import { API_BASE } from '../config';

const FONTS = [
  { key: 'sans', label: 'Sans-serif', family: "'Inter', system-ui, sans-serif" },
  { key: 'serif', label: 'Serif', family: "'Georgia', 'Times New Roman', serif" },
  { key: 'mono', label: 'Mono', family: "'JetBrains Mono', 'Fira Code', monospace" },
];

const THEMES = [
  { key: 'dark', label: 'Dark', bg: 'transparent', color: 'var(--text-main)' },
  { key: 'sepia', label: 'Sepia', bg: 'rgba(180, 140, 80, 0.08)', color: '#d4c5a0' },
  { key: 'light', label: 'Light', bg: 'rgba(255, 255, 255, 0.06)', color: '#e2e8f0' },
];

export default function ReaderView() {
  const { uuid, chapter } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [fontSize, setFontSize] = useState(1.05);
  const [fontIdx, setFontIdx] = useState(0);
  const [themeIdx, setThemeIdx] = useState(0);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE}/api/stories/${uuid}/chapters/${chapter}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(d => { setData(d); setLoading(false); window.scrollTo(0, 0); })
      .catch(() => { addToast("Failed to load chapter.", "error"); setLoading(false); });
  }, [uuid, chapter]);

  const chNum = parseInt(chapter);
  const font = FONTS[fontIdx];
  const theme = THEMES[themeIdx];

  const NavButtons = ({ style }) => (
    <div style={{ display: 'flex', justifyContent: 'space-between', maxWidth: 680, margin: '0 auto', ...style }}>
      <button className="btn-ghost" disabled={chNum <= 1} onClick={() => navigate(`/story/${uuid}/read/${chNum - 1}`)}>
        <ChevronLeft size={16} /> Previous
      </button>
      <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}`)}>
        Ch. {chNum}
      </button>
      <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}/read/${chNum + 1}`)}>
        Next <ChevronRight size={16} />
      </button>
    </div>
  );

  return (
    <div className="fade-in">
      {/* 1.2 — Sticky reader header with nav + settings */}
      <div className="reader-header">
        <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}`)}>
          <ArrowLeft size={18} /> Back
        </button>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button className="btn-ghost" disabled={chNum <= 1} onClick={() => navigate(`/story/${uuid}/read/${chNum - 1}`)} aria-label="Previous chapter">
            <ChevronLeft size={16} />
          </button>
          <span className="text-muted" style={{ fontSize: '0.85rem', minWidth: 60, textAlign: 'center' }}>
            Ch. {chNum}
          </span>
          <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}/read/${chNum + 1}`)} aria-label="Next chapter">
            <ChevronRight size={16} />
          </button>
          <div style={{ width: 1, height: 20, background: 'var(--card-border)', margin: '0 0.25rem' }} />
          {/* Font size controls */}
          <button className="btn-ghost" onClick={() => setFontSize(f => Math.max(0.8, f - 0.1))} aria-label="Decrease font"><Minus size={14} /></button>
          <span className="text-dim" style={{ fontSize: '0.75rem', width: 36, textAlign: 'center' }}>{Math.round(fontSize * 100)}%</span>
          <button className="btn-ghost" onClick={() => setFontSize(f => Math.min(1.5, f + 0.1))} aria-label="Increase font"><Plus size={14} /></button>
          <div style={{ width: 1, height: 20, background: 'var(--card-border)', margin: '0 0.25rem' }} />
          {/* Typography toggle */}
          <button className="btn-ghost" onClick={() => setShowSettings(!showSettings)} aria-label="Typography settings">
            <Type size={16} />
          </button>
        </div>
      </div>

      {/* Typography settings dropdown */}
      {showSettings && (
        <div className="reader-settings-panel">
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
            <label className="text-dim" style={{ fontSize: '0.78rem', minWidth: 50 }}>Font:</label>
            {FONTS.map((f, i) => (
              <button
                key={f.key}
                className={`btn-ghost ${fontIdx === i ? 'reader-setting-active' : ''}`}
                onClick={() => setFontIdx(i)}
                style={{ fontSize: '0.82rem', padding: '0.3rem 0.65rem', fontFamily: f.family }}
              >{f.label}</button>
            ))}
          </div>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <label className="text-dim" style={{ fontSize: '0.78rem', minWidth: 50 }}>Theme:</label>
            {THEMES.map((t, i) => (
              <button
                key={t.key}
                className={`btn-ghost ${themeIdx === i ? 'reader-setting-active' : ''}`}
                onClick={() => setThemeIdx(i)}
                style={{ fontSize: '0.82rem', padding: '0.3rem 0.65rem' }}
              >{t.label}</button>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <div className="reader-content"><div className="skeleton" style={{ height: 400 }} /></div>
      ) : !data ? (
        <div className="reader-content text-muted" style={{ textAlign: 'center' }}>Chapter not found.</div>
      ) : (
        <>
          <h1 style={{ textAlign: 'center', fontSize: '1.6rem', marginBottom: '2rem', marginTop: '1rem' }}>{data.title || `Chapter ${chapter}`}</h1>
          <div
            className="reader-content"
            style={{
              fontSize: `${fontSize}rem`,
              fontFamily: font.family,
              color: theme.color,
              background: theme.bg,
              borderRadius: theme.bg !== 'transparent' ? 'var(--radius-lg)' : 0,
              padding: theme.bg !== 'transparent' ? '2rem 1.5rem' : '2rem 1rem',
            }}
          >
            {data.text?.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)}
          </div>
          <NavButtons style={{ padding: '2rem 1rem' }} />
        </>
      )}
    </div>
  );
}
