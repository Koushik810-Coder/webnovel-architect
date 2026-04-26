import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft, PlayCircle, Loader, Headphones, Book, Users, MessageCircle, ChevronRight, ChevronDown, ChevronUp, SkipBack, SkipForward, Settings, Pencil, Trash2, RotateCcw, X, Check, Download, AlertCircle, RefreshCw } from 'lucide-react';
import { useToast } from './Toast';
import { ChapterListSkeleton } from './Skeleton';
import EmptyState from './EmptyState';
import { API_BASE } from '../config';

const SPEEDS = [0.75, 1, 1.25, 1.5, 2];

export default function BookPlayer() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const audioRef = useRef(null);

  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [chapters, setChapters] = useState([]);
  const [activeChapter, setActiveChapter] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [vttUrl, setVttUrl] = useState(null);
  const [speed, setSpeed] = useState(1);
  const [tab, setTab] = useState('chapters');
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [editingName, setEditingName] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [ingestCount, setIngestCount] = useState(5);
  const [ingesting, setIngesting] = useState(false);
  const [synopsisExpanded, setSynopsisExpanded] = useState(false);
  const settingsRef = useRef(null);

  const fetchStory = () => {
    fetch(`${API_BASE}/api/stories/${uuid}`)
      .then(r => { if (!r.ok) throw new Error(); return r.json(); })
      .then(data => { setStory(data); setLoading(false); })
      .catch(() => { addToast("Failed to load story.", "error"); setLoading(false); });
  };

  const fetchChapters = () => {
    fetch(`${API_BASE}/api/stories/${uuid}/chapters`)
      .then(r => r.ok ? r.json() : [])
      .then(data => Array.isArray(data) && setChapters(data))
      .catch(() => {});
  };

  useEffect(() => { fetchStory(); fetchChapters(); }, [uuid]);

  useEffect(() => {
    if (story?.progress?.status === 'processing') {
      const id = setInterval(() => { fetchStory(); fetchChapters(); }, 3000);
      return () => clearInterval(id);
    }
  }, [story]);

  useEffect(() => {
    if (audioRef.current) audioRef.current.playbackRate = speed;
  }, [speed, audioUrl]);

  // Close settings on outside click
  useEffect(() => {
    const handler = (e) => {
      if (settingsRef.current && !settingsRef.current.contains(e.target)) {
        setSettingsOpen(false); setConfirmDelete(false);
      }
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // Keyboard shortcut: ESC to close menus/editing
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') {
        setSettingsOpen(false); setConfirmDelete(false); setEditingName(null);
      }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const handleRename = async () => {
    if (!editingName?.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/rename`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: editingName.trim() })
      });
      const data = await res.json();
      if (data.status === 'success') {
        addToast(`Renamed to "${data.name}"`, 'success');
        setEditingName(null);
        fetchStory();
      }
    } catch { addToast('Network error.', 'error'); }
  };

  const handleDeleteStory = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        addToast('Story deleted.', 'success');
        navigate('/');
      }
    } catch { addToast('Network error.', 'error'); }
  };

  const handleWipe = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/wipe`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        addToast('All data wiped. Ready for fresh ingestion.', 'success');
        setSettingsOpen(false);
        fetchStory(); fetchChapters();
      }
    } catch { addToast('Network error.', 'error'); }
  };

  const handleIngestMore = async (count) => {
    const num = count || ingestCount;
    setIngesting(true);
    addToast(`Starting ingestion of ${num} more chapters...`, 'info');
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/ingest_more`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ count: num })
      });
      const data = await res.json();
      if (data.status === 'success') {
        addToast(data.message, 'success');
        fetchStory(); fetchChapters();
      } else {
        addToast(`Failed: ${data.detail || 'Unknown error'}`, 'error');
      }
    } catch { addToast('Network error.', 'error'); }
    finally { setIngesting(false); }
  };

  const handlePlay = async (idx) => {
    setActiveChapter(idx);
    setAudioUrl(null); setVttUrl(null); setGenerating(true);
    addToast(`Preparing Chapter ${idx}...`, "info");
    try {
      const res = await fetch(`${API_BASE}/api/audio/${uuid}/chapter/${idx}`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        setAudioUrl(`${API_BASE}${data.audio_path}`);
        setVttUrl(`${API_BASE}${data.vtt_path}`);
        addToast(`Chapter ${idx} ready!`, "success");
      } else {
        addToast("Audio generation failed. Ensure chapter is processed.", "error");
        setActiveChapter(null);
      }
    } catch { addToast("Network error.", "error"); setActiveChapter(null); }
    finally { setGenerating(false); }
  };

  const skipChapter = (dir) => {
    if (!activeChapter || !story) return;
    const next = activeChapter + dir;
    if (next >= 1 && next <= story.chapter_count) handlePlay(next);
  };

  if (loading) return <div style={{ paddingTop: '3rem' }}><ChapterListSkeleton /></div>;
  if (!story) return <EmptyState icon="error" title="Not Found" message="This book could not be found." action="Back to Library" onAction={() => navigate('/')} />;

  const remaining = (story.progress?.total_available || 0) - (story.progress?.current || 0);
  const isFailed = story.progress?.status === 'failed';
  const isProcessing = story.progress?.status === 'processing';
  const isAllDone = story.progress?.current >= story.progress?.total_available;

  return (
    <div className="fade-in" style={{ paddingBottom: audioUrl ? 140 : 0 }}>
      {/* Back */}
      <button className="btn-ghost" onClick={() => navigate('/')} style={{ marginBottom: '1.5rem' }}>
        <ArrowLeft size={18} /> Back to Library
      </button>

      {/* Book Header */}
      <div style={{ display: 'flex', gap: '1.5rem', marginBottom: '2rem', flexWrap: 'wrap' }}>
        {story.metadata?.cover_url ? (
          <img src={story.metadata.cover_url} alt="" style={{ width: 140, height: 200, objectFit: 'cover', borderRadius: 'var(--radius-md)', flexShrink: 0 }} />
        ) : (
          <div style={{ width: 140, height: 200, background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(139,92,246,0.15))', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Book size={48} color="var(--primary)" opacity={0.4} />
          </div>
        )}
        <div style={{ flex: 1, minWidth: 200 }}>
          {editingName !== null ? (
            <form onSubmit={(e) => { e.preventDefault(); handleRename(); }} style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.5rem', maxWidth: 500 }}>
              <input type="text" value={editingName} onChange={(e) => setEditingName(e.target.value)} autoFocus style={{ fontSize: '1.2rem', fontWeight: 700 }} />
              <button type="submit" style={{ padding: '0.4rem 0.75rem' }}><Check size={16} /></button>
              <button type="button" className="btn-ghost" onClick={() => setEditingName(null)}><X size={16} /></button>
            </form>
          ) : (
            <h1 style={{ fontSize: '1.8rem', fontWeight: 800, marginBottom: '0.5rem' }}>{story.name}</h1>
          )}

          {/* 1.1 — Collapsible Synopsis */}
          {story.metadata?.synopsis && (
            <div style={{ marginBottom: '0.75rem', maxWidth: 600 }}>
              <p className="text-muted" style={{
                fontSize: '0.9rem', lineHeight: 1.6,
                ...(!synopsisExpanded ? { display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden' } : {})
              }}>
                {story.metadata.synopsis}
              </p>
              {story.metadata.synopsis.length > 180 && (
                <button
                  className="btn-ghost synopsis-toggle"
                  onClick={() => setSynopsisExpanded(!synopsisExpanded)}
                  style={{ fontSize: '0.78rem', padding: '0.2rem 0', marginTop: '0.25rem', color: 'var(--primary)' }}
                >
                  {synopsisExpanded ? <><ChevronUp size={14} /> Show less</> : <><ChevronDown size={14} /> Read more</>}
                </button>
              )}
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', alignItems: 'center' }}>
            <span className="badge badge-primary">{story.chapter_count} Chapters</span>
            {isProcessing && <span className="badge badge-warning">Processing {story.progress.current}/{story.progress.total_available}</span>}
            {!isProcessing && !isFailed && story.progress?.current > 0 && <span className="badge badge-success">Ready</span>}
            {isFailed && <span className="badge" style={{ background: 'rgba(239,68,68,0.15)', color: 'var(--danger)' }}>Failed</span>}

            {/* Settings Gear */}
            <div style={{ position: 'relative', marginLeft: 'auto' }} ref={settingsRef}>
              <button className="btn-ghost" onClick={() => { setSettingsOpen(!settingsOpen); setConfirmDelete(false); }} aria-label="Story settings">
                <Settings size={18} />
              </button>
              {settingsOpen && (
                <div className="story-context-menu" style={{ right: 0, top: '2.2rem' }}>
                  <button onClick={() => { setEditingName(story.name); setSettingsOpen(false); }}>
                    <Pencil size={14} /> Rename
                  </button>
                  <button onClick={handleWipe}>
                    <RotateCcw size={14} /> Wipe Data
                  </button>
                  <div className="context-menu-divider" />
                  {confirmDelete ? (
                    <button className="context-menu-danger" onClick={handleDeleteStory}>
                      <Trash2 size={14} /> Confirm Delete
                    </button>
                  ) : (
                    <button className="context-menu-danger" onClick={() => setConfirmDelete(true)}>
                      <Trash2 size={14} /> Delete Story
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="tabs">
        <button className={`tab ${tab === 'chapters' ? 'active' : ''}`} onClick={() => setTab('chapters')}>
          <Book size={15} style={{ marginRight: 6, verticalAlign: -2 }} /> Chapters
        </button>
        <button className={`tab ${tab === 'cast' ? 'active' : ''}`} onClick={() => navigate(`/story/${uuid}/cast`)}>
          <Users size={15} style={{ marginRight: 6, verticalAlign: -2 }} /> Characters
        </button>
        <button className={`tab ${tab === 'ask' ? 'active' : ''}`} onClick={() => navigate(`/story/${uuid}/ask`)}>
          <MessageCircle size={15} style={{ marginRight: 6, verticalAlign: -2 }} /> Ask About Story
        </button>
      </div>

      {/* Chapter List */}
      {story.chapter_count === 0 ? (
        <EmptyState icon="book" title="No chapters yet" message="This book is still being processed. Chapters will appear here shortly." />
      ) : (
        <div className="chapters-list">
          {Array.from({ length: story.chapter_count }).map((_, i) => {
            const idx = i + 1;
            const isPlaying = activeChapter === idx;
            const chTitle = chapters[i]?.title || `Chapter ${idx}`;
            const isIngesting = story.progress?.status === 'processing' && idx > story.progress.current;

            return (
              <div key={idx} className={`chapter-row ${isPlaying && audioUrl ? 'chapter-row--active' : ''}`}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flex: 1, minWidth: 0 }}>
                  <div className="chapter-num">{idx}</div>
                  <div style={{ minWidth: 0 }}>
                    <span className="truncate" style={{ display: 'block', fontWeight: 500 }}>{chTitle}</span>
                    <Link to={`/story/${uuid}/read/${idx}`} className="text-dim" style={{ fontSize: '0.78rem' }} onClick={e => e.stopPropagation()}>
                      Read <ChevronRight size={12} style={{ verticalAlign: -1 }} />
                    </Link>
                  </div>
                </div>
                <button
                  onClick={() => handlePlay(idx)}
                  disabled={(generating && !isPlaying) || isIngesting}
                  style={isPlaying && audioUrl ? { background: 'rgba(255,255,255,0.08)', color: 'var(--primary)' } : {}}
                >
                  {generating && isPlaying ? <><Loader size={16} className="spin" /> Generating...</>
                    : isPlaying && audioUrl ? <><Headphones size={16} /> Playing</>
                    : isIngesting ? <><Loader size={16} className="spin" /> Ingesting...</>
                    : <><PlayCircle size={16} /> Play</>}
                </button>
              </div>
            );
          })}
        </div>
      )}

      {/* 1.5 — Error State for Failed Ingestion */}
      {isFailed && (
        <div className="card card--static ingest-error-banner" style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <AlertCircle size={22} color="var(--danger)" />
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: 'var(--danger)', marginBottom: '0.2rem' }}>Ingestion Failed</div>
              <p className="text-muted" style={{ fontSize: '0.85rem', margin: 0 }}>
                An error occurred during chapter processing. You can retry from where it left off.
              </p>
            </div>
            <button onClick={() => handleIngestMore(3)} disabled={ingesting} style={{ whiteSpace: 'nowrap' }}>
              {ingesting ? <><Loader size={16} className="spin" /> Retrying...</> : <><RefreshCw size={16} /> Retry</>}
            </button>
          </div>
        </div>
      )}

      {/* Ingestion Panel */}
      {story.progress && story.progress.total_available > 0 && !isFailed && (
        <div className="card card--static" style={{ marginTop: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>
              <Download size={16} style={{ marginRight: 6, verticalAlign: -2, color: 'var(--primary)' }} />
              Chapter Ingestion
            </h3>
            <span className="text-muted" style={{ fontSize: '0.82rem' }}>
              <span className="ingest-counter">{story.progress.current}</span> / {story.progress.total_available} chapters processed
            </span>
          </div>

          {/* Progress bar showing overall completion */}
          <div className="progress-container" style={{ height: 8, marginBottom: '1rem' }}>
            <div
              className="progress-bar"
              style={{ width: `${(story.progress.current / story.progress.total_available) * 100}%` }}
            />
          </div>

          {isProcessing ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <Loader size={18} className="spin" color="var(--primary)" />
              <span style={{ fontSize: '0.9rem', color: 'var(--primary)', fontWeight: 600 }}>
                Processing... {story.progress.current} / {story.progress.total_available} complete
              </span>
            </div>
          ) : isAllDone ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--success)', fontSize: '0.9rem', fontWeight: 600 }}>
              <Check size={16} /> All {story.progress.total_available} chapters ingested!
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', flexWrap: 'wrap' }}>
              <label className="text-muted" style={{ fontSize: '0.85rem', whiteSpace: 'nowrap' }}>Process next:</label>
              <input
                type="range"
                min={1}
                max={Math.min(remaining, 50)}
                value={Math.min(ingestCount, remaining)}
                onChange={(e) => setIngestCount(Number(e.target.value))}
                style={{ flex: 1, minWidth: 120, accentColor: 'var(--primary)' }}
              />
              <span style={{ fontWeight: 700, fontSize: '0.95rem', minWidth: 60, textAlign: 'center', color: 'var(--primary)' }}>
                {Math.min(ingestCount, remaining)} ch.
              </span>
              <button
                onClick={() => handleIngestMore()}
                disabled={ingesting}
                style={{ whiteSpace: 'nowrap' }}
              >
                {ingesting ? <><Loader size={16} className="spin" /> Starting...</> : <><Download size={16} /> Ingest</>}
              </button>

              {/* 1.4 — Ingest All Remaining */}
              {remaining > ingestCount && (
                <button
                  className="btn-ghost"
                  onClick={() => handleIngestMore(remaining)}
                  disabled={ingesting}
                  style={{ whiteSpace: 'nowrap', fontSize: '0.82rem', color: 'var(--primary)' }}
                >
                  Ingest All ({remaining})
                </button>
              )}
            </div>
          )}
        </div>
      )}

      {/* Audio Player */}
      {audioUrl && (
        <div className="player-container">
          <div className="player-info">
            <Headphones size={20} color="var(--primary)" />
            <div style={{ flex: 1, minWidth: 0 }}>
              <div className="truncate" style={{ fontWeight: 600, fontSize: '0.9rem' }}>{story.name}</div>
              <div className="text-dim" style={{ fontSize: '0.75rem' }}>Chapter {activeChapter}</div>
            </div>
            <div className="player-controls">
              <button className="btn-ghost" onClick={() => skipChapter(-1)} aria-label="Previous chapter"><SkipBack size={16} /></button>
              <button className="btn-ghost" onClick={() => skipChapter(1)} aria-label="Next chapter"><SkipForward size={16} /></button>
              {SPEEDS.map(s => (
                <button key={s} className={`speed-btn ${speed === s ? 'active' : ''}`} onClick={() => setSpeed(s)}>{s}x</button>
              ))}
            </div>
          </div>
          <audio ref={audioRef} controls autoPlay crossOrigin="anonymous" style={{ width: '100%', maxWidth: 700 }}>
            <source src={audioUrl} type="audio/mpeg" />
            {vttUrl && <track label="English" kind="subtitles" srcLang="en" src={vttUrl} default />}
          </audio>
        </div>
      )}
    </div>
  );
}
