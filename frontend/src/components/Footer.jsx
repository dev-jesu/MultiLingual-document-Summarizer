import { Scale } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="border-t border-slate-200/80 bg-white/80 backdrop-blur mt-auto">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center justify-between gap-4 sm:flex-row">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-navy text-white">
              <Scale size={14} />
            </div>
            <div>
              <p className="text-sm font-semibold text-navy">District Court e-Services</p>
              <p className="text-xs text-slate-400">Multilingual Legal Summarizer</p>
            </div>
          </div>

          <div className="flex items-center gap-6 text-xs text-slate-500">
            <Link to="/" className="hover:text-navy transition-colors">Home</Link>
            <Link to="/summarizer" className="hover:text-navy transition-colors">AI Summarizer</Link>
            <Link to="/dashboard" className="hover:text-navy transition-colors">Workspace</Link>
          </div>

          <p className="text-xs text-slate-400">
            © {new Date().getFullYear()} e-Court Services. Powered by Gemini AI.
          </p>
        </div>
      </div>
    </footer>
  );
}
