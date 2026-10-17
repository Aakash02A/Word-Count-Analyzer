import React, { useRef } from 'react';
import { Upload, FileCheck, Play, AlertTriangle } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import AnalysisResults from '../components/AnalysisResults';
import useAnalysis from '../hooks/useAnalysis';

export default function DocumentsPage() {
  const analysis = useAnalysis('file');
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      analysis.setSelectedFile(e.target.files[0]);
    }
  };

  return (
    <div className="page-content">
      <PageHeader
        icon={<Upload size={22} color="var(--accent-emerald)" />}
        title="Document Upload"
        description="Upload TXT, PDF, or DOCX files. The system extracts readable text and performs full analysis."
      />

      <section className="analyzer-section">
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
          {analysis.selectedFile ? (
            <>
              <FileCheck size={36} color="var(--accent-emerald)" />
              <span style={{ fontWeight: 600, color: 'var(--text-main)' }}>{analysis.selectedFile.name}</span>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                {Math.round(analysis.selectedFile.size / 1024)} KB • Click to change document
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

        <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>
          Scanned PDFs without embedded text may not produce results. OCR is not currently supported.
        </p>

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
            <button onClick={() => analysis.handleClear('file')} className="btn-secondary">
              <span>Clear</span>
            </button>
            <button onClick={() => analysis.handleAnalyze('file')} disabled={analysis.isAnalyzing} className="btn-primary">
              <Play size={15} />
              <span>{analysis.isAnalyzing ? 'Processing...' : 'Analyze Document'}</span>
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
