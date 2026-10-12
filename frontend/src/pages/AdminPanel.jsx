import { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Shield, FolderKanban, Users, FileText, Sparkles, Plus,
  Scale, ChevronRight, Loader2, AlertCircle, CheckCircle,
  Upload, Trash2, UserPlus, ArrowRight, Clock, Search,
  BarChart3, X, Eye, ChevronDown
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { adminApi } from '../services/api';
import Modal from '../components/Modal';

const STATUS_CONFIG = {
  active:   { label: 'Active',   color: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-400' },
  pending:  { label: 'Pending',  color: 'bg-amber-100 text-amber-700',     dot: 'bg-amber-400' },
  closed:   { label: 'Closed',   color: 'bg-slate-100 text-slate-600',     dot: 'bg-slate-400' },
  disposed: { label: 'Disposed', color: 'bg-red-100 text-red-600',         dot: 'bg-red-400' },
  default:  { label: 'Unknown',  color: 'bg-slate-100 text-slate-500',     dot: 'bg-slate-300' },
};

const COURT_LEVELS = ['District', 'High Court', 'Supreme Court', 'Subordinate', 'Tribunal'];
const STAGES = ['Filing', 'Notice', 'Arguments', 'Evidence', 'Judgment', 'Appeal'];

const TABS = [
  { id: 'overview',   label: 'Overview',     icon: BarChart3 },
  { id: 'cases',      label: 'Cases',        icon: FolderKanban },
  { id: 'advocates',  label: 'Advocates',    icon: Users },
  { id: 'documents',  label: 'Documents',    icon: FileText },
];

/* ───── Stat Card ───── */
function StatCard({ icon: Icon, label, value, gradient }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      className="relative overflow-hidden rounded-2xl border border-slate-100 bg-white p-6 shadow-sm hover:shadow-md transition-all"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-1 text-3xl font-bold text-slate-900">{value}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br ${gradient} text-white shadow-sm`}>
          <Icon size={22} />
        </div>
      </div>
    </motion.div>
  );
}

/* ───── Main Admin Panel ───── */
export default function AdminPanel() {
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();

  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [cases, setCases] = useState([]);
  const [advocates, setAdvocates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');

  // Modals
  const [showNewCase, setShowNewCase] = useState(false);
  const [showEnroll, setShowEnroll] = useState(null); // case_id
  const [showAllocate, setShowAllocate] = useState(null); // case_id
  const [selectedCase, setSelectedCase] = useState(null); // for case detail panel

  // Form states
  const [caseForm, setCaseForm] = useState({
    case_number: '', court_name: '', court_level: 'District',
    stage: 'Filing', status: 'active', description: '',
  });
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState('');

  const [enrollId, setEnrollId] = useState('');
  const [enrolling, setEnrolling] = useState(false);
  const [enrollError, setEnrollError] = useState('');
  const [enrollSuccess, setEnrollSuccess] = useState('');

  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadSuccess, setUploadSuccess] = useState('');
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return; }
    if (user?.role !== 'admin') { navigate('/dashboard'); return; }
    loadData();
  }, [isAuthenticated, user, navigate]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [statsRes, casesRes, advocatesRes] = await Promise.all([
        adminApi.getStats(),
        adminApi.listCases(),
        adminApi.listAdvocates(),
      ]);
      setStats(statsRes.data);
      setCases(casesRes.data || []);
      setAdvocates(advocatesRes.data || []);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  // ── Case Creation ──
  const handleCreateCase = async (e) => {
    e.preventDefault();
    setCreating(true);
    setCreateError('');
    try {
      await adminApi.createCase(caseForm);
      setCaseForm({ case_number: '', court_name: '', court_level: 'District', stage: 'Filing', status: 'active', description: '' });
      setShowNewCase(false);
      await loadData();
    } catch (err) {
      setCreateError(err?.response?.data?.detail || 'Failed to create case.');
    } finally {
      setCreating(false);
    }
  };

  // ── Advocate Enrollment ──
  const handleEnroll = async (e) => {
    e.preventDefault();
    setEnrolling(true);
    setEnrollError('');
    setEnrollSuccess('');
    try {
      const res = await adminApi.enrollAdvocate(showEnroll, enrollId);
      setEnrollSuccess(res.data.message);
      setEnrollId('');
      await loadData();
    } catch (err) {
      setEnrollError(err?.response?.data?.detail || 'Failed to enroll advocate.');
    } finally {
      setEnrolling(false);
    }
  };

  const handleRemoveMember = async (caseId, memberId) => {
    try {
      await adminApi.removeMember(caseId, memberId);
      await loadData();
      if (selectedCase) {
        const updated = await adminApi.getCase(caseId);
        setSelectedCase(updated.data);
      }
    } catch (err) {
      console.error('Failed to remove member:', err);
    }
  };

  // ── Document Allocation ──
  const handleAllocateDocument = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadError('');
    setUploadSuccess('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      await adminApi.allocateDocument(showAllocate, formData);
      setUploadSuccess(`"${file.name}" allocated successfully!`);
      await loadData();
    } catch (err) {
      setUploadError(err?.response?.data?.detail || 'Failed to allocate document.');
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  // ── View Case Detail ──
  const handleViewCase = async (caseId) => {
    try {
      const res = await adminApi.getCase(caseId);
      setSelectedCase(res.data);
    } catch (err) {
      console.error('Failed to load case details:', err);
    }
  };

  // Filtered cases for search
  const filteredCases = cases.filter(c =>
    c.case_number?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.court_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={32} className="animate-spin text-navy" />
          <p className="text-sm text-slate-500">Loading admin panel…</p>
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
          className="mb-8"
        >
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <Shield size={16} className="text-amber-500" />
                <span className="text-xs font-semibold uppercase tracking-widest text-amber-600">Admin Panel</span>
              </div>
              <h1 className="font-heading text-3xl font-bold text-navy sm:text-4xl">
                Administration
              </h1>
              <p className="mt-1 text-sm text-slate-500">
                Manage cases, enroll advocates, and allocate documents
              </p>
            </div>
            <motion.button
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              onClick={() => setShowNewCase(true)}
              className="inline-flex items-center gap-2 rounded-xl bg-navy px-5 py-3 text-sm font-bold text-white shadow-md shadow-navy/20 hover:bg-[#16304d] transition-colors"
            >
              <Plus size={18} />
              Create Case
            </motion.button>
          </div>

          {/* Tab Bar */}
          <div className="mt-6 flex gap-1 rounded-2xl bg-slate-100 p-1 w-fit">
            {TABS.map(tab => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all ${
                    isActive
                      ? 'bg-white text-navy shadow-sm'
                      : 'text-slate-400 hover:text-slate-700 hover:bg-white/50'
                  }`}
                >
                  <Icon size={15} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </motion.div>

        {/* ── TAB CONTENT ── */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >

            {/* ══════ OVERVIEW TAB ══════ */}
            {activeTab === 'overview' && (
              <div className="space-y-8">
                {/* Stats */}
                <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                  <StatCard icon={FolderKanban} label="Total Cases" value={stats?.total_cases || 0} gradient="from-navy to-blue-800" />
                  <StatCard icon={Users} label="Advocates" value={stats?.total_advocates || 0} gradient="from-violet-600 to-indigo-700" />
                  <StatCard icon={FileText} label="Documents" value={stats?.total_documents || 0} gradient="from-emerald-600 to-teal-700" />
                  <StatCard icon={Sparkles} label="AI Runs" value={stats?.total_ai_runs || 0} gradient="from-amber-500 to-orange-600" />
                </div>

                {/* Recent Cases */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
                    <h2 className="font-heading text-lg font-bold text-slate-800">Recent Cases</h2>
                    <button
                      onClick={() => setActiveTab('cases')}
                      className="text-sm font-medium text-navy hover:underline inline-flex items-center gap-1"
                    >
                      View all <ChevronRight size={14} />
                    </button>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {cases.slice(0, 5).map(c => {
                      const st = STATUS_CONFIG[c.status] || STATUS_CONFIG.default;
                      return (
                        <div
                          key={c.id}
                          className="flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition cursor-pointer"
                          onClick={() => handleViewCase(c.id)}
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-navy/10 text-navy">
                              <Scale size={16} />
                            </div>
                            <div className="min-w-0">
                              <p className="font-semibold text-slate-800 truncate">{c.case_number}</p>
                              <p className="text-xs text-slate-500">{c.court_name} • {c.member_count || 0} members • {c.document_count || 0} docs</p>
                            </div>
                          </div>
                          <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${st.color}`}>
                            <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
                            {st.label}
                          </span>
                        </div>
                      );
                    })}
                    {cases.length === 0 && (
                      <div className="px-6 py-10 text-center">
                        <p className="text-sm text-slate-400">No cases yet. Create your first case to get started.</p>
                      </div>
                    )}
                  </div>
                </div>

                {/* Advocates */}
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
                    <h2 className="font-heading text-lg font-bold text-slate-800">Registered Advocates</h2>
                    <button
                      onClick={() => setActiveTab('advocates')}
                      className="text-sm font-medium text-navy hover:underline inline-flex items-center gap-1"
                    >
                      View all <ChevronRight size={14} />
                    </button>
                  </div>
                  <div className="divide-y divide-slate-100">
                    {advocates.slice(0, 5).map(a => (
                      <div key={a.id} className="flex items-center justify-between px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700 font-bold text-sm">
                            {(a.full_name || '?')[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-800">{a.full_name || 'Unnamed'}</p>
                            <p className="text-xs text-slate-500">{a.phone || 'No phone'}</p>
                          </div>
                        </div>
                        <span className="rounded-full bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700">
                          Advocate
                        </span>
                      </div>
                    ))}
                    {advocates.length === 0 && (
                      <div className="px-6 py-10 text-center">
                        <p className="text-sm text-slate-400">No advocates registered yet.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* ══════ CASES TAB ══════ */}
            {activeTab === 'cases' && (
              <div className="space-y-6">
                {/* Search + Actions Bar */}
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="relative flex-1 max-w-md">
                    <Search size={16} className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" />
                    <input
                      value={searchQuery}
                      onChange={e => setSearchQuery(e.target.value)}
                      placeholder="Search cases by number, court, or description…"
                      className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                    />
                  </div>
                  <button
                    onClick={() => setShowNewCase(true)}
                    className="inline-flex items-center gap-2 rounded-xl bg-navy px-4 py-2.5 text-sm font-bold text-white hover:bg-[#16304d] transition shadow-sm"
                  >
                    <Plus size={15} /> New Case
                  </button>
                </div>

                {/* Cases Grid */}
                {filteredCases.length === 0 ? (
                  <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-white py-20 text-center">
                    <FolderKanban size={28} className="text-slate-300 mb-3" />
                    <h3 className="text-lg font-semibold text-slate-700">No cases found</h3>
                    <p className="mt-1 text-sm text-slate-400">
                      {searchQuery ? 'Try a different search term.' : 'Create your first case to get started.'}
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {filteredCases.map((c, i) => {
                      const st = STATUS_CONFIG[c.status] || STATUS_CONFIG.default;
                      return (
                        <motion.div
                          key={c.id}
                          initial={{ opacity: 0, y: 16 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: i * 0.04 }}
                          className="rounded-2xl border border-slate-200 bg-white shadow-sm hover:shadow-lg transition-all overflow-hidden group"
                        >
                          <div className="h-1.5 w-full bg-gradient-to-r from-navy to-blue-800" />
                          <div className="p-5">
                            <div className="flex items-start justify-between gap-2 mb-3">
                              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-navy/10 text-navy">
                                <Scale size={16} />
                              </div>
                              <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${st.color}`}>
                                <span className={`h-1.5 w-1.5 rounded-full ${st.dot}`} />
                                {st.label}
                              </span>
                            </div>

                            <h3 className="font-bold text-slate-900 leading-snug line-clamp-1">{c.case_number}</h3>
                            <p className="mt-1 text-xs text-slate-500 line-clamp-1">{c.court_name}</p>
                            {c.description && (
                              <p className="mt-2 text-sm text-slate-600 line-clamp-2 leading-relaxed">{c.description}</p>
                            )}

                            {/* Meta */}
                            <div className="mt-4 flex items-center gap-3 text-xs text-slate-400">
                              <span className="flex items-center gap-1"><Users size={11} /> {c.member_count || 0} members</span>
                              <span className="flex items-center gap-1"><FileText size={11} /> {c.document_count || 0} docs</span>
                            </div>

                            {/* Actions */}
                            <div className="mt-4 flex flex-wrap gap-2 border-t border-slate-100 pt-3">
                              <button
                                onClick={() => handleViewCase(c.id)}
                                className="inline-flex items-center gap-1 rounded-lg bg-slate-100 px-2.5 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-200 transition"
                              >
                                <Eye size={11} /> View
                              </button>
                              <button
                                onClick={() => { setShowEnroll(c.id); setEnrollError(''); setEnrollSuccess(''); }}
                                className="inline-flex items-center gap-1 rounded-lg bg-violet-100 px-2.5 py-1.5 text-xs font-semibold text-violet-700 hover:bg-violet-200 transition"
                              >
                                <UserPlus size={11} /> Enroll
                              </button>
                              <button
                                onClick={() => { setShowAllocate(c.id); setUploadError(''); setUploadSuccess(''); }}
                                className="inline-flex items-center gap-1 rounded-lg bg-emerald-100 px-2.5 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-200 transition"
                              >
                                <Upload size={11} /> Allocate Doc
                              </button>
                              <Link
                                to={`/cases/${c.id}`}
                                className="inline-flex items-center gap-1 rounded-lg bg-blue-100 px-2.5 py-1.5 text-xs font-semibold text-blue-700 hover:bg-blue-200 transition"
                              >
                                <Sparkles size={11} /> Workspace
                              </Link>
                            </div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                )}
              </div>
            )}

            {/* ══════ ADVOCATES TAB ══════ */}
            {activeTab === 'advocates' && (
              <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
                  <div>
                    <h2 className="font-heading text-lg font-bold text-slate-800">All Advocates</h2>
                    <p className="text-sm text-slate-500">{advocates.length} registered advocate{advocates.length !== 1 ? 's' : ''}</p>
                  </div>
                </div>

                {advocates.length === 0 ? (
                  <div className="px-6 py-16 text-center">
                    <Users size={28} className="text-slate-300 mx-auto mb-3" />
                    <h3 className="text-base font-semibold text-slate-700">No advocates registered</h3>
                    <p className="mt-1 text-sm text-slate-400">Advocates need to sign up first before they can be enrolled in cases.</p>
                  </div>
                ) : (
                  <div className="divide-y divide-slate-100">
                    {advocates.map(a => (
                      <div key={a.id} className="flex items-center justify-between px-6 py-4 hover:bg-slate-50 transition">
                        <div className="flex items-center gap-4">
                          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-600 text-white font-bold text-sm shadow-sm">
                            {(a.full_name || '?')[0].toUpperCase()}
                          </div>
                          <div>
                            <p className="font-semibold text-slate-800">{a.full_name || 'Unnamed Advocate'}</p>
                            <div className="flex items-center gap-3 mt-0.5">
                              <p className="text-xs text-slate-500">{a.phone || 'No phone'}</p>
                              <span className="text-xs text-slate-300">•</span>
                              <p className="text-xs text-slate-400">ID: {a.id?.slice(0, 8)}…</p>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                            Advocate
                          </span>
                          <button
                            onClick={() => navigator.clipboard.writeText(a.id)}
                            className="rounded-lg bg-slate-100 px-2.5 py-1.5 text-xs font-medium text-slate-600 hover:bg-slate-200 transition"
                            title="Copy advocate ID for enrollment"
                          >
                            Copy ID
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* ══════ DOCUMENTS TAB ══════ */}
            {activeTab === 'documents' && (
              <div className="space-y-6">
                <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                  <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
                    <div>
                      <h2 className="font-heading text-lg font-bold text-slate-800">Document Allocation</h2>
                      <p className="text-sm text-slate-500">Select a case below to allocate documents</p>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                      {cases.map(c => (
                        <div
                          key={c.id}
                          className="rounded-xl border border-slate-200 bg-slate-50 p-4 hover:border-navy/30 hover:bg-navy/5 transition cursor-pointer"
                          onClick={() => { setShowAllocate(c.id); setUploadError(''); setUploadSuccess(''); }}
                        >
                          <div className="flex items-center gap-3 mb-2">
                            <Scale size={16} className="text-navy" />
                            <h3 className="font-semibold text-slate-800 text-sm truncate">{c.case_number}</h3>
                          </div>
                          <p className="text-xs text-slate-500 mb-2">{c.court_name}</p>
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-slate-400">{c.document_count || 0} documents</span>
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-navy">
                              <Upload size={10} /> Allocate
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                    {cases.length === 0 && (
                      <div className="text-center py-10">
                        <p className="text-sm text-slate-400">Create a case first to allocate documents.</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

          </motion.div>
        </AnimatePresence>

        {/* ── Case Detail Slide-over ── */}
        <AnimatePresence>
          {selectedCase && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-40 bg-slate-900/40 backdrop-blur-sm"
                onClick={() => setSelectedCase(null)}
              />
              <motion.div
                initial={{ x: '100%' }}
                animate={{ x: 0 }}
                exit={{ x: '100%' }}
                transition={{ type: 'spring', damping: 30, stiffness: 300 }}
                className="fixed right-0 top-0 z-50 h-full w-full max-w-xl bg-white shadow-2xl border-l border-slate-200 overflow-y-auto"
              >
                <div className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-100 bg-white px-6 py-4">
                  <h2 className="font-heading text-lg font-bold text-slate-900">Case Details</h2>
                  <button
                    onClick={() => setSelectedCase(null)}
                    className="flex h-8 w-8 items-center justify-center rounded-full text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
                  >
                    <X size={18} />
                  </button>
                </div>

                <div className="p-6 space-y-6">
                  {/* Case Info */}
                  <div className="rounded-xl bg-gradient-to-br from-navy to-blue-800 p-5 text-white">
                    <h3 className="font-bold text-xl mb-1">{selectedCase.case?.case_number}</h3>
                    <p className="text-blue-200 text-sm">{selectedCase.case?.court_name} • {selectedCase.case?.court_level}</p>
                    {selectedCase.case?.description && (
                      <p className="mt-3 text-blue-100 text-sm leading-relaxed">{selectedCase.case.description}</p>
                    )}
                  </div>

                  {/* Members */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-heading text-base font-bold text-slate-800 flex items-center gap-2">
                        <Users size={16} className="text-violet-600" /> Enrolled Members
                      </h3>
                      <button
                        onClick={() => { setShowEnroll(selectedCase.case?.id); setEnrollError(''); setEnrollSuccess(''); }}
                        className="inline-flex items-center gap-1 rounded-lg bg-violet-100 px-2.5 py-1.5 text-xs font-semibold text-violet-700 hover:bg-violet-200 transition"
                      >
                        <UserPlus size={11} /> Enroll
                      </button>
                    </div>
                    <div className="space-y-2">
                      {(selectedCase.members || []).map(m => (
                        <div key={m.id} className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-100 px-4 py-3">
                          <div className="flex items-center gap-3">
                            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-navy/10 text-navy font-bold text-xs">
                              {(m.user?.full_name || '?')[0].toUpperCase()}
                            </div>
                            <div>
                              <p className="font-medium text-slate-800 text-sm">{m.user?.full_name || m.user?.username || 'Unknown'}</p>
                              <p className="text-xs text-slate-400 capitalize">{m.role}</p>
                            </div>
                          </div>
                          {m.role !== 'owner' && (
                            <button
                              onClick={() => handleRemoveMember(selectedCase.case?.id, m.id)}
                              className="text-red-400 hover:text-red-600 transition"
                              title="Remove from case"
                            >
                              <Trash2 size={14} />
                            </button>
                          )}
                        </div>
                      ))}
                      {(selectedCase.members || []).length === 0 && (
                        <p className="text-sm text-slate-400 text-center py-4">No members enrolled.</p>
                      )}
                    </div>
                  </div>

                  {/* Documents */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-heading text-base font-bold text-slate-800 flex items-center gap-2">
                        <FileText size={16} className="text-emerald-600" /> Allocated Documents
                      </h3>
                      <button
                        onClick={() => { setShowAllocate(selectedCase.case?.id); setUploadError(''); setUploadSuccess(''); }}
                        className="inline-flex items-center gap-1 rounded-lg bg-emerald-100 px-2.5 py-1.5 text-xs font-semibold text-emerald-700 hover:bg-emerald-200 transition"
                      >
                        <Upload size={11} /> Allocate
                      </button>
                    </div>
                    <div className="space-y-2">
                      {(selectedCase.documents || []).map(doc => {
                        const ext = doc.file_type?.replace('.', '').toUpperCase() || 'DOC';
                        return (
                          <div key={doc.id} className="flex items-center justify-between rounded-xl bg-slate-50 border border-slate-100 px-4 py-3">
                            <div className="flex items-center gap-3">
                              <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg font-bold text-xs ${
                                ext === 'PDF' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
                              }`}>
                                {ext}
                              </div>
                              <div>
                                <p className="font-medium text-slate-800 text-sm truncate max-w-[200px]">{doc.file_name}</p>
                                <p className="text-xs text-slate-400">
                                  {doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : ''} •{' '}
                                  <span className={doc.processing_status === 'completed' ? 'text-emerald-600' : 'text-amber-600'}>
                                    {doc.processing_status}
                                  </span>
                                </p>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                      {(selectedCase.documents || []).length === 0 && (
                        <p className="text-sm text-slate-400 text-center py-4">No documents allocated yet.</p>
                      )}
                    </div>
                  </div>

                  {/* AI Runs */}
                  {(selectedCase.ai_runs || []).length > 0 && (
                    <div>
                      <h3 className="font-heading text-base font-bold text-slate-800 flex items-center gap-2 mb-3">
                        <Sparkles size={16} className="text-amber-500" /> AI Summaries
                      </h3>
                      <div className="space-y-2">
                        {selectedCase.ai_runs.map(run => (
                          <div key={run.id} className="rounded-xl bg-slate-50 border border-slate-100 px-4 py-3">
                            <div className="flex items-center justify-between mb-2">
                              <span className="text-xs font-semibold text-violet-700 uppercase">{run.operation}</span>
                              <span className={`text-xs font-bold ${run.status === 'completed' ? 'text-emerald-600' : 'text-amber-600'}`}>
                                {run.status}
                              </span>
                            </div>
                            {run.result && (
                              <p className="text-sm text-slate-600 line-clamp-3 leading-relaxed">{run.result}</p>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Go to workspace */}
                  <Link
                    to={`/cases/${selectedCase.case?.id}`}
                    className="flex items-center justify-center gap-2 rounded-xl bg-navy py-3 text-sm font-bold text-white hover:bg-[#16304d] transition w-full"
                  >
                    Open Full Workspace <ArrowRight size={15} />
                  </Link>
                </div>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* ── Create Case Modal ── */}
        <Modal isOpen={showNewCase} onClose={() => { setShowNewCase(false); setCreateError(''); }} title="Create New Case">
          <form onSubmit={handleCreateCase} className="space-y-4">
            {createError && (
              <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
                <AlertCircle size={15} className="shrink-0" /> {createError}
              </div>
            )}
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Case Number <span className="text-red-500">*</span></label>
              <input
                required value={caseForm.case_number}
                onChange={e => setCaseForm(p => ({ ...p, case_number: e.target.value }))}
                placeholder="e.g. C.C. No. 1245/2025"
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Court Name <span className="text-red-500">*</span></label>
              <input
                required value={caseForm.court_name}
                onChange={e => setCaseForm(p => ({ ...p, court_name: e.target.value }))}
                placeholder="e.g. Judicial Magistrate Court, Chennai"
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Court Level</label>
                <select
                  value={caseForm.court_level}
                  onChange={e => setCaseForm(p => ({ ...p, court_level: e.target.value }))}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                >
                  {COURT_LEVELS.map(l => <option key={l}>{l}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1.5">Stage</label>
                <select
                  value={caseForm.stage}
                  onChange={e => setCaseForm(p => ({ ...p, stage: e.target.value }))}
                  className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                >
                  {STAGES.map(s => <option key={s}>{s}</option>)}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Status</label>
              <div className="flex gap-2">
                {['active', 'pending', 'closed'].map(s => (
                  <button
                    type="button" key={s}
                    onClick={() => setCaseForm(p => ({ ...p, status: s }))}
                    className={`flex-1 rounded-xl py-2 text-xs font-semibold capitalize transition border ${
                      caseForm.status === s ? 'bg-navy text-white border-navy' : 'bg-white text-slate-600 border-slate-200 hover:border-slate-300'
                    }`}
                  >{s}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-1.5">Description</label>
              <textarea
                value={caseForm.description}
                onChange={e => setCaseForm(p => ({ ...p, description: e.target.value }))}
                placeholder="Brief description of the case…"
                rows={3}
                className="w-full rounded-xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm text-slate-800 placeholder:text-slate-400 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition resize-none"
              />
            </div>
            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => { setShowNewCase(false); setCreateError(''); }}
                className="flex-1 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
              >Cancel</button>
              <button
                type="submit" disabled={creating}
                className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-navy py-2.5 text-sm font-bold text-white hover:bg-[#16304d] disabled:opacity-60 transition"
              >
                {creating ? <><Loader2 size={15} className="animate-spin" /> Creating…</> : <><Plus size={15} /> Create Case</>}
              </button>
            </div>
          </form>
        </Modal>

        {/* ── Enroll Advocate Modal ── */}
        <Modal isOpen={!!showEnroll} onClose={() => { setShowEnroll(null); setEnrollError(''); setEnrollSuccess(''); }} title="Enroll Advocate in Case">
          <form onSubmit={handleEnroll} className="space-y-4">
            {enrollError && (
              <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
                <AlertCircle size={15} className="shrink-0" /> {enrollError}
              </div>
            )}
            {enrollSuccess && (
              <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700 border border-emerald-100">
                <CheckCircle size={15} className="shrink-0" /> {enrollSuccess}
              </div>
            )}

            <div className="rounded-xl bg-slate-50 border border-slate-100 p-4">
              <p className="text-xs font-medium text-slate-500 mb-2">Select an advocate to enroll:</p>
              {advocates.length === 0 ? (
                <p className="text-sm text-slate-400">No advocates available.</p>
              ) : (
                <div className="space-y-2 max-h-52 overflow-y-auto">
                  {advocates.map(a => (
                    <div
                      key={a.id}
                      onClick={() => setEnrollId(a.id)}
                      className={`flex items-center gap-3 rounded-xl border p-3 cursor-pointer transition ${
                        enrollId === a.id
                          ? 'border-navy/40 bg-navy/5'
                          : 'border-slate-200 bg-white hover:border-slate-300'
                      }`}
                    >
                      <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-100 text-violet-700 font-bold text-xs">
                        {(a.full_name || '?')[0].toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="font-medium text-slate-800 text-sm truncate">{a.full_name || 'Unnamed'}</p>
                        <p className="text-xs text-slate-400">{a.phone || 'No phone'}</p>
                      </div>
                      {enrollId === a.id && <CheckCircle size={14} className="text-navy shrink-0 ml-auto" />}
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex gap-3 pt-2">
              <button
                type="button"
                onClick={() => { setShowEnroll(null); setEnrollError(''); setEnrollSuccess(''); }}
                className="flex-1 rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
              >Cancel</button>
              <button
                type="submit" disabled={enrolling || !enrollId}
                className="flex-1 inline-flex items-center justify-center gap-2 rounded-xl bg-violet-600 py-2.5 text-sm font-bold text-white hover:bg-violet-700 disabled:opacity-50 transition"
              >
                {enrolling ? <><Loader2 size={15} className="animate-spin" /> Enrolling…</> : <><UserPlus size={15} /> Enroll Advocate</>}
              </button>
            </div>
          </form>
        </Modal>

        {/* ── Allocate Document Modal ── */}
        <Modal isOpen={!!showAllocate} onClose={() => { setShowAllocate(null); setUploadError(''); setUploadSuccess(''); }} title="Allocate Document to Case">
          <div className="space-y-4">
            {uploadError && (
              <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
                <AlertCircle size={15} className="shrink-0" /> {uploadError}
              </div>
            )}
            {uploadSuccess && (
              <div className="flex items-center gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-sm text-emerald-700 border border-emerald-100">
                <CheckCircle size={15} className="shrink-0" /> {uploadSuccess}
              </div>
            )}

            <div
              className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 py-12 text-center cursor-pointer hover:border-navy/30 hover:bg-navy/5 transition"
              onClick={() => fileInputRef.current?.click()}
            >
              {uploading ? (
                <div className="flex flex-col items-center gap-3">
                  <Loader2 size={28} className="animate-spin text-navy" />
                  <p className="text-sm font-medium text-slate-600">Processing document…</p>
                </div>
              ) : (
                <>
                  <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-100 text-emerald-600 mb-4">
                    <Upload size={24} />
                  </div>
                  <h3 className="text-base font-semibold text-slate-700">Click to upload a document</h3>
                  <p className="mt-1 text-sm text-slate-400">PDF or DOCX — will be processed and allocated to this case</p>
                </>
              )}
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleAllocateDocument}
              className="hidden"
              accept=".pdf,.docx"
            />

            <button
              onClick={() => { setShowAllocate(null); setUploadError(''); setUploadSuccess(''); }}
              className="w-full rounded-xl border border-slate-200 bg-white py-2.5 text-sm font-semibold text-slate-700 hover:bg-slate-50 transition"
            >
              Close
            </button>
          </div>
        </Modal>

      </div>
    </div>
  );
}
