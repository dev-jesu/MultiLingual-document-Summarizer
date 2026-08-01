import { motion } from 'framer-motion';
import { CheckCircle2, FileText, ScanLine, Sparkles, BookText } from 'lucide-react';

const steps = [
  { label: 'Upload Complete', icon: CheckCircle2, active: true },
  { label: 'Parsing Document', icon: FileText, active: true },
  { label: 'Cleaning Text', icon: ScanLine, active: true },
  { label: 'Chunking Document', icon: BookText, active: true },
  { label: 'Generating Summary', icon: Sparkles, active: false },
];

export default function LoadingProgress() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft"
    >
      <div className="mb-6 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gold">Processing</p>
          <h3 className="mt-1 text-xl font-semibold text-slate-800">Preparing your legal summary</h3>
        </div>
        <div className="rounded-full bg-navy/10 px-3 py-1 text-sm font-medium text-navy">In progress</div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {steps.map((step, index) => {
          const Icon = step.icon;
          return (
            <div key={step.label} className="rounded-2xl border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
              <div className={`mb-2 flex h-9 w-9 items-center justify-center rounded-full ${index < 4 ? 'bg-navy text-white' : 'bg-gold/15 text-gold'}`}>
                <Icon size={16} />
              </div>
              <p className="font-medium text-slate-800">{step.label}</p>
            </div>
          );
        })}
      </div>
    </motion.div>
  );
}
