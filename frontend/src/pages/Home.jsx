import { motion } from 'framer-motion';
import { ArrowRight, BookOpen, Globe2, Scale } from 'lucide-react';
import { Link } from 'react-router-dom';

const features = [
  { title: 'Upload Legal Documents', description: 'Securely process PDF and DOCX files with a trusted workflow.', icon: BookOpen },
  { title: 'Summarize in Multiple Indian Languages', description: 'Generate concise legal summaries in English, Tamil, Hindi, Telugu, Kannada, Malayalam, and Marathi.', icon: Globe2 },
  { title: 'Preserve Legal Meaning', description: 'Maintain legal terminology, dates, case numbers, and court references.', icon: Scale },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-slatebg">
      <main className="mx-auto flex min-h-[calc(100vh-120px)] max-w-7xl flex-col px-4 py-8 sm:px-6 lg:flex-row lg:items-center lg:px-8 lg:py-12">
        <motion.section
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.35 }}
          className="flex-1 lg:pr-10"
        >
          <div className="inline-flex items-center rounded-full border border-slate-200 bg-white px-3 py-2 text-sm font-medium text-navy shadow-sm">
            <Scale size={16} className="mr-2" /> e-Governance • Legal Intelligence
          </div>
          <h1 className="mt-6 max-w-2xl font-heading text-4xl font-semibold leading-tight text-navy sm:text-5xl">
            Empowering Faster Access to Legal Information
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-600">
            AI-powered multilingual legal document summarization designed for Indian District Court e-Services.
          </p>

          <div className="mt-8 grid gap-4 md:grid-cols-3">
            {features.map((feature) => {
              const Icon = feature.icon;
              return (
                <div key={feature.title} className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-navy/10 text-navy">
                    <Icon size={18} />
                  </div>
                  <h3 className="font-semibold text-slate-800">{feature.title}</h3>
                  <p className="mt-2 text-sm leading-6 text-slate-500">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </motion.section>

        <motion.section
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.35 }}
          className="mt-10 flex-1 lg:mt-0"
        >
          <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-soft sm:p-10">
            <div className="flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-navy text-white">
                <Scale size={20} />
              </div>
              <div>
                <p className="font-heading text-lg font-semibold text-navy">Multilingual Legal Document Summarization Tool</p>
                <p className="text-sm text-slate-500">Official e-Court digital service</p>
              </div>
            </div>

            <p className="mt-8 text-lg leading-8 text-slate-600">
              Generate accurate AI-powered legal summaries across multiple Indian languages with a professional, trustworthy experience.
            </p>

            <Link to="/summarizer" className="mt-8 inline-flex items-center rounded-full bg-navy px-6 py-3 font-semibold text-white transition hover:bg-[#16304d]">
              Open Summarizer <ArrowRight className="ml-2" size={18} />
            </Link>
          </div>
        </motion.section>
      </main>
    </div>
  );
}
