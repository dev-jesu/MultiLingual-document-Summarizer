import PropTypes from 'prop-types';

export default function DocumentInfoCard({ data }) {
  const metadata = [
    { label: 'Filename', value: data?.filename || '—' },
    { label: 'Pages', value: data?.pages ?? '—' },
    { label: 'Processing Time', value: data?.processing_time_seconds ? `${data.processing_time_seconds}s` : '—' },
    { label: 'Language', value: data?.summary ? 'Multilingual output' : '—' },
    { label: 'Estimated Tokens', value: data?.estimated_tokens ?? '—' },
  ];

  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-soft">
      <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gold">Document Information</p>
      <div className="mt-5 grid gap-4 sm:grid-cols-2">
        {metadata.map((item) => (
          <div key={item.label} className="rounded-2xl bg-slate-50 p-4">
            <p className="text-xs uppercase tracking-[0.2em] text-slate-500">{item.label}</p>
            <p className="mt-2 text-sm font-semibold text-slate-800">{item.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

DocumentInfoCard.propTypes = {
  data: PropTypes.object,
};
