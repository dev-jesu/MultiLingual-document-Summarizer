import { useState } from 'react';
import { motion } from 'framer-motion';
import { Copy, Download, FileText, RefreshCw } from 'lucide-react';
import Button from '../components/Button';
import DocumentInfoCard from '../components/DocumentInfoCard';
import EmptyState from '../components/EmptyState';
import ErrorAlert from '../components/ErrorAlert';
import LanguageSelector from '../components/LanguageSelector';
import LoadingProgress from '../components/LoadingProgress';
import SummaryCard from '../components/SummaryCard';
import Toast from '../components/Toast';
import UploadZone from '../components/UploadZone';
import { summarizeDocument, exportSummary } from '../services/api';

export default function Summarizer() {
  const [file, setFile] = useState(null);
  const [sourceLanguage, setSourceLanguage] = useState('auto');
  const [targetLanguage, setTargetLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [exportingFormat, setExportingFormat] = useState(null);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [toast, setToast] = useState(null);

  const showToast = (title, message = '', type = 'info', duration = 3500) => {
    setToast({ title, message, type });
    if (duration > 0) {
      setTimeout(() => setToast(null), duration);
    }
  };

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
      showToast('Summary Generated', 'Document legal summary is ready.', 'success');
    } catch (err) {
      const message = err?.response?.data?.detail || 'The service is temporarily unavailable. Please try again.';
      setError(message);
      showToast('Generation Failed', message, 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result?.summary) return;
    try {
      await navigator.clipboard.writeText(result.summary);
      showToast('Copy Summary', 'Summary copied to clipboard successfully.', 'success');
    } catch {
      showToast('Copy Failed', 'Unable to copy summary to clipboard.', 'error');
    }
  };

  const handleExport = async (format) => {
    if (!result?.summary) return;

    setExportingFormat(format);
    showToast('Download Started', `Preparing your ${format.toUpperCase()} report...`, 'info', 2000);

    const payload = {
      filename: result.filename || file?.name || 'judgement.pdf',
      summary: result.summary,
      language: targetLanguage,
      processing_time: `${result.processing_time_seconds || 0}s`,
    };

    try {
      const downloadedName = await exportSummary(format, payload);
      showToast('Export Successful', `Downloaded ${downloadedName}`, 'success');
    } catch (err) {
      const detail = err?.response?.data?.detail || `Failed to export ${format.toUpperCase()} report.`;
      showToast('Export Failed', detail, 'error');
    } finally {
      setExportingFormat(null);
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
                    <Button onClick={() => handleExport('pdf')} variant="secondary" className="gap-2" disabled={Boolean(exportingFormat)}>
                      <Download size={16} /> {exportingFormat === 'pdf' ? 'Downloading PDF...' : 'Download PDF'}
                    </Button>
                    <Button onClick={() => handleExport('docx')} variant="secondary" className="gap-2" disabled={Boolean(exportingFormat)}>
                      <Download size={16} /> {exportingFormat === 'docx' ? 'Downloading DOCX...' : 'Download DOCX'}
                    </Button>
                    <Button onClick={() => handleExport('txt')} variant="secondary" className="gap-2" disabled={Boolean(exportingFormat)}>
                      <FileText size={16} /> {exportingFormat === 'txt' ? 'Downloading TXT...' : 'Download TXT'}
                    </Button>
                    <Button onClick={handleCopy} variant="secondary" className="gap-2">
                      <Copy size={16} /> Copy Summary
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

      <Toast toast={toast} onClose={() => setToast(null)} />
    </div>
  );
}
