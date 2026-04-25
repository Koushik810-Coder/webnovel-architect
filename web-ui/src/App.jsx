import { Routes, Route } from 'react-router-dom';
import Library from './components/Library';
import BookPlayer from './components/BookPlayer';

function App() {
  return (
    <div className="container">
      <Routes>
        <Route path="/" element={<Library />} />
        <Route path="/story/:uuid" element={<BookPlayer />} />
      </Routes>
    </div>
  );
}

export default App;
