import { motion } from 'framer-motion';
import {
  ArrowRight, BookOpen, Globe2, Scale, Sparkles,
  ShieldCheck, Zap, Download, ChevronRight
} from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  {
    title: 'Upload Legal Documents',
    description: 'Securely process PDF and DOCX files with resilient, page-by-page extraction.',
    icon: BookOpen,
    color: 'from-blue-500 to-blue-700',
    bg: 'bg-blue-50',
  },
  {
    title: 'Multilingual Summaries',
    description: 'Generate concise AI summaries in 7 Indian languages including Tamil, Hindi, and Telugu.',
    icon: Globe2,
    color: 'from-emerald-500 to-teal-600',
    bg: 'bg-emerald-50',
  },
  {
    title: 'Preserve Legal Meaning',
    description: 'Maintains legal terminology, dates, case numbers, and court references with precision.',
    icon: Scale,
    color: 'from-violet-500 to-indigo-600',
    bg: 'bg-violet-50',
  },
];

const highlights = [
  { icon: Zap,         label: 'Gemini 2.5 Flash', sub: 'Powered by Google AI' },
  { icon: ShieldCheck, label: 'Secure & Private',  sub: 'Supabase Auth + RLS' },
  { icon: Download,    label: 'PDF / DOCX / TXT',  sub: 'Professional exports' },
];

const container = { hidden: {}, show: { transition: { staggerChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0 } };

export default function Home() {
  return (
    <div className="min-h-screen bg-slatebg overflow-hidden">

      {/* Hero Section */}
      <main className="relative mx-auto max-w-7xl px-4 pt-12 pb-20 sm:px-6 lg:px-8">

        {/* Background orbs */}
        <div className="pointer-events-none absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 h-[600px] w-[600px] rounded-full bg-blue-100/60 blur-3xl" />
          <div className="absolute -bottom-20 -left-40 h-[500px] w-[500px] rounded-full bg-indigo-100/50 blur-3xl" />
        </div>

        <div className="relative flex flex-col items-center lg:flex-row lg:items-center lg:gap-16">

          {/* Left — Hero Text */}
          <motion.section
            initial={{ opacity: 0, x: -24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45 }}
            className="flex-1 text-center lg:text-left"
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white/80 px-4 py-2 text-sm font-semibold text-navy shadow-sm backdrop-blur-sm mb-6"
            >
              <Scale size={15} className="text-gold" />
              e-Governance • Legal Intelligence • Stage 6 Ready
            </motion.div>

            <h1 className="font-heading text-4xl font-bold leading-tight text-navy sm:text-5xl lg:text-6xl">
              Empowering Faster
              <span className="block bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Access to Justice
              </span>
            </h1>

            <p className="mt-5 max-w-xl text-lg leading-8 text-slate-600 mx-auto lg:mx-0">
              AI-powered multilingual legal document summarization designed for Indian District Court e-Services.
              Upload once, summarize in 7 languages.
            </p>

            {/* Highlights */}
            <motion.div
              variants={container}
              initial="hidden"
              animate="show"
              className="mt-8 flex flex-wrap justify-center lg:justify-start gap-3"
            >
              {highlights.map(h => {
                const Icon = h.icon;
                return (
                  <motion.div
                    key={h.label}
                    variants={item}
                    className="flex items-center gap-2.5 rounded-xl border border-slate-200 bg-white px-4 py-2.5 shadow-sm"
                  >
                    <Icon size={16} className="text-navy" />
                    <div>
                      <p className="text-xs font-bold text-slate-800">{h.label}</p>
                      <p className="text-[10px] text-slate-500">{h.sub}</p>
                    </div>
                  </motion.div>
                );
              })}
            </motion.div>

            {/* CTAs */}
            <div className="mt-10 flex flex-wrap justify-center lg:justify-start gap-4">
              <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
                <Link
                  to="/summarizer"
                  className="inline-flex items-center gap-2 rounded-2xl bg-navy px-7 py-3.5 text-base font-bold text-white shadow-lg shadow-navy/25 hover:bg-[#16304d] transition-colors"
                >
                  <Sparkles size={18} /> Open AI Summarizer
                </Link>
              </motion.div>
              <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.97 }}>
                <Link
                  to="/login"
                  className="inline-flex items-center gap-2 rounded-2xl border-2 border-navy/20 bg-white px-7 py-3.5 text-base font-bold text-navy hover:bg-slate-50 transition-colors"
                >
                  Sign In to Workspace <ArrowRight size={18} />
                </Link>
              </motion.div>
            </div>
          </motion.section>

          {/* Right — Info Card */}
          <motion.section
            initial={{ opacity: 0, x: 24 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.45, delay: 0.1 }}
            className="mt-14 flex-1 lg:mt-0"
          >
            <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-soft sm:p-10">
              {/* Header */}
              <div className="flex items-center gap-4">
                <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-navy to-blue-800 text-white shadow-md">
                  <Scale size={24} />
                </div>
                <div>
                  <p className="font-heading text-lg font-bold text-navy">District Court e-Services</p>
                  <p className="text-sm text-slate-500">Multilingual Legal Summarizer</p>
                </div>
              </div>

              {/* Features */}
              <motion.div
                variants={container}
                initial="hidden"
                animate="show"
                className="mt-7 space-y-4"
              >
                {features.map(f => {
                  const Icon = f.icon;
                  return (
                    <motion.div
                      key={f.title}
                      variants={item}
                      className={`flex items-start gap-4 rounded-2xl ${f.bg} p-4 border border-slate-100`}
                    >
                      <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br ${f.color} text-white`}>
                        <Icon size={18} />
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-800">{f.title}</h3>
                        <p className="mt-1 text-sm leading-relaxed text-slate-500">{f.description}</p>
                      </div>
                    </motion.div>
                  );
                })}
              </motion.div>

              {/* CTA */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
                className="mt-7"
              >
                <Link
                  to="/summarizer"
                  className="group flex items-center justify-between rounded-2xl bg-gradient-to-r from-navy to-blue-800 px-6 py-4 text-white transition hover:from-[#16304d] hover:to-blue-900"
                >
                  <div>
                    <p className="font-bold">Try the AI Summarizer</p>
                    <p className="text-sm text-blue-200 mt-0.5">No account required</p>
                  </div>
                  <ChevronRight size={20} className="text-blue-300 group-hover:translate-x-1 transition-transform" />
                </Link>
              </motion.div>
            </div>
          </motion.section>
        </div>

        {/* Language badges strip */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="relative mt-16 text-center"
        >
          <p className="text-xs font-semibold uppercase tracking-widest text-slate-400 mb-4">
            Supported Languages
          </p>
          <div className="flex flex-wrap justify-center gap-2">
            {['English', 'தமிழ்', 'हिंदी', 'తెలుగు', 'ಕನ್ನಡ', 'മലയാളം', 'मराठी'].map((lang, i) => (
              <motion.span
                key={lang}
                initial={{ opacity: 0, scale: 0.85 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.6 + i * 0.05 }}
                className="rounded-full border border-slate-200 bg-white px-4 py-1.5 text-sm font-medium text-slate-700 shadow-sm"
              >
                {lang}
              </motion.span>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  );
}
