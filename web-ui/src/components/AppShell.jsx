import { useState, useEffect } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { BookOpen, Library, Menu, X } from 'lucide-react';
import { API_BASE } from '../config';

export default function AppShell({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [health, setHealth] = useState(null);
  const location = useLocation();

  useEffect(() => { setSidebarOpen(false); }, [location]);

  useEffect(() => {
    const check = () => fetch(`${API_BASE}/api/health`).then(() => setHealth('online')).catch(() => setHealth('offline'));
    check();
    const id = setInterval(check, 30000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="app-shell">
      <button className="sidebar-toggle" onClick={() => setSidebarOpen(!sidebarOpen)} aria-label="Toggle navigation">
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      <aside className={`app-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="sidebar-brand">
          <h1>📖 Webnovel Architect</h1>
          <p>Story Intelligence Engine</p>
        </div>
        <nav className="sidebar-nav">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'active' : ''}>
            <Library size={18} /> My Library
          </NavLink>
        </nav>
        <div className="sidebar-status">
          <span className="status-dot" style={health === 'offline' ? { background: 'var(--danger)', animation: 'none' } : {}} />
          {health === 'online' ? 'Engine Online' : health === 'offline' ? 'Engine Offline' : 'Connecting...'}
        </div>
      </aside>

      <main className="app-main">
        <div className="container">
          {children}
        </div>
      </main>
    </div>
  );
}
