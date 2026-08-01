import { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Download, RefreshCw } from 'lucide-react';
import Button from '../components/Button';
import DocumentInfoCard from '../components/DocumentInfoCard';
import EmptyState from '../components/EmptyState';
import ErrorAlert from '../components/ErrorAlert';
import LanguageSelector from '../components/LanguageSelector';
import LoadingProgress from '../components/LoadingProgress';
import SummaryCard from '../components/SummaryCard';
import UploadZone from '../components/UploadZone';
import { summarizeDocument } from '../services/api';

export default function Summarizer() {
  const [file, setFile] = useState(null);
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    setError('');
    setResult(null);
  };

  const handleRemove = () => {
    setFile(null);
    setResult(null);
    setError('');
  };

  const handleSubmit = async () => {
    if (!file) {
      setError('Please select a PDF or DOCX file to continue.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('source_language', sourceLanguage);
    formData.append('target_language', targetLanguage);

    try {
      const response = await summarizeDocument(formData);
      setResult(response.data);
    } catch (err) {
      const message = err?.response?.data?.detail || 'The service is temporarily unavailable. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result?.summary) return;
    try {
      await navigator.clipboard.writeText(result.summary);
      setError('');
    } catch {
      setError('Unable to copy summary.');
    }
  };

  return (
    <div className="min-h-screen bg-slatebg px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} className="rounded-[32px] border border-slate-200 bg-white p-6 shadow-soft sm:p-8 lg:p-10">
          <div className="text-center">
            <p className="text-sm font-semibold uppercase tracking-[0.2em] text-gold">Summarizer</p>
            <h1 className="mt-2 font-heading text-3xl font-semibold text-navy sm:text-4xl">Upload a legal document and generate a summary</h1>
            <p className="mx-auto mt-3 max-w-2xl text-base text-slate-600">Supported formats: PDF and DOCX. Choose the source and target languages for multilingual summaries.</p>
          </div>

          <div className="mt-8 grid gap-8 lg:grid-cols-[1.1fr_0.9fr]">
            <div className="space-y-6">
              <div className="rounded-3xl border border-slate-200 bg-slate-50 p-5">
                <h2 className="text-lg font-semibold text-slate-800">Upload Legal Document</h2>
                <p className="mt-1 text-sm text-slate-500">Supported formats: PDF and DOCX</p>
                <div className="mt-5">
                  <UploadZone file={file} onFileChange={handleFileChange} onRemove={handleRemove} />
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <LanguageSelector label="Source Language" value={sourceLanguage} onChange={setSourceLanguage} source />
                <LanguageSelector label="Target Language" value={targetLanguage} onChange={setTargetLanguage} />
              </div>

              <div className="flex justify-center">
                <Button onClick={handleSubmit} disabled={!file || loading} className="min-w-[220px]">
                  {loading ? 'Generating Summary...' : 'Generate Summary'}
                </Button>
              </div>
            </div>

            <div className="space-y-6">
              {loading ? (
                <LoadingProgress />
              ) : error ? (
                <ErrorAlert message={error} />
              ) : !file ? (
                <EmptyState />
              ) : null}

              {result && (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
                  <SummaryCard summary={result.summary} />
                  <DocumentInfoCard data={result} />
                  <div className="flex flex-wrap gap-3">
                    <Button onClick={handleCopy} variant="secondary" className="gap-2">
                      <Copy size={16} /> Copy Summary
                    </Button>
                    <Button variant="secondary" className="gap-2" disabled>
                      <Download size={16} /> Download PDF
                    </Button>
                    <Button variant="secondary" className="gap-2" disabled>
                      <Download size={16} /> Download DOCX
                    </Button>
                    <Button onClick={handleRemove} variant="secondary" className="gap-2">
                      <RefreshCw size={16} /> Upload New Document
                    </Button>
                  </div>
                </motion.div>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
