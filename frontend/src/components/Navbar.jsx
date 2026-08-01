import { NavLink } from 'react-router-dom';
import { Scale, Home, Sparkles } from 'lucide-react';

const navItems = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/summarizer', label: 'Summarizer', icon: Sparkles },
];

export default function Navbar() {
  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <NavLink to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-navy text-white">
            <Scale size={18} />
          </div>
          <div>
            <p className="font-heading text-sm font-semibold text-navy">District Court e-Services</p>
            <p className="text-xs text-slate-500">Multilingual Legal Summarizer</p>
          </div>
        </NavLink>

        <nav className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 p-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-navy text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-navy'
                }`
              }
            >
              <Icon size={16} />
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  );
}
