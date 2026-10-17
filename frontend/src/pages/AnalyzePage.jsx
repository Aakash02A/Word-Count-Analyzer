import React, { useEffect, useRef } from 'react';
import { FileText, BookOpen, RotateCcw, Play, AlertTriangle } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import AnalysisResults from '../components/AnalysisResults';
import useAnalysis from '../hooks/useAnalysis';

export default function AnalyzePage() {
  const analysis = useAnalysis('text');
  const hasRun = useRef(false);

  // Auto-analyze sample text on first load
  useEffect(() => {
    if (!hasRun.current && analysis.inputText.trim()) {
      hasRun.current = true;
      analysis.handleAnalyze('text');
    }
  }, []);

  return (
    <div className="page-content">
      <PageHeader
        icon={<FileText size={22} color="var(--primary)" />}
        title="Analyze Text"
        description="Paste or type raw text for comprehensive linguistic analysis including word frequency, sentiment, bigrams, and noun phrase extraction."
      />

      {/* Text Input Section */}
      <section className="analyzer-section">
        <div className="section-title">
          <BookOpen size={20} color="var(--primary)" />
          <span>Text Input</span>
        </div>
        <p className="section-desc">
          Enter or paste text content below. Use the controls to configure analysis options.
        </p>

        <div className="textarea-container">
          <textarea
            className="text-input"
            value={analysis.inputText}
            onChange={(e) => analysis.setInputText(e.target.value)}
            placeholder="Type or paste text content here..."
            rows={6}
          />
        </div>

        {/* Controls Row */}
        <div className="controls-row">
          <div className="options-group">
            <label className="option-item">
              <input
                type="checkbox"
                checked={analysis.caseSensitive}
                onChange={(e) => analysis.setCaseSensitive(e.target.checked)}
              />
              <span>Case Sensitive</span>
            </label>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <span>Top Words:</span>
              <select
                className="option-select"
                value={analysis.topN}
                onChange={(e) => analysis.setTopN(Number(e.target.value))}
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
                value={analysis.engine}
                onChange={(e) => analysis.setEngine(e.target.value)}
                style={{ fontWeight: 500 }}
              >
                <option value="python">Python In-Memory (Ultra Fast)</option>
                <option value="pyspark">Apache PySpark (DataFrame)</option>
              </select>
            </div>
          </div>

          <div className="buttons-group">
            <button onClick={analysis.loadSample} className="btn-secondary" title="Load sample content">
              <RotateCcw size={14} />
              <span>Sample</span>
            </button>
            <button onClick={() => analysis.handleClear('text')} className="btn-secondary" title="Clear input">
              <span>Clear</span>
            </button>
            <button onClick={() => analysis.handleAnalyze('text')} disabled={analysis.isAnalyzing} className="btn-primary">
              <Play size={15} />
              <span>{analysis.isAnalyzing ? 'Analyzing...' : 'Analyze Text'}</span>
            </button>
          </div>
        </div>

        {analysis.analysisError && (
          <div style={{ marginTop: '1.25rem', padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={18} />
            <span>{analysis.analysisError}</span>
          </div>
        )}
      </section>

      {/* Results */}
      <AnalysisResults
        analysisResult={analysis.analysisResult}
        freqViewMode={analysis.freqViewMode}
        setFreqViewMode={analysis.setFreqViewMode}
        lengthViewMode={analysis.lengthViewMode}
        setLengthViewMode={analysis.setLengthViewMode}
        isExporting={analysis.isExporting}
        onExportCsv={analysis.handleExportCsv}
      />
    </div>
  );
}
