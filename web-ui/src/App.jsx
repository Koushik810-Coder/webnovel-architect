import { Routes, Route } from 'react-router-dom';
import AppShell from './components/AppShell';
import Library from './components/Library';
import BookPlayer from './components/BookPlayer';
import ReaderView from './components/ReaderView';
import CastPage from './components/CastPage';
import WikiViewer from './components/WikiViewer';
import StoryChat from './components/StoryChat';

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<Library />} />
        <Route path="/story/:uuid" element={<BookPlayer />} />
        <Route path="/story/:uuid/read/:chapter" element={<ReaderView />} />
        <Route path="/story/:uuid/cast" element={<CastPage />} />
        <Route path="/story/:uuid/wiki/:characterId" element={<WikiViewer />} />
        <Route path="/story/:uuid/ask" element={<StoryChat />} />
      </Routes>
    </AppShell>
  );
}

export default App;
