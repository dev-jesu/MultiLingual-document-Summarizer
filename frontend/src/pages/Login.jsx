import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAuth } from '../contexts/AuthContext';
import {
  Scale, User, Lock, ArrowRight, AlertCircle,
  Eye, EyeOff, Shield, Info
} from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password);
      // Route based on role
      if (user?.role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Login failed. Please check your credentials.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const demoAccounts = [
    { label: 'Admin', username: 'admin', password: 'Admin@123', color: 'text-amber-600 bg-amber-50 border-amber-200' },
    { label: 'Advocate 1', username: 'adv001', password: 'Adv@12345', color: 'text-blue-600 bg-blue-50 border-blue-200' },
    { label: 'Advocate 2', username: 'adv002', password: 'Adv@67890', color: 'text-violet-600 bg-violet-50 border-violet-200' },
  ];

  const fillDemo = (account) => {
    setUsername(account.username);
    setPassword(account.password);
  };

  return (
    <div className="relative min-h-[calc(100vh-140px)] flex items-center justify-center px-4 py-12 overflow-hidden">

      {/* Background orbs */}
      <div className="pointer-events-none absolute inset-0">
        <div className="absolute -top-32 -left-32 h-96 w-96 rounded-full bg-blue-100/70 blur-3xl" />
        <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-indigo-100/60 blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="relative w-full max-w-md"
      >
        {/* Logo Header */}
        <div className="text-center mb-8">
          <div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-navy to-blue-800 text-white shadow-xl shadow-navy/25 mb-4">
            <Scale size={28} />
          </div>
          <h1 className="font-heading text-2xl font-bold text-slate-900 mb-1">Welcome Back</h1>
          <p className="text-slate-500 text-sm">Sign in to your District Court e-Services account</p>
        </div>

        {/* Login Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/60 border border-slate-100 p-8">

          {/* Secure badge */}
          <div className="flex items-center gap-2 justify-center mb-6 rounded-xl bg-slate-50 border border-slate-100 px-4 py-2.5">
            <Shield size={13} className="text-emerald-600" />
            <span className="text-xs font-medium text-slate-600">Secured by Local JWT Auth</span>
          </div>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-2 bg-red-50 text-red-700 text-sm rounded-xl px-4 py-3 mb-5 border border-red-100"
            >
              <AlertCircle size={16} className="shrink-0" />
              <span>{error}</span>
            </motion.div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Username
              </label>
              <div className="relative">
                <User size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={e => setUsername(e.target.value)}
                  required
                  placeholder="admin / adv001 / adv002"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:bg-white focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-slate-700 mb-1.5">
                Password
              </label>
              <div className="relative">
                <Lock size={17} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  id="password"
                  type={showPass ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  placeholder="Enter your password"
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 py-3 pl-11 pr-11 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:bg-white focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                />
                <button
                  type="button"
                  onClick={() => setShowPass(p => !p)}
                  className="absolute right-3.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 transition"
                >
                  {showPass ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <motion.button
              type="submit"
              disabled={loading}
              whileHover={{ scale: loading ? 1 : 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="mt-2 w-full flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-navy to-blue-700 py-3.5 text-sm font-bold text-white shadow-lg shadow-navy/20 hover:from-[#16304d] hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-navy/30 transition disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="h-5 w-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                <>Sign In <ArrowRight size={16} /></>
              )}
            </motion.button>
          </form>
        </div>

        {/* Demo accounts */}
        <div className="mt-6 bg-white rounded-2xl border border-slate-100 shadow-sm p-5">
          <div className="flex items-center gap-2 mb-3">
            <Info size={14} className="text-slate-400" />
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Demo Accounts</span>
          </div>
          <div className="space-y-2">
            {demoAccounts.map(acc => (
              <button
                key={acc.username}
                type="button"
                onClick={() => fillDemo(acc)}
                className={`w-full flex items-center justify-between rounded-xl border px-4 py-2.5 text-xs font-medium transition hover:opacity-80 ${acc.color}`}
              >
                <span className="font-bold">{acc.label}</span>
                <span className="opacity-70">{acc.username} / {acc.password}</span>
              </button>
            ))}
          </div>
          <p className="text-[11px] text-slate-400 text-center mt-3">Click any account to auto-fill credentials</p>
        </div>
      </motion.div>
    </div>
  );
}
