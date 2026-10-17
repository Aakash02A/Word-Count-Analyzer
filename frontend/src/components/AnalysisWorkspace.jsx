import React, { useRef } from 'react';
import {
  BookOpen,
  RotateCcw,
  Play,
  AlertTriangle,
  FileText,
  Upload,
  Globe,
  FileCheck
} from 'lucide-react';

export default function AnalysisWorkspace({
  inputMode = 'text',
  setInputMode,
  inputText,
  setInputText,
  selectedFile,
  setSelectedFile,
  inputUrl,
  setInputUrl,
  caseSensitive,
  setCaseSensitive,
  topN,
  setTopN,
  engine = 'python',
  setEngine,
  isAnalyzing,
  onAnalyze,
  onLoadSample,
  onClear,
  error,
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <section className="analyzer-section">
      <div className="section-title">
        <BookOpen size={20} color="var(--primary)" />
        <span>Multi-Source Ingestion & Analysis Workspace</span>
      </div>
      <p className="section-desc">
        Select your content source below: paste raw text, upload documents (TXT, PDF, DOCX), or analyze a public webpage URL.
      </p>

      {/* Ingestion Source Tabs */}
      <div className="tab-bar">
        <button
          className={`tab-btn ${inputMode === 'text' ? 'active' : ''}`}
          onClick={() => setInputMode('text')}
        >
          <FileText size={16} />
          <span>Raw Text</span>
        </button>

        <button
          className={`tab-btn ${inputMode === 'file' ? 'active' : ''}`}
          onClick={() => setInputMode('file')}
        >
          <Upload size={16} />
          <span>Document Upload</span>
        </button>

        <button
          className={`tab-btn ${inputMode === 'url' ? 'active' : ''}`}
          onClick={() => setInputMode('url')}
        >
          <Globe size={16} />
          <span>Webpage URL</span>
        </button>
      </div>

      {/* Input Mode 1: Raw Text */}
      {inputMode === 'text' && (
        <div className="textarea-container">
          <textarea
            className="text-input"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Type or paste text content here..."
            rows={5}
          />
        </div>
      )}

      {/* Input Mode 2: Document Upload */}
      {inputMode === 'file' && (
        <div>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept=".txt,.pdf,.docx"
            style={{ display: 'none' }}
          />
          <div
            className="file-dropzone"
            onClick={() => fileInputRef.current?.click()}
          >
            {selectedFile ? (
              <>
                <FileCheck size={36} color="var(--accent-emerald)" />
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{selectedFile.name}</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                  {Math.round(selectedFile.size / 1024)} KB • Click to change document
                </span>
              </>
            ) : (
              <>
                <Upload size={36} color="var(--primary)" />
                <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>Click or Drag & Drop Document Here</span>
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                  Supports plain text (.txt), PDF (.pdf), and Word (.docx) up to 10 MB
                </span>
              </>
            )}
          </div>
        </div>
      )}

      {/* Input Mode 3: Webpage URL */}
      {inputMode === 'url' && (
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="url"
                className="text-input"
                style={{ minHeight: 'auto', padding: '0.75rem 1rem 0.75rem 2.5rem' }}
                value={inputUrl}
                onChange={(e) => setInputUrl(e.target.value)}
                placeholder="https://example.com/article"
              />
              <Globe size={18} color="var(--text-dim)" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
            Webpage content is fetched safely with server-side SSRF validation, DNS verification, and DOM parsing.
          </p>
        </div>
      )}

      {/* Common Controls Row */}
      <div className="controls-row">
        <div className="options-group">
          <label className="option-item">
            <input
              type="checkbox"
              checked={caseSensitive}
              onChange={(e) => setCaseSensitive(e.target.checked)}
            />
            <span>Case Sensitive</span>
          </label>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            <span>Top Words:</span>
            <select
              className="option-select"
              value={topN}
              onChange={(e) => setTopN(Number(e.target.value))}
            >
              <option value={5}>Top 5</option>
              <option value={10}>Top 10</option>
              <option value={20}>Top 20</option>
              <option value={50}>Top 50</option>
            </select>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
            <span>Engine:</span>
            <select
              className="option-select"
              value={engine}
              onChange={(e) => setEngine && setEngine(e.target.value)}
              style={{ fontWeight: 500 }}
            >
              <option value="python">Python In-Memory (Ultra Fast)</option>
              <option value="pyspark">Apache PySpark (DataFrame)</option>
            </select>
          </div>
        </div>

        <div className="buttons-group">
          {inputMode === 'text' && (
            <button onClick={onLoadSample} className="btn-secondary" title="Load sample content">
              <RotateCcw size={14} />
              <span>Sample</span>
            </button>
          )}
          <button onClick={onClear} className="btn-secondary" title="Clear input">
            <span>Clear</span>
          </button>
          <button onClick={onAnalyze} disabled={isAnalyzing} className="btn-primary">
            <Play size={15} />
            <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Source'}</span>
          </button>
        </div>
      </div>

      {error && (
        <div style={{ marginTop: '1.25rem', padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={18} />
          <span>{error}</span>
        </div>
      )}
    </section>
  );
}
