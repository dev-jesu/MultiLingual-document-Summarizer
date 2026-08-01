import { FileSearch } from 'lucide-react';

export default function EmptyState() {
  return (
    <div className="rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-10 text-center">
      <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-navy/10 text-navy">
        <FileSearch size={28} />
      </div>
      <h3 className="mt-5 text-xl font-semibold text-slate-800">No document uploaded yet</h3>
      <p className="mt-2 text-sm text-slate-500">Upload a PDF or DOCX file to generate a professional summary.</p>
    </div>
  );
}
