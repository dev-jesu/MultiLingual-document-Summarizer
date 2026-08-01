import { motion } from 'framer-motion';
import PropTypes from 'prop-types';

export default function SummaryCard({ summary, title = 'Summary' }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft"
    >
      <div className="mb-4 flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gold">{title}</p>
          <h3 className="mt-1 text-xl font-semibold text-slate-800">Generated Summary</h3>
        </div>
      </div>
      <div className="whitespace-pre-line rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-700">
        {summary || 'No summary available yet.'}
      </div>
    </motion.section>
  );
}

SummaryCard.propTypes = {
  summary: PropTypes.string,
  title: PropTypes.string,
};
