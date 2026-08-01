import { FileText, UploadCloud, X } from 'lucide-react';
import PropTypes from 'prop-types';

export default function UploadZone({ file, onFileChange, onRemove }) {
  const handleDrop = (event) => {
    event.preventDefault();
    const droppedFile = event.dataTransfer.files?.[0];
    if (droppedFile) {
      onFileChange(droppedFile);
    }
  };

  return (
    <div
      onDragOver={(event) => event.preventDefault()}
      onDrop={handleDrop}
      className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-6 text-center transition hover:border-navy hover:bg-white"
    >
      {file ? (
        <div className="space-y-3">
          <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-navy/10 text-navy">
            <FileText size={24} />
          </div>
          <div>
            <p className="font-semibold text-slate-800">{file.name}</p>
            <p className="text-sm text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB • {file.type || 'Unknown type'}</p>
          </div>
          <button
            type="button"
            onClick={onRemove}
            className="inline-flex items-center gap-2 rounded-full border border-slate-300 px-3 py-2 text-sm text-slate-600 hover:border-red-300 hover:text-red-600"
          >
            <X size={14} /> Remove
          </button>
        </div>
      ) : (
        <div className="space-y-3">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-navy/10 text-navy">
            <UploadCloud size={28} />
          </div>
          <div>
            <p className="text-lg font-semibold text-slate-800">Drag & Drop your legal document</p>
            <p className="mt-1 text-sm text-slate-500">or browse files from your device</p>
          </div>
          <label className="inline-flex cursor-pointer items-center rounded-full border border-navy px-4 py-2 text-sm font-semibold text-navy transition hover:bg-navy hover:text-white">
            Browse Files
            <input type="file" accept=".pdf,.docx" className="hidden" onChange={(event) => onFileChange(event.target.files?.[0])} />
          </label>
          <p className="text-xs text-slate-500">Supported formats: PDF • DOCX • Max 100 MB</p>
        </div>
      )}
    </div>
  );
}

UploadZone.propTypes = {
  file: PropTypes.object,
  onFileChange: PropTypes.func.isRequired,
  onRemove: PropTypes.func.isRequired,
};
