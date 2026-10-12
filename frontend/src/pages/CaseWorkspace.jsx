import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Scale, ArrowLeft, FileText, Sparkles, Info, Upload,
  Loader2, CheckCircle, XCircle, Clock, Download,
  AlertCircle, ChevronDown, Globe, Copy, RefreshCw, Users, Gavel
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api, { exportSummary } from '../services/api';

const LANGUAGES = [
  { code: 'en', label: 'English' },
  { code: 'ta', label: 'Tamil' },
  { code: 'hi', label: 'Hindi' },
  { code: 'te', label: 'Telugu' },
  { code: 'kn', label: 'Kannada' },
  { code: 'ml', label: 'Malayalam' },
  { code: 'mr', label: 'Marathi' },
];

const TAB_CONFIG = [
  { id: 'overview',   label: 'Overview',     icon: Info },
  { id: 'documents',  label: 'Documents',    icon: FileText },
  { id: 'ai',         label: 'AI Workspace', icon: Sparkles },
];

const STATUS_CONFIG = {
  active:   { label: 'Active',   color: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' },
  pending:  { label: 'Pending',  color: 'bg-amber-100 text-amber-700',     dot: 'bg-amber-500' },
  closed:   { label: 'Closed',   color: 'bg-slate-100 text-slate-600',     dot: 'bg-slate-400' },
  default:  { label: 'Unknown',  color: 'bg-slate-100 text-slate-500',     dot: 'bg-slate-300' },
};

const DOC_STATUS_CONFIG = {
  completed:  { icon: CheckCircle, color: 'text-emerald-600', bg: 'bg-emerald-50', label: 'Ready' },
  processing: { icon: Loader2,     color: 'text-blue-600',    bg: 'bg-blue-50',    label: 'Processing', spin: true },
  failed:     { icon: XCircle,     color: 'text-red-600',     bg: 'bg-red-50',     label: 'Failed' },
  default:    { icon: Clock,       color: 'text-slate-500',   bg: 'bg-slate-50',   label: 'Pending' },
};

function TabButton({ tab, activeTab, onClick }) {
  const Icon = tab.icon;
  const isActive = activeTab === tab.id;
  return (
    <button
      onClick={() => onClick(tab.id)}
      className={`relative flex items-center gap-2 rounded-xl px-4 py-2.5 text-sm font-semibold transition-all duration-200 ${
        isActive
          ? 'bg-white text-navy shadow-sm'
          : 'text-slate-400 hover:text-slate-700 hover:bg-white/50'
      }`}
    >
      <Icon size={15} />
      {tab.label}
    </button>
  );
}

function DocumentRow({ doc, onSelect, selectedId }) {
  const ext = doc.file_type?.replace('.', '').toUpperCase() || 'DOC';
  const cfg = DOC_STATUS_CONFIG[doc.processing_status] || DOC_STATUS_CONFIG.default;
  const StatusIcon = cfg.icon;
  const isSelected = selectedId === doc.id;
  const sizeKB = doc.file_size ? `${(doc.file_size / 1024).toFixed(1)} KB` : '';

  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      className={`flex items-center justify-between gap-4 rounded-xl border p-4 transition-all cursor-pointer ${
        isSelected ? 'border-navy/30 bg-navy/5' : 'border-slate-200 bg-white hover:border-slate-300 hover:shadow-sm'
      }`}
      onClick={() => onSelect && onSelect(doc)}
    >
      <div className="flex items-center gap-3 min-w-0">
        <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl font-bold text-xs ${
          ext === 'PDF' ? 'bg-red-100 text-red-600' : 'bg-blue-100 text-blue-600'
        }`}>
          {ext}
        </div>
        <div className="min-w-0">
          <p className="font-semibold text-slate-800 truncate">{doc.file_name}</p>
          <p className="text-xs text-slate-400">{sizeKB}</p>
        </div>
      </div>
      <div className={`inline-flex shrink-0 items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${cfg.bg} ${cfg.color}`}>
        <StatusIcon size={12} className={cfg.spin ? 'animate-spin' : ''} />
        {cfg.label}
      </div>
    </motion.div>
  );
}

function AIRunCard({ run, onExport }) {
  const [expanded, setExpanded] = useState(true);
  const [copying, setCopying] = useState(false);

  // Support both old Supabase format (run.result / run.status) and new local DB format (run.summary)
  const content = run.summary || run.result || '';
  const docName = run.document_name || run.documents?.file_name || 'Document';
  const langLabel = run.language || run.target_language || 'en';
  const isCompleted = !run.status || run.status === 'completed';

  const handleCopy = async () => {
    if (!content) return;
    await navigator.clipboard.writeText(content);
    setCopying(true);
    setTimeout(() => setCopying(false), 2000);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-2xl border border-slate-200 bg-white overflow-hidden shadow-sm"
    >
      <div className="flex items-center justify-between gap-3 p-4 bg-slate-50 border-b border-slate-100">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="rounded-lg bg-violet-100 px-2.5 py-1 text-xs font-bold text-violet-700 uppercase tracking-wider">
            Summarize
          </span>
          <span className="text-sm text-slate-500">{docName}</span>
          {langLabel && (
            <span className="rounded-full bg-blue-50 border border-blue-100 px-2 py-0.5 text-[11px] font-semibold text-blue-600 uppercase">
              {langLabel}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-bold px-2.5 py-1 rounded-full ${
            isCompleted ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
          }`}>
            {isCompleted ? 'completed' : (run.status || 'pending')}
          </span>
          <button
            onClick={() => setExpanded(e => !e)}
            className="flex h-7 w-7 items-center justify-center rounded-lg hover:bg-slate-200 transition"
          >
            <ChevronDown size={14} className={`text-slate-500 transition-transform ${expanded ? 'rotate-180' : ''}`} />
          </button>
        </div>
      </div>

      <AnimatePresence>
        {expanded && content && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            <div className="p-4">
              <div className="relative rounded-xl bg-slate-50 border border-slate-100 p-4 max-h-80 overflow-y-auto">
                <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{content}</p>
              </div>
              <div className="mt-3 flex flex-wrap gap-2">
                <button
                  onClick={handleCopy}
                  className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition"
                >
                  <Copy size={12} />
                  {copying ? 'Copied!' : 'Copy'}
                </button>
                {['pdf', 'docx', 'txt'].map(fmt => (
                  <button
                    key={fmt}
                    onClick={() => onExport && onExport({...run, result: content}, fmt)}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-50 transition"
                  >
                    <Download size={12} />
                    {fmt.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export default function CaseWorkspace() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuth();
  const isAdmin = user?.role === 'admin';

  const [activeTab, setActiveTab] = useState('overview');
  const [caseData, setCaseData] = useState(null);
  const [parties, setParties] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [aiRuns, setAiRuns] = useState([]);

  const [selectedDoc, setSelectedDoc] = useState(null);
  const [targetLang, setTargetLang] = useState('en');
  const [isSummarizing, setIsSummarizing] = useState(false);
  const [summarizeError, setSummarizeError] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [exportingRun, setExportingRun] = useState(null);

  const fileInputRef = useRef(null);

  useEffect(() => {
    if (!isAuthenticated) { navigate('/login'); return; }

    api.get(`/cases/${id}`)
      .then(res => {
        setCaseData(res.data.case);
        setDocuments(res.data.documents || []);
        setParties(res.data.parties || []);
      })
      .catch(err => console.error('Failed to load case:', err));

    fetchAiRuns();
  }, [id, isAuthenticated, navigate]);

  const fetchAiRuns = () => {
    api.get(`/cases/${id}/ai`)
      .then(res => setAiRuns(Array.isArray(res.data) ? res.data : []))
      .catch(err => console.error('Failed to load AI runs:', err));
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setUploading(true);
    setUploadError('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await api.post(`/cases/${id}/documents`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setDocuments(prev => [...prev, res.data]);
    } catch (err) {
      setUploadError(err?.response?.data?.detail || 'Upload failed. Please try again.');
    } finally {
      setUploading(false);
      e.target.value = null;
    }
  };

  const handleSummarize = async () => {
    if (!selectedDoc) return;
    setIsSummarizing(true);
    setSummarizeError('');

    const formData = new FormData();
    formData.append('document_id', selectedDoc.id);
    formData.append('target_language', targetLang);

    try {
      await api.post(`/cases/${id}/ai/summarize`, formData);
      await fetchAiRuns();
    } catch (err) {
      setSummarizeError(err?.response?.data?.detail || 'Summarization failed. Please try again.');
    } finally {
      setIsSummarizing(false);
    }
  };

  const handleExport = async (run, format) => {
    setExportingRun(`${run.id}-${format}`);
    const payload = {
      filename: run.documents?.file_name || 'summary',
      summary: run.result,
      language: targetLang,
      processing_time: '0s',
    };
    try {
      await exportSummary(format, payload);
    } catch (err) {
      console.error('Export failed', err);
    } finally {
      setExportingRun(null);
    }
  };

  if (!caseData) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 size={32} className="animate-spin text-navy" />
          <p className="text-sm text-slate-500">Loading workspace…</p>
        </div>
      </div>
    );
  }

  const status = STATUS_CONFIG[caseData.status] || STATUS_CONFIG.default;
  const completedDocs = documents.filter(d => d.processing_status === 'completed');

  return (
    <div className="min-h-screen bg-slatebg">
      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">

        {/* Back breadcrumb */}
        <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="mb-6">
          <Link to="/dashboard" className="inline-flex items-center gap-2 text-sm font-medium text-slate-500 hover:text-navy transition-colors">
            <ArrowLeft size={15} /> Back to Dashboard
          </Link>
        </motion.div>

        {/* Case Header */}
        <motion.div
          initial={{ opacity: 0, y: -12 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 overflow-hidden rounded-2xl bg-gradient-to-br from-navy to-blue-900 p-8 text-white shadow-xl shadow-navy/20"
        >
          <div className="flex flex-col gap-6 sm:flex-row sm:items-start sm:justify-between">
            <div className="flex items-start gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-white/15">
                <Scale size={24} />
              </div>
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold bg-white/20 text-white`}>
                    <span className={`h-1.5 w-1.5 rounded-full ${status.dot}`} />
                    {status.label}
                  </span>
                  {caseData.stage && (
                    <span className="rounded-full bg-white/15 px-2.5 py-1 text-xs font-medium text-blue-200">
                      {caseData.stage}
                    </span>
                  )}
                </div>
                <h1 className="font-heading text-2xl font-bold sm:text-3xl">{caseData.case_number}</h1>
                <p className="mt-1 text-blue-200 text-sm">{caseData.court_name} • {caseData.court_level}</p>
                {caseData.description && (
                  <p className="mt-3 max-w-xl text-sm text-blue-100 leading-relaxed">{caseData.description}</p>
                )}
              </div>
            </div>

            {/* Quick stats */}
            <div className="flex gap-4 shrink-0">
              <div className="text-center">
                <p className="text-2xl font-bold">{documents.length}</p>
                <p className="text-xs text-blue-200">Documents</p>
              </div>
              <div className="w-px bg-white/20" />
              <div className="text-center">
                <p className="text-2xl font-bold">{aiRuns.length}</p>
                <p className="text-xs text-blue-200">AI Runs</p>
              </div>
              <div className="w-px bg-white/20" />
              <div className="text-center">
                <p className="text-2xl font-bold">{parties.length}</p>
                <p className="text-xs text-blue-200">Parties</p>
              </div>
            </div>
          </div>

          {/* Tab Bar */}
          <div className="mt-6 flex gap-1 rounded-2xl bg-white/10 p-1 w-fit">
            {TAB_CONFIG.map(tab => (
              <TabButton key={tab.id} tab={tab} activeTab={activeTab} onClick={setActiveTab} />
            ))}
          </div>
        </motion.div>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={activeTab}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >

            {/* ── OVERVIEW TAB ── */}
            {activeTab === 'overview' && (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
                {/* Case Details */}
                <div className="lg:col-span-2 space-y-6">
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h2 className="font-heading text-lg font-bold text-slate-800 mb-5 flex items-center gap-2">
                      <Info size={18} className="text-navy" /> Case Details
                    </h2>
                    <div className="grid grid-cols-2 gap-4">
                      {[
                        { label: 'Case Number',  value: caseData.case_number },
                        { label: 'Court',        value: caseData.court_name },
                        { label: 'Court Level',  value: caseData.court_level || '—' },
                        { label: 'Status',       value: caseData.status },
                        { label: 'Stage',        value: caseData.stage || '—' },
                        { label: 'Case ID',      value: caseData.id?.slice(0,8) + '…' },
                      ].map(({ label, value }) => (
                        <div key={label} className="rounded-xl bg-slate-50 p-4">
                          <p className="text-xs font-medium text-slate-400 mb-1">{label}</p>
                          <p className="font-semibold text-slate-800 truncate">{value}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Parties */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h2 className="font-heading text-lg font-bold text-slate-800 mb-4 flex items-center gap-2">
                      <Users size={18} className="text-navy" /> Parties
                    </h2>
                    {parties.length === 0 ? (
                      <div className="flex flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 py-10 text-center">
                        <Users size={22} className="text-slate-300 mb-2" />
                        <p className="text-sm text-slate-400">No parties assigned to this case yet.</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {parties.map((p, i) => (
                          <div key={i} className="flex items-center gap-3 rounded-xl border border-slate-100 bg-slate-50 p-3">
                            <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-navy/10 text-navy font-bold text-sm">
                              {(p.parties?.name || p.name || '?')[0].toUpperCase()}
                            </div>
                            <div>
                              <p className="font-semibold text-slate-800 text-sm">{p.parties?.name || p.name}</p>
                              <p className="text-xs text-slate-500">{p.role}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>

                {/* Sidebar */}
                <div className="space-y-6">
                  {/* Quick Actions */}
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h2 className="font-heading text-base font-bold text-slate-800 mb-4">Quick Actions</h2>
                    <div className="space-y-2">
                      <button
                        onClick={() => setActiveTab('documents')}
                        className="flex w-full items-center gap-3 rounded-xl bg-slate-50 border border-slate-200 px-4 py-3 text-sm font-medium text-slate-700 hover:bg-slate-100 transition text-left"
                      >
                        <FileText size={15} className="text-navy" /> {isAdmin ? 'Allocate Document' : 'View Case Documents'}
                      </button>
                      <button
                        onClick={() => setActiveTab('ai')}
                        className="flex w-full items-center gap-3 rounded-xl bg-violet-50 border border-violet-100 px-4 py-3 text-sm font-medium text-violet-700 hover:bg-violet-100 transition text-left"
                      >
                        <Sparkles size={15} /> Run AI Summarizer
                      </button>
                    </div>
                  </div>

                  {/* Recent AI runs */}
                  {aiRuns.length > 0 && (
                    <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                      <h2 className="font-heading text-base font-bold text-slate-800 mb-4 flex items-center gap-2">
                        <Sparkles size={15} className="text-violet-600" /> Recent AI Runs
                      </h2>
                      <div className="space-y-2">
                        {aiRuns.slice(0, 3).map(run => (
                          <div key={run.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
                            <p className="text-xs text-slate-600 truncate max-w-[140px]">{run.documents?.file_name}</p>
                            <span className={`text-xs font-semibold ${run.status === 'completed' ? 'text-emerald-600' : 'text-amber-600'}`}>
                              {run.status}
                            </span>
                          </div>
                        ))}
                      </div>
                      <button
                        onClick={() => setActiveTab('ai')}
                        className="mt-3 text-xs font-medium text-navy hover:underline"
                      >
                        View all →
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── DOCUMENTS TAB ── */}
            {activeTab === 'documents' && (
              <div className="rounded-2xl border border-slate-200 bg-white shadow-sm overflow-hidden">
                <div className="flex items-center justify-between gap-4 border-b border-slate-100 bg-slate-50 px-6 py-4">
                  <div>
                    <h2 className="font-heading text-lg font-bold text-slate-800">
                      {isAdmin ? 'Document Allocation' : 'Allocated Documents'}
                    </h2>
                    <p className="text-sm text-slate-500">
                      {isAdmin
                        ? `${documents.length} document${documents.length !== 1 ? 's' : ''} in this case. You can allocate new documents below.`
                        : `${documents.length} document${documents.length !== 1 ? 's' : ''} allocated by the administrator for this case.`}
                    </p>
                  </div>
                  <div>
                    {isAdmin ? (
                      <>
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          disabled={uploading}
                          className="inline-flex items-center gap-2 rounded-xl bg-navy px-4 py-2.5 text-sm font-bold text-white hover:bg-[#16304d] disabled:opacity-60 transition shadow-sm"
                        >
                          {uploading ? (
                            <><Loader2 size={15} className="animate-spin" /> Allocating…</>
                          ) : (
                            <><Upload size={15} /> Allocate Document</>
                          )}
                        </button>
                        <input type="file" ref={fileInputRef} onChange={handleFileUpload} className="hidden" accept=".pdf,.docx" />
                      </>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-3 py-1.5 text-xs font-semibold text-blue-700">
                        <CheckCircle size={13} /> Admin Managed
                      </span>
                    )}
                  </div>
                </div>

                {uploadError && (
                  <div className="mx-6 mt-4 flex items-center gap-2 rounded-xl bg-red-50 px-4 py-3 text-sm text-red-700 border border-red-100">
                    <AlertCircle size={15} className="shrink-0" /> {uploadError}
                  </div>
                )}

                <div className="p-6">
                  {documents.length === 0 ? (
                    isAdmin ? (
                      <div
                        className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 py-16 text-center cursor-pointer hover:border-navy/30 hover:bg-navy/5 transition-colors"
                        onClick={() => fileInputRef.current?.click()}
                      >
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-slate-100 text-slate-400 mb-4">
                          <Upload size={24} />
                        </div>
                        <h3 className="text-base font-semibold text-slate-700">Drop files here or click to allocate</h3>
                        <p className="mt-1 text-sm text-slate-400">Supports PDF and DOCX files for this case</p>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 py-16 text-center">
                        <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-amber-50 text-amber-500 mb-4">
                          <FileText size={24} />
                        </div>
                        <h3 className="text-base font-semibold text-slate-700">No documents allocated yet</h3>
                        <p className="mt-1 text-sm text-slate-400 max-w-sm">
                          The court administrator has not yet allocated documents to this case. Once allocated, they will appear here for you to analyze.
                        </p>
                      </div>
                    )
                  ) : (
                    <div className="space-y-3">
                      {documents.map(doc => (
                        <DocumentRow key={doc.id} doc={doc} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── AI WORKSPACE TAB ── */}
            {activeTab === 'ai' && (
              <div className="grid grid-cols-1 gap-6 lg:grid-cols-[340px_1fr]">
                {/* Left Panel: Controls */}
                <div className="space-y-4">
                  <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
                    <h2 className="font-heading text-lg font-bold text-slate-800 mb-5 flex items-center gap-2">
                      <Sparkles size={18} className="text-violet-600" /> AI Tools
                    </h2>

                    <div className="space-y-4">
                      {/* Document selector */}
                      <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1.5">
                          Select Document
                        </label>
                        {completedDocs.length === 0 ? (
                          <div className="rounded-xl border-2 border-dashed border-slate-200 p-4 text-center">
                            <p className="text-xs text-slate-400">
                              Upload and process a document first.
                            </p>
                            <button
                              onClick={() => setActiveTab('documents')}
                              className="mt-2 text-xs font-medium text-navy hover:underline"
                            >
                              Go to Documents →
                            </button>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            {completedDocs.map(doc => (
                              <div
                                key={doc.id}
                                onClick={() => setSelectedDoc(doc)}
                                className={`flex items-center gap-3 cursor-pointer rounded-xl border p-3 transition ${
                                  selectedDoc?.id === doc.id
                                    ? 'border-navy/40 bg-navy/5'
                                    : 'border-slate-200 hover:border-slate-300 bg-white'
                                }`}
                              >
                                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-emerald-100 text-emerald-600 text-xs font-bold">
                                  {doc.file_type?.replace('.', '').toUpperCase() || 'DOC'}
                                </div>
                                <p className="text-sm font-medium text-slate-700 truncate">{doc.file_name}</p>
                                {selectedDoc?.id === doc.id && (
                                  <CheckCircle size={14} className="text-navy shrink-0 ml-auto" />
                                )}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>

                      {/* Language */}
                      <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1.5 flex items-center gap-1.5">
                          <Globe size={14} /> Output Language
                        </label>
                        <select
                          value={targetLang}
                          onChange={e => setTargetLang(e.target.value)}
                          className="w-full rounded-xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm text-slate-800 focus:border-navy focus:outline-none focus:ring-2 focus:ring-navy/10 transition"
                        >
                          {LANGUAGES.map(l => (
                            <option key={l.code} value={l.code}>{l.label}</option>
                          ))}
                        </select>
                      </div>

                      {/* Operation (locked to Summarize) */}
                      <div>
                        <label className="block text-sm font-semibold text-slate-700 mb-1.5">Operation</label>
                        <div className="rounded-xl border border-violet-200 bg-violet-50 px-3 py-2.5 text-sm font-medium text-violet-700 flex items-center gap-2">
                          <Sparkles size={14} /> Summarize
                        </div>
                      </div>

                      {summarizeError && (
                        <div className="flex items-center gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-xs text-red-700 border border-red-100">
                          <AlertCircle size={13} className="shrink-0" /> {summarizeError}
                        </div>
                      )}

                      <motion.button
                        whileHover={{ scale: selectedDoc && !isSummarizing ? 1.02 : 1 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={handleSummarize}
                        disabled={!selectedDoc || isSummarizing}
                        className="w-full inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 py-3 text-sm font-bold text-white shadow-md shadow-violet-200 hover:from-violet-700 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                      >
                        {isSummarizing ? (
                          <><Loader2 size={16} className="animate-spin" /> Generating Summary…</>
                        ) : (
                          <><Sparkles size={16} /> Generate Summary</>
                        )}
                      </motion.button>
                    </div>
                  </div>
                </div>

                {/* Right Panel: AI Results */}
                <div>
                  <div className="mb-4 flex items-center justify-between">
                    <h2 className="font-heading text-lg font-bold text-slate-800">AI Results</h2>
                    {aiRuns.length > 0 && (
                      <button
                        onClick={fetchAiRuns}
                        className="inline-flex items-center gap-1.5 rounded-lg text-sm text-slate-500 hover:text-navy transition"
                      >
                        <RefreshCw size={14} /> Refresh
                      </button>
                    )}
                  </div>

                  {aiRuns.length === 0 ? (
                    <div className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-white py-16 text-center">
                      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-400 mb-4">
                        <Sparkles size={24} />
                      </div>
                      <h3 className="text-base font-semibold text-slate-700">No AI analyses yet</h3>
                      <p className="mt-1 text-sm text-slate-400 max-w-xs">
                        Select a document and run "Generate Summary" to see results here.
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {aiRuns.map(run => (
                        <AIRunCard key={run.id} run={run} onExport={handleExport} />
                      ))}
                    </div>
                  )}
                </div>
              </div>
            )}

          </motion.div>
        </AnimatePresence>
      </div>
    </div>
  );
}
