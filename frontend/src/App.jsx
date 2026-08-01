import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import Summarizer from './pages/Summarizer';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slatebg font-body text-textdark">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/summarizer" element={<Summarizer />} />
        </Routes>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
