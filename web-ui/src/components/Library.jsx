import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Book, Clock, Plus, Loader } from 'lucide-react';
import { useToast } from './Toast';

const API_BASE = 'http://localhost:8000';

export default function Library() {
  const [stories, setStories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [importUrl, setImportUrl] = useState('');
  const [importing, setImporting] = useState(false);
  const navigate = useNavigate();
  const { addToast } = useToast();

  const fetchStories = () => {
    console.debug('[Library] Fetching story list...');
    fetch(`${API_BASE}/api/stories/`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) {
          console.info(`[Library] Successfully loaded ${data.length} stories.`);
          setStories(data);
        } else {
          console.error('[Library] Expected array of stories, got:', data);
          setStories([]);
          addToast("Received invalid data format from server.", "error");
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('[Library] Error fetching stories:', err);
        addToast("Could not connect to the backend server. Please ensure it's running.", "error");
        setLoading(false);
      });
  };

  useEffect(() => {
    console.debug('[Library] Component mounted.');
    fetchStories();
  }, []);

  // Poll for progress if any story is processing
  useEffect(() => {
    const isAnyStoryProcessing = stories.some(s => s.progress?.status === 'processing');
    
    if (isAnyStoryProcessing) {
      console.debug('[Library] Detected stories in progress. Starting polling interval...');
      const interval = setInterval(fetchStories, 3000);
      return () => {
        console.debug('[Library] Stopping polling interval.');
        clearInterval(interval);
      }
    }
  }, [stories]);

  const handleImport = async (e) => {
    e.preventDefault();
    if (!importUrl) return;
    
    console.info(`[Library] Starting import from: ${importUrl}`);
    setImporting(true);
    addToast("Starting import... this may take a moment.", "info");

    try {
      const res = await fetch(`${API_BASE}/api/stories/import_url`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: importUrl })
      });
      const data = await res.json();
      
      if(data.status === 'success') {
        console.info(`[Library] Import successful. New Story UUID: ${data.story_uuid}`);
        addToast("Import started! Processing the first chapters in the background.", "success");
        setImportUrl('');
        fetchStories();
      } else {
        console.error('[Library] Import failed:', data.detail || 'Unknown error');
        addToast(`Failed to import: ${data.detail || 'check engine logs'}`, "error");
      }
    } catch(err) {
      console.error('[Library] Network error during import:', err);
      addToast("Network error. Is the backend running?", "error");
    } finally {
      setImporting(false);
    }
  };

  return (
    <div>
      <header>
        <h1>My Library</h1>
        <p>Listen to your generated webnovel audiobooks.</p>
      </header>

      <div className="card" style={{ marginBottom: '3rem', cursor: 'default' }}>
        <h3 style={{ marginBottom: '1rem', color: 'var(--text-main)' }}>Add New Novel</h3>
        <form onSubmit={handleImport} style={{ display: 'flex', gap: '1rem' }}>
          <input 
            type="url" 
            placeholder="Paste a RoyalRoad Fiction URL here..." 
            value={importUrl}
            onChange={(e) => setImportUrl(e.target.value)}
            style={{ 
              flex: 1, 
              padding: '0.75rem 1rem', 
              borderRadius: '8px', 
              border: '1px solid var(--card-border)',
              background: 'rgba(0,0,0,0.2)',
              color: 'var(--text-main)',
              fontFamily: 'inherit',
              fontSize: '1rem'
            }}
          />
          <button type="submit" disabled={importing || !importUrl} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {importing ? <><Loader size={18} className="spin" /> Importing...</> : <><Plus size={18} /> Import Book</>}
          </button>
        </form>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading novels...</div>
      ) : (
        <div className="grid">
          {stories.length === 0 && (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', color: 'var(--text-muted)' }}>
              Your library is empty. Import a novel above to get started.
            </div>
          )}
          {stories.map(story => (
            <div 
              key={story.uuid} 
              className="card" 
              onClick={() => {
                console.debug(`[Library] Navigating to story: ${story.uuid}`);
                navigate(`/story/${story.uuid}`);
              }}
            >
              {story.metadata?.cover_url ? (
                <div style={{
                  height: '220px',
                  backgroundImage: `url(${story.metadata.cover_url})`,
                  backgroundSize: 'cover',
                  backgroundPosition: 'center',
                  borderRadius: '8px',
                  marginBottom: '1rem'
                }} />
              ) : (
                <div style={{ 
                  height: '220px', 
                  background: 'linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))',
                  borderRadius: '8px',
                  marginBottom: '1rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}>
                  <Book size={64} color="var(--primary)" opacity={0.5} />
                </div>
              )}
              
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.5rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {story.name}
              </h2>
              
              {story.metadata?.synopsis && (
                <p style={{
                  fontSize: '0.85rem',
                  color: 'var(--text-muted)',
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                  marginBottom: '1rem'
                }}>
                  {story.metadata.synopsis}
                </p>
              )}
              
              {story.progress?.status === 'processing' ? (
                <div style={{ marginTop: '0.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '4px', color: 'var(--primary)' }}>
                    <span>Processing Ingestion...</span>
                    <span>{story.progress.current} / {story.progress.total}</span>
                  </div>
                  <div className="progress-container">
                    <div 
                      className="progress-bar" 
                      style={{ width: `${(story.progress.current / story.progress.total) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ) : (
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  <Clock size={16} />
                  <span>Last updated: {new Date(story.updated_at).toLocaleDateString()}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
