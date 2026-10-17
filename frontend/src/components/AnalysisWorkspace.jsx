import React from 'react';
import { BookOpen, RotateCcw, Play, AlertTriangle } from 'lucide-react';

export default function AnalysisWorkspace({
  inputText,
  setInputText,
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
  return (
    <section className="analyzer-section">
      <div className="section-title">
        <BookOpen size={20} color="var(--primary)" />
        <span>Text Analysis Workspace</span>
      </div>
      <p className="section-desc">
        Submit text below to execute high-performance linguistic analytics and frequency metrics.
      </p>

      <div className="textarea-container">
        <textarea
          className="text-input"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type or paste text content here..."
          rows={5}
        />
      </div>

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
          <button onClick={onLoadSample} className="btn-secondary" title="Load sample content">
            <RotateCcw size={14} />
            <span>Sample</span>
          </button>
          <button onClick={onClear} className="btn-secondary" title="Clear input">
            <span>Clear</span>
          </button>
          <button onClick={onAnalyze} disabled={isAnalyzing} className="btn-primary">
            <Play size={15} />
            <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Text'}</span>
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
