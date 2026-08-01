import { AlertCircle } from 'lucide-react';
import PropTypes from 'prop-types';

export default function ErrorAlert({ message }) {
  if (!message) return null;

  return (
    <div className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
      <div className="flex items-start gap-2">
        <AlertCircle size={16} className="mt-0.5 shrink-0" />
        <span>{message}</span>
      </div>
    </div>
  );
}

ErrorAlert.propTypes = {
  message: PropTypes.string,
};
