import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  FolderKanban, Plus, FileText, Calendar, Sparkles,
  ArrowRight, Scale, Clock, CheckCircle, AlertCircle,
  TrendingUp, Users, ChevronRight, Loader2, Shield
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import Modal from '../components/Modal';

const STATUS_CONFIG = {
  active:   { label: 'Active',   color: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-400' },
  pending:  { label: 'Pending',  color: 'bg-amber-100 text-amber-700',   dot: 'bg-amber-400' },
  closed:   { label: 'Closed',   color: 'bg-slate-100 text-slate-600',   dot: 'bg-slate-400' },
  default:  { label: 'Unknown',  color: 'bg-slate-100 text-slate-500',   dot: 'bg-slate-300' },
};

const CASE_COLORS = [
  'from-navy/90 to-blue-900',
  'from-indigo-700 to-indigo-900',
  'from-violet-700 to-violet-900',
  'from-blue-700 to-blue-900',
  'from-teal-700 to-teal-900',
];

function StatCard({ icon: Icon, label, value, sub, color }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-2xl border border-slate-100 p-6 shadow-sm hover:shadow-md transition-all duration-200"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className={`mt-1 text-3xl font-bold ${color || 'text-slate-900'}`}>{value}</p>
          {sub && <p className="mt-1 text-xs text-slate-400">{sub}</p>}
        </div>
        <div className={`flex h-11 w-11 items-center justify-center rounded-xl ${color ? 'bg-navy/10' : 'bg-slate-100'}`}>
          <Icon size={20} className={color || 'text-slate-500'} />
        </div>
      </div>
    </motion.div>
  );
}

function CaseCard({ c, index }) {
  const status = STATUS_CONFIG[c.status] || STATUS_CONFIG.default;
  const gradient = CASE_COLORS[index % CASE_COLORS.length];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.06 }}
      whileHover={{ y: -4, transition: { duration: 0.2 } }}
    >
      <Link to={`/cases/${c.id}`} className="block h-full">
        <div className="h-full rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-xl transition-all duration-300 overflow-hidden group">
          {/* Top color stripe */}
          <div className={`h-1.5 w-full bg-gradient-to-r ${gradient}`} />

          <div className="p-6">
            {/* Header */}
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} text-white shadow-sm`}>
                <Scale size={18} />
              </div>
              <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${status.color}`}>
                <span className={`h-1.5 w-1.5 rounded-full ${status.dot}`} />
                {status.label}
              </span>
            </div>

            {/* Case number */}
            <h3 className="mt-3 font-bold text-slate-900 leading-snug line-clamp-2 group-hover:text-navy transition-colors">
              {c.case_number}
            </h3>

            {/* Court */}
            <p className="mt-1 text-xs text-slate-500 line-clamp-1">{c.court_name}</p>

            {/* Description */}
            {c.description && (
              <p className="mt-3 text-sm text-slate-600 line-clamp-2 leading-relaxed">{c.description}</p>
            )}

            {/* Footer */}
            <div className="mt-4 flex items-center justify-between border-t border-slate-100 pt-4">
              <span className="inline-flex items-center gap-1.5 rounded-lg bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-600">
                <Clock size={11} />
                {c.stage || 'Initial Stage'}
              </span>
              <ChevronRight size={16} className="text-slate-300 group-hover:text-navy group-hover:translate-x-1 transition-all duration-200" />
            </div>
          </div>
        </div>
      </Link>
    </motion.div>
  );
}

export default function Dashboard() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);

  const { user, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return; }
    // If admin, redirect to admin panel
    if (isAdmin) { navigate('/admin'); return; }

    api.get('/cases/')
      .then(res => { if (Array.isArray(res.data)) setCases(res.data); })
      .catch(err => console.error('Failed to load cases:', err))
      .finally(() => setLoading(false));
  }, [isAuthenticated, navigate, isAdmin]);

  const activeCases = cases.filter(c => c.status === 'active').length;
  const pendingCases = cases.filter(c => c.status === 'pending').length;

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={32} className="animate-spin text-navy" />
          <p className="text-sm text-slate-500">Loading your workspace…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slatebg">
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">

        {/* Page Header */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-10 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
        >
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold uppercase tracking-widest text-gold">Legal Workspace</span>
            </div>
            <h1 className="font-heading text-3xl font-bold text-navy sm:text-4xl">
              {user?.email ? `Welcome back` : 'Dashboard'}
            </h1>
            {user?.email && (
              <p className="mt-1 text-sm text-slate-500">
                Signed in as <span className="font-medium text-slate-700">{user.email}</span>
                {user.role && <span className="ml-2 rounded-full bg-blue-100 px-2 py-0.5 text-xs font-medium text-blue-700">{user.role}</span>}
              </p>
            )}
          </div>

          {/* Info banner for advocates */}
          <div className="inline-flex items-center gap-2 rounded-xl bg-amber-50 border border-amber-100 px-4 py-2.5 text-xs text-amber-700">
            <AlertCircle size={14} className="shrink-0" />
            <span>Cases and documents are managed by your admin. You can view and summarize assigned documents.</span>
          </div>
        </motion.div>

        {/* Stats Row */}
        <div className="mb-10 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <StatCard icon={FolderKanban} label="Enrolled Cases" value={cases.length} sub="Cases assigned to you" color="text-navy" />
          <StatCard icon={CheckCircle}  label="Active"      value={activeCases}   sub="Currently running" color="text-emerald-600" />
          <StatCard icon={AlertCircle}  label="Pending"     value={pendingCases}  sub="Awaiting action"   color="text-amber-600" />
          <StatCard icon={Sparkles}     label="AI Analyses" value="—"             sub="Across your cases"  color="text-violet-600" />
        </div>

        {/* Cases Section */}
        <div>
          <div className="mb-6 flex items-center justify-between">
            <h2 className="font-heading text-xl font-bold text-slate-800">My Enrolled Cases</h2>
            <span className="text-sm text-slate-400">{cases.length} case{cases.length !== 1 ? 's' : ''}</span>
          </div>

          {cases.length === 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-white py-20 text-center"
            >
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-navy/10 text-navy mb-4">
                <FolderKanban size={28} />
              </div>
              <h3 className="text-lg font-semibold text-slate-800">No cases assigned yet</h3>
              <p className="mt-2 max-w-sm text-sm text-slate-500">
                Your administrator will enroll you in cases and allocate documents for you to review and summarize.
              </p>
            </motion.div>
          ) : (
            <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {cases.map((c, i) => <CaseCard key={c.id} c={c} index={i} />)}
            </div>
          )}
        </div>

        {/* Quick Links */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mt-10 rounded-2xl bg-gradient-to-r from-navy to-blue-800 p-6 text-white"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h3 className="font-heading text-lg font-bold">Quick AI Summarizer</h3>
              <p className="mt-1 text-sm text-blue-200">
                Need a one-off summary? Use the standalone AI Summarizer without a case context.
              </p>
            </div>
            <Link
              to="/summarizer"
              className="inline-flex items-center gap-2 rounded-xl bg-white/15 px-5 py-2.5 text-sm font-semibold hover:bg-white/25 transition-colors shrink-0"
            >
              <Sparkles size={16} /> Open Summarizer <ArrowRight size={16} />
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
