import React from 'react';
import MetricsCards from './MetricsCards';
import FrequencyTable from './FrequencyTable';
import WordFrequencyChart from './WordFrequencyChart';
import LengthDistribution from './LengthDistribution';
import LengthDistributionChart from './LengthDistributionChart';
import BigramPills from './BigramPills';
import SentimentCard from './SentimentCard';
import NounPhrasesPills from './NounPhrasesPills';
import { FileText, Globe, Upload, Image as ImageIcon, Download, BarChart2, Table, Activity, Copy, Check } from 'lucide-react';

/**
 * Reusable analysis results panel.
 * Renders metrics, charts, tables, and export for any analysis result.
 */
export default function AnalysisResults({
  analysisResult,
  freqViewMode,
  setFreqViewMode,
  lengthViewMode,
  setLengthViewMode,
  isExporting,
  onExportCsv,
}) {
  const [copied, setCopied] = React.useState(false);

  if (!analysisResult) return null;

  const handleCopyExtracted = () => {
    if (analysisResult.extracted_text) {
      navigator.clipboard.writeText(analysisResult.extracted_text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="results-container">
      {/* Action & Meta Header Bar */}
      <div className="results-header-bar">
        <div className="results-meta-badge">
          {analysisResult.metadata.source_type === 'file' ? (
            <Upload size={16} color="var(--accent-emerald)" />
          ) : analysisResult.metadata.source_type === 'url' ? (
            <Globe size={16} color="var(--accent-cyan)" />
          ) : analysisResult.metadata.source_type === 'image' ? (
            <ImageIcon size={16} color="var(--accent-amber)" />
          ) : (
            <FileText size={16} color="var(--primary)" />
          )}
          <span>
            Source: <strong style={{ color: 'var(--text-main)' }}>{analysisResult.metadata.source_name || 'Direct Input'}</strong>
            {' '}({analysisResult.metadata.source_type.toUpperCase()})
          </span>
          <span style={{ color: 'var(--border-subtle)' }}>•</span>
          <span style={{ fontFamily: 'monospace', color: 'var(--text-dim)' }}>
            {analysisResult.metadata.engine_used} ({analysisResult.metadata.execution_time_ms || 0}ms)
          </span>
        </div>

        <button
          className="btn-export"
          onClick={onExportCsv}
          disabled={isExporting}
        >
          <Download size={15} />
          <span>{isExporting ? 'Exporting...' : 'Export CSV Report'}</span>
        </button>
      </div>

      {/* Extracted Text (OCR) Preview Panel if present */}
      {analysisResult.extracted_text && (
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.25rem 1.5rem',
            display: 'flex',
            flexDirection: 'column',
            gap: '0.75rem',
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <ImageIcon size={16} color="var(--accent-amber)" />
              <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)' }}>
                Extracted Text from Image (OCR)
              </span>
            </div>
            <button
              onClick={handleCopyExtracted}
              className="btn-secondary"
              style={{ padding: '0.3rem 0.65rem', fontSize: '0.75rem', display: 'inline-flex', alignItems: 'center', gap: '0.35rem' }}
            >
              {copied ? <Check size={13} color="var(--accent-emerald)" /> : <Copy size={13} />}
              <span>{copied ? 'Copied!' : 'Copy Text'}</span>
            </button>
          </div>
          <p
            style={{
              margin: 0,
              fontSize: '0.85rem',
              color: 'var(--text-muted)',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap',
              maxHeight: '160px',
              overflowY: 'auto',
              background: 'var(--bg-secondary)',
              padding: '0.75rem 1rem',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            {analysisResult.extracted_text}
          </p>
        </div>
      )}

      {/* Metric Summary Cards */}
      <MetricsCards result={analysisResult} />

      {/* Two-Column Detail View */}
      <div className="results-columns">
        {/* Left Column: Frequency Ranking (Table or Visual Chart) & Noun Phrases */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.5rem', gap: '0.25rem' }}>
              <button
                className={`view-toggle-btn ${freqViewMode === 'table' ? 'active' : ''}`}
                onClick={() => setFreqViewMode('table')}
              >
                <Table size={13} />
                <span>Table</span>
              </button>
              <button
                className={`view-toggle-btn ${freqViewMode === 'chart' ? 'active' : ''}`}
                onClick={() => setFreqViewMode('chart')}
              >
                <BarChart2 size={13} />
                <span>Chart</span>
              </button>
            </div>

            {freqViewMode === 'table' ? (
              <FrequencyTable topWords={analysisResult.top_words} />
            ) : (
              <WordFrequencyChart topWords={analysisResult.top_words} />
            )}
          </div>

          <NounPhrasesPills phrases={analysisResult.noun_phrases} />
        </div>

        {/* Right Column: Sentiment, Length Distribution (Bars or Chart Curve), Bigrams */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <SentimentCard sentiment={analysisResult.sentiment} />

          <div>
            <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.5rem', gap: '0.25rem' }}>
              <button
                className={`view-toggle-btn ${lengthViewMode === 'bars' ? 'active' : ''}`}
                onClick={() => setLengthViewMode('bars')}
              >
                <Table size={13} />
                <span>Bars</span>
              </button>
              <button
                className={`view-toggle-btn ${lengthViewMode === 'chart' ? 'active' : ''}`}
                onClick={() => setLengthViewMode('chart')}
              >
                <Activity size={13} />
                <span>Curve</span>
              </button>
            </div>

            {lengthViewMode === 'bars' ? (
              <LengthDistribution distribution={analysisResult.word_length_distribution} />
            ) : (
              <LengthDistributionChart distribution={analysisResult.word_length_distribution} />
            )}
          </div>

          <BigramPills bigrams={analysisResult.bigrams} />
        </div>
      </div>
    </div>
  );
}
