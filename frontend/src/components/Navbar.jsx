import { NavLink, useNavigate } from 'react-router-dom';
import { Scale, Home, Sparkles, FolderKanban, LogIn, LogOut, User } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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

        <div className="flex items-center gap-3">
          <nav className="flex items-center gap-2 rounded-full border border-slate-200 bg-slate-50 p-1">
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-navy text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-navy'
                }`
              }
            >
              <Home size={16} />
              Home
            </NavLink>
            <NavLink
              to="/summarizer"
              className={({ isActive }) =>
                `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-navy text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-navy'
                }`
              }
            >
              <Sparkles size={16} />
              AI Summarizer
            </NavLink>
            {isAuthenticated && user?.role === 'admin' && (
              <NavLink
                to="/admin"
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-navy text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-navy'
                  }`
                }
              >
                <FolderKanban size={16} />
                Admin Panel
              </NavLink>
            )}
            {isAuthenticated && user?.role !== 'admin' && (
              <NavLink
                to="/dashboard"
                className={({ isActive }) =>
                  `flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition ${
                    isActive ? 'bg-navy text-white shadow-sm' : 'text-slate-600 hover:bg-white hover:text-navy'
                  }`
                }
              >
                <FolderKanban size={16} />
                My Cases
              </NavLink>
            )}
          </nav>

          {isAuthenticated ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-100 text-slate-700 text-xs font-semibold">
                <User size={13} className="text-slate-500" />
                <span className="truncate max-w-[120px]">{user?.email || 'User'}</span>
                <span className="text-[10px] uppercase tracking-wider bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded">
                  {user?.role || 'user'}
                </span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center gap-1.5 rounded-full border border-slate-200 px-3 py-2 text-xs font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition"
                title="Sign Out"
              >
                <LogOut size={14} />
                <span className="hidden sm:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <NavLink
              to="/login"
              className="flex items-center gap-1.5 rounded-full bg-blue-600 px-4 py-2 text-xs font-semibold text-white shadow-sm hover:bg-blue-700 transition"
            >
              <LogIn size={14} />
              Sign In
            </NavLink>
          )}
        </div>
      </div>
    </header>
  );
}
