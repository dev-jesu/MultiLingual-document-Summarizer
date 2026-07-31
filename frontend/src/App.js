import { useState } from 'react';
import './App.css';

const BACKEND_BASE_URL = 'http://127.0.0.1:8000';

function App() {
  const [file, setFile] = useState(null);
  const [strategy, setStrategy] = useState('merged');
  const [maxTokens, setMaxTokens] = useState(6000);
  const [overlap, setOverlap] = useState(150);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showRawText, setShowRawText] = useState(false);
  const [showCleanedText, setShowCleanedText] = useState(false);
  const [showAllChunks, setShowAllChunks] = useState(false);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
    setResponse(null);
    setError('');
    setShowRawText(false);
    setShowCleanedText(false);
    setShowAllChunks(false);
  };

  const isSummaryResponse = (data) => {
    return data && typeof data === 'object' && 'summary' in data && !('text' in data);
  };

  const renderMetadata = (data) => {
    const entries = [
      { label: 'Filename', value: data.filename || '—' },
      { label: 'Pages', value: data.pages ?? '—' },
      { label: 'Processed chunks', value: data.chunks_processed ?? data.total_chunks ?? '—' },
      { label: 'Estimated tokens', value: data.estimated_tokens ?? '—' },
      { label: 'Gemini requests', value: data.gemini_requests ?? '—' },
      { label: 'Processing time', value: data.processing_time_seconds ? `${data.processing_time_seconds}s` : '—' }
    ];

    return (
      <div className="metadata-grid">
        {entries.map((entry) => (
          <div className="meta-row" key={entry.label}>
            <span>{entry.label}</span>
            <span>{entry.value}</span>
          </div>
        ))}
      </div>
    );
  };

  const renderTextSection = (title, content, showState, setShowState) => {
    if (!content) {
      return null;
    }

    const preview = content.length > 1200 ? `${content.slice(0, 1200)}...` : content;

    return (
      <section className="result-section">
        <div className="section-header">
          <h3>{title}</h3>
          {content.length > 1200 && (
            <button type="button" className="expand-button" onClick={() => setShowState(!showState)}>
              {showState ? 'Show less' : 'Show full text'}
            </button>
          )}
        </div>
        <div className="result-text">{showState ? content : preview}</div>
      </section>
    );
  };

  const renderChunks = (chunks) => {
    if (!chunks || !Array.isArray(chunks) || chunks.length === 0) {
      return null;
    }

    const visibleChunks = showAllChunks ? chunks : chunks.slice(0, 3);

    return (
      <section className="result-section">
        <div className="section-header">
          <h3>Chunks</h3>
          {chunks.length > 3 && (
            <button type="button" className="expand-button" onClick={() => setShowAllChunks(!showAllChunks)}>
              {showAllChunks ? 'Show fewer' : `Show all (${chunks.length})`}
            </button>
          )}
        </div>
        <div className="chunks-list">
          {visibleChunks.map((chunk) => (
            <div key={chunk.chunk_index} className="chunk-card">
              <div className="chunk-header">
                <span>Chunk #{chunk.chunk_index + 1}</span>
                <span>{chunk.token_estimate} tokens</span>
              </div>
              <div className="chunk-text">{chunk.text}</div>
            </div>
          ))}
        </div>
      </section>
    );
  };

  const postFile = async (endpoint) => {
    if (!file) {
      setError('Please select a PDF or DOCX file first.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    if (endpoint === '/upload') {
      formData.append('strategy', strategy);
      formData.append('max_tokens', maxTokens);
      formData.append('overlap', overlap);
    }

    setLoading(true);
    setResponse(null);
    setError('');

    try {
      const res = await fetch(`${BACKEND_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Request failed.');
      }
      setResponse(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="panel">
        <h1>Legal Document Summarizer</h1>
        <p className="subtitle">Upload a legal document and either analyze it or generate a summary.</p>

        <label className="field-label">
          Document file
          <input type="file" accept=".pdf,.docx" onChange={handleFileChange} />
        </label>

        <div className="form-row">
          <label className="field-label">
            Chunking strategy
            <select value={strategy} onChange={(e) => setStrategy(e.target.value)}>
              <option value="merged">Merged</option>
              <option value="paragraph">Paragraph</option>
              <option value="page">Page</option>
            </select>
          </label>

          <label className="field-label">
            Max tokens
            <input
              type="number"
              value={maxTokens}
              min="100"
              max="8000"
              onChange={(e) => setMaxTokens(Number(e.target.value))}
            />
          </label>

          <label className="field-label">
            Overlap
            <input
              type="number"
              value={overlap}
              min="0"
              max="500"
              onChange={(e) => setOverlap(Number(e.target.value))}
            />
          </label>
        </div>

        <div className="button-row">
          <button onClick={() => postFile('/upload')} disabled={loading}>
            {loading ? 'Processing...' : 'Analyze Document'}
          </button>
          <button onClick={() => postFile('/summarize')} disabled={loading}>
            {loading ? 'Processing...' : 'Summarize Document'}
          </button>
        </div>

        {error && <div className="message error">{error}</div>}
        {response && (
          <div className="output-card">
            <h2>Result</h2>
            {renderMetadata(response)}

            {isSummaryResponse(response) ? (
              <section className="result-section">
                <h3>Summary</h3>
                <div className="result-text">{response.summary}</div>
              </section>
            ) : (
              <>
                {renderTextSection('Raw text', response.text, showRawText, setShowRawText)}
                {renderTextSection('Cleaned text', response.cleaned_text, showCleanedText, setShowCleanedText)}
                {renderChunks(response.chunks)}
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
