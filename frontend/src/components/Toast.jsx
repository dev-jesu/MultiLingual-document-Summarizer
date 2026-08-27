import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

export default function Toast({ toast, onClose }) {
  if (!toast) return null;

  const typeStyles = {
    success: 'bg-emerald-900/90 border-emerald-500/40 text-emerald-100 shadow-emerald-950/40',
    error: 'bg-rose-900/90 border-rose-500/40 text-rose-100 shadow-rose-950/40',
    info: 'bg-blue-900/90 border-blue-500/40 text-blue-100 shadow-blue-950/40',
  };

  const icons = {
    success: <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0" />,
    error: <AlertCircle className="h-5 w-5 text-rose-400 shrink-0" />,
    info: <Info className="h-5 w-5 text-blue-400 shrink-0" />,
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: 30, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        exit={{ opacity: 0, y: 20, scale: 0.95 }}
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-2xl border px-4 py-3.5 text-sm font-medium shadow-2xl backdrop-blur-md transition-all ${
          typeStyles[toast.type] || typeStyles.info
        }`}
      >
        {icons[toast.type] || icons.info}
        <div className="flex-1 pr-2">
          <p className="font-semibold">{toast.title}</p>
          {toast.message && <p className="text-xs opacity-80 mt-0.5">{toast.message}</p>}
        </div>
        <button
          onClick={onClose}
          className="rounded-lg p-1 hover:bg-white/10 transition-colors"
          aria-label="Close notification"
        >
          <X className="h-4 w-4 opacity-70 hover:opacity-100" />
        </button>
      </motion.div>
    </AnimatePresence>
  );
}
