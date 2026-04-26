import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { Book, Clock, Plus, Loader, Search, MoreVertical, Pencil, Trash2, RotateCcw, X, Check, ArrowUpDown } from 'lucide-react';
import { useToast } from './Toast';
import { LibrarySkeleton } from './Skeleton';
import EmptyState from './EmptyState';
import { API_BASE } from '../config';

const SORT_OPTIONS = [
  { key: 'recent', label: 'Most Recent' },
  { key: 'name', label: 'Name A–Z' },
  { key: 'name-desc', label: 'Name Z–A' },
  { key: 'progress', label: 'Progress' },
];

export default function Library() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [newStoryName, setNewStoryName] = useState('');
  const [creatingStory, setCreatingStory] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [menuOpen, setMenuOpen] = useState(null);
  const [renaming, setRenaming] = useState(null);
  const [confirmDelete, setConfirmDelete] = useState(null);
  const navigate = useNavigate();
  const { addToast } = useToast();
  const menuRef = useRef(null);

  const fetchStories = () => {
    fetch(`${API_BASE}/api/stories/`)
      .then(res => { if (!res.ok) throw new Error(`HTTP ${res.status}`); return res.json(); })
      .then(data => { setStories(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => { addToast("Could not connect to the backend server.", "error"); setLoading(false); });
  };

  useEffect(() => { fetchStories(); }, []);

  useEffect(() => {
    if (stories.some(s => s.progress?.status === 'processing')) {
      const id = setInterval(fetchStories, 3000);
      return () => clearInterval(id);
    }
  }, [stories]);

  // Close menu on outside click
  useEffect(() => {
    const handler = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.target)) setMenuOpen(null);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  // ESC to close menus
  useEffect(() => {
    const handler = (e) => {
      if (e.key === 'Escape') { setMenuOpen(null); setRenaming(null); setConfirmDelete(null); }
    };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, []);

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importUrl) return;
    setImporting(true);
    addToast("Starting import... this may take a moment.", "info");
    try {
      const res = await fetch(`${API_BASE}/api/stories/import_url`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: importUrl })
      });
      const data = await res.json();
      if (data.status === 'success') {
        addToast(`Imported "${data.name || 'Novel'}"! Processing chapters in the background.`, "success");
        setImportUrl('');
        fetchStories();
      } else {
        addToast(`Import failed: ${data.detail || 'unknown error'}`, "error");
      }
    } catch { addToast("Network error. Is the backend running?", "error"); }
    finally { setImporting(false); }
  };

  const handleCreateStory = async (e) => {
    e.preventDefault();
    if (!newStoryName.trim()) return;
    setCreatingStory(true);
    try {
      const res = await fetch(`${API_BASE}/api/stories/create`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: newStoryName.trim() })
      });
      const data = await res.json();
      if (data.status === 'success') {
        addToast(`Created "${data.name}"`, "success");
        setNewStoryName('');
        setShowCreateForm(false);
        fetchStories();
      } else {
        addToast(`Failed: ${data.detail || 'unknown error'}`, "error");
      }
    } catch { addToast("Network error.", "error"); }
    finally { setCreatingStory(false); }
  };

  const handleRename = async (uuid) => {
    if (!renaming || !renaming.name.trim()) return;
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/rename`, {
        method: 'PUT', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: renaming.name.trim() })
      });
      const data = await res.json();
      if (data.status === 'success') {
        addToast(`Renamed to "${data.name}"`, "success");
        setRenaming(null);
        fetchStories();
      } else {
        addToast(`Rename failed: ${data.detail}`, "error");
      }
    } catch { addToast("Network error.", "error"); }
  };

  const handleDelete = async (uuid) => {
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}`, { method: 'DELETE' });
      const data = await res.json();
      if (data.status === 'success') {
        addToast("Story moved to trash.", "success");
        setConfirmDelete(null);
        setMenuOpen(null);
        fetchStories();
      } else {
        addToast(`Delete failed: ${data.detail}`, "error");
      }
    } catch { addToast("Network error.", "error"); }
  };

  const handleWipe = async (uuid) => {
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/wipe`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'success') {
        addToast("All story data wiped. Ready for fresh ingestion.", "success");
        setMenuOpen(null);
        fetchStories();
      } else {
        addToast(`Wipe failed: ${data.detail}`, "error");
      }
    } catch { addToast("Network error.", "error"); }
  };

  // 1.3 — Sort + filter
  const filtered = stories
    .filter(s => s.name.toLowerCase().includes(search.toLowerCase()))
    .sort((a, b) => {
      switch (sortBy) {
        case 'name': return a.name.localeCompare(b.name);
        case 'name-desc': return b.name.localeCompare(a.name);
        case 'progress': return (b.progress?.current || 0) - (a.progress?.current || 0);
        case 'recent':
        default: return new Date(b.updated_at) - new Date(a.updated_at);
      }
    });

  return (
    <div className="fade-in">
      <header>
        <h1>My Library</h1>
        <p>Your AI-generated webnovel audiobooks</p>
      </header>

      {/* Import Card */}
      <div className="card card--static" style={{ marginBottom: '1.25rem' }}>
        <h3 style={{ marginBottom: '0.75rem' }}>Add New Novel</h3>
        <form onSubmit={handleImport} style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="url"
            placeholder="Paste a RoyalRoad Fiction URL here..."
            value={importUrl}
            onChange={(e) => setImportUrl(e.target.value)}
          />
          <button type="submit" disabled={importing || !importUrl} style={{ whiteSpace: 'nowrap' }}>
            {importing ? <><Loader size={16} className="spin" /> Importing...</> : <><Plus size={16} /> Import</>}
          </button>
        </form>
      </div>

      {/* Create Blank Story */}
      <div className="card card--static" style={{ marginBottom: '2rem' }}>
        {!showCreateForm ? (
          <button
            className="btn-ghost"
            onClick={() => setShowCreateForm(true)}
            style={{ width: '100%', justifyContent: 'center', padding: '0.6rem', color: 'var(--text-muted)' }}
          >
            <Plus size={16} /> Create Blank Story
          </button>
        ) : (
          <form onSubmit={handleCreateStory} style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <input
              type="text"
              placeholder="Story name..."
              value={newStoryName}
              onChange={(e) => setNewStoryName(e.target.value)}
              autoFocus
            />
            <button type="submit" disabled={creatingStory || !newStoryName.trim()} style={{ whiteSpace: 'nowrap' }}>
              {creatingStory ? <Loader size={16} className="spin" /> : <Check size={16} />} Create
            </button>
            <button type="button" className="btn-ghost" onClick={() => { setShowCreateForm(false); setNewStoryName(''); }}>
              <X size={16} />
            </button>
          </form>
        )}
      </div>

      {/* Search + Sort Bar */}
      {stories.length > 0 && (
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={16} style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
            <input
              type="search" placeholder="Search library..."
              value={search} onChange={(e) => setSearch(e.target.value)}
              style={{ paddingLeft: '2.5rem' }}
            />
          </div>
          {/* 1.3 — Sort Dropdown */}
          <div className="sort-dropdown" style={{ position: 'relative' }}>
            <button className="btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.65rem 0.85rem', border: '1px solid var(--card-border)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', whiteSpace: 'nowrap' }}>
              <ArrowUpDown size={14} />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                style={{
                  background: 'transparent', border: 'none', color: 'var(--text-muted)',
                  fontFamily: 'inherit', fontSize: '0.85rem', cursor: 'pointer', outline: 'none'
                }}
              >
                {SORT_OPTIONS.map(o => <option key={o.key} value={o.key}>{o.label}</option>)}
              </select>
            </button>
          </div>
        </div>
      )}

      {loading ? <LibrarySkeleton /> : filtered.length === 0 && stories.length === 0 ? (
        <EmptyState icon="book" title="Your library is empty" message="Import a novel above to get started with AI-generated audiobooks." />
      ) : filtered.length === 0 ? (
        <EmptyState icon="search" title="No results" message={`No novels matching "${search}".`} />
      ) : (
        <div className="grid">
          {filtered.map(story => (
            <div key={story.uuid} className="card" style={{ position: 'relative' }} onClick={() => navigate(`/story/${story.uuid}`)}>
              {/* Context Menu Button */}
              <button
                className="btn-ghost story-menu-btn"
                onClick={(e) => { e.stopPropagation(); setMenuOpen(menuOpen === story.uuid ? null : story.uuid); setConfirmDelete(null); }}
                style={{ position: 'absolute', top: '0.75rem', right: '0.75rem', zIndex: 10, padding: '0.35rem' }}
                aria-label="Story options"
              >
                <MoreVertical size={18} />
              </button>

              {/* Context Menu Dropdown */}
              {menuOpen === story.uuid && (
                <div
                  ref={menuRef}
                  className="story-context-menu"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button onClick={() => { setRenaming({ uuid: story.uuid, name: story.name }); setMenuOpen(null); }}>
                    <Pencil size={14} /> Rename
                  </button>
                  <button onClick={() => handleWipe(story.uuid)}>
                    <RotateCcw size={14} /> Wipe Data
                  </button>
                  <div className="context-menu-divider" />
                  {confirmDelete === story.uuid ? (
                    <button className="context-menu-danger" onClick={() => handleDelete(story.uuid)}>
                      <Trash2 size={14} /> Confirm Delete
                    </button>
                  ) : (
                    <button className="context-menu-danger" onClick={() => setConfirmDelete(story.uuid)}>
                      <Trash2 size={14} /> Delete
                    </button>
                  )}
                </div>
              )}

              {/* Rename Overlay */}
              {renaming?.uuid === story.uuid && (
                <div className="rename-overlay" onClick={(e) => e.stopPropagation()}>
                  <form onSubmit={(e) => { e.preventDefault(); handleRename(story.uuid); }} style={{ display: 'flex', gap: '0.5rem', width: '100%' }}>
                    <input
                      type="text"
                      value={renaming.name}
                      onChange={(e) => setRenaming({ ...renaming, name: e.target.value })}
                      autoFocus
                      style={{ flex: 1, fontSize: '0.85rem' }}
                    />
                    <button type="submit" style={{ padding: '0.4rem 0.75rem', fontSize: '0.8rem' }}>
                      <Check size={14} />
                    </button>
                    <button type="button" className="btn-ghost" onClick={() => setRenaming(null)} style={{ padding: '0.4rem' }}>
                      <X size={14} />
                    </button>
                  </form>
                </div>
              )}

              {story.metadata?.cover_url ? (
                <div className="card-cover" style={{ backgroundImage: `url(${story.metadata.cover_url})` }} />
              ) : (
                <div className="card-cover card-cover--placeholder">
                  <Book size={56} color="var(--primary)" opacity={0.4} />
                </div>
              )}
              <h2 className="truncate" style={{ fontSize: '1.15rem', marginBottom: '0.4rem' }}>{story.name}</h2>
              {story.metadata?.synopsis && (
                <p className="text-muted" style={{ fontSize: '0.82rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden', marginBottom: '0.75rem', lineHeight: 1.5 }}>
                  {story.metadata.synopsis}
                </p>
              )}
              {story.progress?.status === 'processing' ? (
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 4, color: 'var(--primary)' }}>
                    <span>Processing Ingestion...</span>
                    <span>{story.progress.current} / {story.progress.total}</span>
                  </div>
                  <div className="progress-container">
                    <div className="progress-bar" style={{ width: `${story.progress.total ? (story.progress.current / story.progress.total) * 100 : 0}%` }} />
                  </div>
                </div>
              ) : (
                <div className="text-dim" style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem' }}>
                  <Clock size={14} />
                  <span>{new Date(story.updated_at).toLocaleDateString()}</span>
                  {story.progress?.current > 0 && story.progress?.total_available > 0 && (
                    <span style={{ marginLeft: 'auto', fontSize: '0.72rem', color: 'var(--text-dim)' }}>
                      {story.progress.current}/{story.progress.total_available} ch.
                    </span>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
