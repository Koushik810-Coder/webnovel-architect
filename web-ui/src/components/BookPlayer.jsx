import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, PlayCircle, Loader, Headphones } from 'lucide-react';
import { useToast } from './Toast';

const API_BASE = 'http://localhost:8000';

export default function BookPlayer() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  
  const [story, setStory] = useState(null);
  const [loading, setLoading] = useState(true);
  
  const [activeChapter, setActiveChapter] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [audioUrl, setAudioUrl] = useState(null);
  const [vttUrl, setVttUrl] = useState(null);

  const fetchStory = () => {
    console.debug(`[BookPlayer] Loading story details for UUID: ${uuid}`);
    fetch(`${API_BASE}/api/stories/${uuid}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        return res.json();
      })
      .then(data => {
        console.info(`[BookPlayer] Successfully loaded story: ${data.name}`);
        setStory(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('[BookPlayer] Error fetching story details:', err);
        addToast("Failed to load story details. Is the server online?", "error");
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchStory();
  }, [uuid]);

  // Poll for progress updates if the book is still ingesting
  useEffect(() => {
    if (story && story.progress?.status === 'processing') {
      const interval = setInterval(fetchStory, 3000);
      return () => clearInterval(interval);
    }
  }, [story]);

  const handlePlayChapter = async (chapterIndex) => {
    console.info(`[BookPlayer] Requesting audio for Chapter ${chapterIndex} of story ${uuid}`);
    setActiveChapter(chapterIndex);
    setAudioUrl(null);
    setVttUrl(null);
    setGenerating(true);
    addToast(`Preparing Chapter ${chapterIndex}...`, "info");

    try {
      const res = await fetch(`${API_BASE}/api/audio/${uuid}/chapter/${chapterIndex}`, {
        method: 'POST'
      });
      const data = await res.json();
      
      if (data.status === 'success') {
        console.info(`[BookPlayer] Audio generation successful: ${data.audio_path}`);
        setAudioUrl(`${API_BASE}${data.audio_path}`);
        setVttUrl(`${API_BASE}${data.vtt_path}`);
        addToast(`Chapter ${chapterIndex} ready!`, "success");
      } else {
        console.error('[BookPlayer] Audio generation failed:', data.status);
        addToast("Failed to render chapter audio. Note: Chapter must be processed/extracted first.", "error");
        setActiveChapter(null);
      }
    } catch (err) {
      console.error('[BookPlayer] Network error during audio generation:', err);
      addToast("Network error. Is the generator active?", "error");
      setActiveChapter(null);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Loading book details...</div>;
  if (!story) return <div style={{ textAlign: 'center', marginTop: '4rem' }}>Book not found.</div>;

  return (
    <div style={{ paddingBottom: audioUrl ? '150px' : '0' }}>
      <button 
        onClick={() => {
          console.debug('[BookPlayer] User navigating back to library.');
          navigate('/');
        }}
        style={{ background: 'transparent', padding: '0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}
      >
        <ArrowLeft size={20} /> Back to Library
      </button>

      <header style={{ marginTop: '2rem', textAlign: 'left' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>{story.name}</h1>
        <p style={{ color: 'var(--text-muted)' }}>
          {story.progress?.status === 'processing' 
            ? `Ingesting story content (${story.progress.current} / ${story.progress.total})...`
            : `${story.chapter_count} Available Chapters`
          }
        </p>
      </header>

      <div className="chapters-list" style={{ marginTop: '3rem' }}>
        {Array.from({ length: story.chapter_count }).map((_, i) => {
          const chIndex = i + 1;
          const isPlaying = activeChapter === chIndex;
          
          return (
            <div key={chIndex} className="chapter-row">
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div style={{ 
                  background: 'rgba(255,255,255,0.05)', 
                  width: '40px', height: '40px', 
                  borderRadius: '50%', 
                  display: 'flex', alignItems: 'center', justifyContent: 'center'
                }}>
                  {chIndex}
                </div>
                <span style={{ fontSize: '1.1rem', fontWeight: '500' }}>Chapter {chIndex}</span>
              </div>
              
              <button 
                onClick={() => handlePlayChapter(chIndex)}
                disabled={(generating && !isPlaying) || (story.progress?.status === 'processing' && chIndex > story.progress.current)}
                style={{ 
                  display: 'flex', alignItems: 'center', gap: '0.5rem',
                  background: isPlaying ? 'rgba(255,255,255,0.1)' : 'var(--primary)',
                  color: isPlaying ? 'var(--primary)' : 'white'
                }}
              >
                {generating && isPlaying ? (
                  <><Loader size={18} className="spin" /> Generating Audio...</>
                ) : isPlaying && audioUrl ? (
                  <><Headphones size={18} /> Now Playing</>
                ) : story.progress?.status === 'processing' && chIndex > story.progress.current ? (
                  <><Loader size={18} className="spin" /> Ingesting...</>
                ) : (
                  <><PlayCircle size={18} /> Play</>
                )}
              </button>
            </div>
          );
        })}
      </div>

      {audioUrl && (
        <div className="player-container">
          <div style={{ maxWidth: '800px', width: '100%', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <Headphones size={24} color="var(--primary)" />
            <div>
              <h3 style={{ margin: 0, fontSize: '1rem' }}>{story.name}</h3>
              <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-muted)' }}>Chapter {activeChapter}</p>
            </div>
          </div>
          <audio controls autoPlay crossOrigin="anonymous">
            <source src={audioUrl} type="audio/mpeg" />
            {vttUrl && <track label="English" kind="subtitles" srcLang="en" src={vttUrl} default />}
            Your browser does not support the audio element.
          </audio>
        </div>
      )}
    </div>
  );
}
