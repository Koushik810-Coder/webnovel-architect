import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Send, Loader } from 'lucide-react';
import { useToast } from './Toast';
import { API_BASE } from '../config';

const EXAMPLES = [
  "What happened after the battle in the cavern?",
  "Who are the main allies of the protagonist?",
  "Summarize the events of the latest chapter.",
];

export default function StoryChat() {
  const { uuid } = useParams();
  const navigate = useNavigate();
  const { addToast } = useToast();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [asking, setAsking] = useState(false);

  const handleAsk = async (q) => {
    const query = q || input.trim();
    if (!query || asking) return;
    setInput('');
    setMessages(m => [...m, { role: 'user', text: query }]);
    setAsking(true);
    try {
      const res = await fetch(`${API_BASE}/api/stories/${uuid}/ask`, {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      const data = await res.json();
      setMessages(m => [...m, { role: 'assistant', text: data.answer || data.detail || 'No answer generated.' }]);
    } catch { addToast("Failed to get answer.", "error"); setMessages(m => [...m, { role: 'assistant', text: 'Network error.' }]); }
    finally { setAsking(false); }
  };

  return (
    <div className="fade-in">
      <button className="btn-ghost" onClick={() => navigate(`/story/${uuid}`)} style={{ marginBottom: '1.5rem' }}>
        <ArrowLeft size={18} /> Back to Book
      </button>
      <header><h1>Ask About the Story</h1><p>Ask questions and the AI will reason through the story timeline</p></header>

      <div className="card card--static chat-container">
        <div className="chat-messages">
          {messages.length === 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', flex: 1, gap: '1rem' }}>
              <p className="text-dim" style={{ fontSize: '0.9rem' }}>Try asking something like...</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {EXAMPLES.map((ex, i) => (
                  <button key={i} className="btn-ghost" onClick={() => handleAsk(ex)}
                    style={{ textAlign: 'left', padding: '0.6rem 1rem', border: '1px solid var(--card-border)', borderRadius: 'var(--radius-sm)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    "{ex}"
                  </button>
                ))}
              </div>
            </div>
          )}
          {messages.map((m, i) => <div key={i} className={`chat-bubble ${m.role}`}>{m.text}</div>)}
          {asking && <div className="chat-bubble assistant"><Loader size={14} className="spin" style={{ marginRight: 6 }} /> Thinking through the timeline...</div>}
        </div>
        <div className="chat-input-row">
          <input value={input} onChange={e => setInput(e.target.value)} placeholder="Ask about the story..."
            onKeyDown={e => e.key === 'Enter' && handleAsk()} disabled={asking} />
          <button onClick={() => handleAsk()} disabled={asking || !input.trim()}><Send size={16} /></button>
        </div>
      </div>
    </div>
  );
}
