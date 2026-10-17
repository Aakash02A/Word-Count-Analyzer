import React from 'react';
import { Globe, Play, AlertTriangle } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import AnalysisResults from '../components/AnalysisResults';
import useAnalysis from '../hooks/useAnalysis';

export default function UrlAnalysisPage() {
  const analysis = useAnalysis('url');

  return (
    <div className="page-content">
      <PageHeader
        icon={<Globe size={22} color="var(--accent-cyan)" />}
        title="Webpage URL Analysis"
        description="Provide a public HTTP/HTTPS URL. The server safely fetches and extracts readable text with SSRF protection."
      />

      <section className="analyzer-section">
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
            <div style={{ position: 'relative', flex: 1 }}>
              <input
                type="url"
                className="text-input"
                style={{ minHeight: 'auto', padding: '0.75rem 1rem 0.75rem 2.5rem' }}
                value={analysis.inputUrl}
                onChange={(e) => analysis.setInputUrl(e.target.value)}
                placeholder="https://example.com/article"
              />
              <Globe size={18} color="var(--text-dim)" style={{ position: 'absolute', left: '0.85rem', top: '50%', transform: 'translateY(-50%)' }} />
            </div>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginTop: '0.5rem' }}>
            Content is fetched server-side with DNS validation, IP range filtering, redirect re-validation, and response size limits.
          </p>
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
              <select className="option-select" value={analysis.topN} onChange={(e) => analysis.setTopN(Number(e.target.value))}>
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={20}>Top 20</option>
                <option value={50}>Top 50</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <span>Engine:</span>
              <select className="option-select" value={analysis.engine} onChange={(e) => analysis.setEngine(e.target.value)} style={{ fontWeight: 500 }}>
                <option value="python">Python In-Memory (Ultra Fast)</option>
                <option value="pyspark">Apache PySpark (DataFrame)</option>
              </select>
            </div>
          </div>

          <div className="buttons-group">
            <button onClick={() => analysis.handleClear('url')} className="btn-secondary">
              <span>Clear</span>
            </button>
            <button onClick={() => analysis.handleAnalyze('url')} disabled={analysis.isAnalyzing} className="btn-primary">
              <Play size={15} />
              <span>{analysis.isAnalyzing ? 'Fetching...' : 'Analyze URL'}</span>
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
