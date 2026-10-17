import React, { useState, useEffect } from 'react';
import { checkHealth, analyzeText } from './services/api';
import StatusBadge from './components/StatusBadge';
import {
  FileText,
  Cpu,
  BarChart3,
  Sparkles,
  RefreshCw,
  Server,
  Layers,
  AlertTriangle,
  Play,
  RotateCcw,
  BookOpen,
  Hash,
  Activity,
  AlignLeft,
  Compass
} from 'lucide-react';

const SAMPLE_TEXT = `Apache PySpark provides a robust, high-performance distributed DataFrame framework for big data processing. Word Intelligence integrates PySpark analytics with Natural Language Processing heuristics to transform unstructured content into structured insights. Analyzing token frequencies, bigrams, and word-length distributions allows researchers to understand linguistic patterns rapidly.`;

export default function App() {
  // Backend Health State
  const [healthState, setHealthState] = useState({
    status: 'checking',
    data: null,
    error: null,
    latencyMs: null,
    lastChecked: null,
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Analysis State
  const [inputText, setInputText] = useState(SAMPLE_TEXT);
  const [topN, setTopN] = useState(10);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const fetchHealth = async () => {
    setIsRefreshing(true);
    const startTime = performance.now();
    const result = await checkHealth();
    const endTime = performance.now();
    const latency = Math.round(endTime - startTime);

    if (result.success) {
      setHealthState({
        status: 'connected',
        data: result.data,
        error: null,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    } else {
      setHealthState({
        status: 'disconnected',
        data: null,
        error: result.error,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    }
    setIsRefreshing(false);
  };

  const handleAnalyze = async () => {
    if (!inputText.trim()) {
      setAnalysisError('Please enter or paste text to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    const result = await analyzeText({
      text: inputText,
      top_n: topN,
      case_sensitive: caseSensitive,
    });

    if (result.success) {
      setAnalysisResult(result.data);
    } else {
      setAnalysisError(result.error);
    }
    setIsAnalyzing(false);
  };

  useEffect(() => {
    fetchHealth();
    handleAnalyze();
  }, []);

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <div className="brand">
          <div className="brand-icon">
            <Layers size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <h1 className="brand-title">Word Intelligence</h1>
              <span className="brand-version">v0.4</span>
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <StatusBadge
            status={healthState.status}
            message={
              healthState.status === 'connected'
                ? `API Online (${healthState.latencyMs}ms)`
                : healthState.status === 'disconnected'
                ? 'API Disconnected'
                : 'Verifying...'
            }
          />
          <button
            onClick={fetchHealth}
            disabled={isRefreshing}
            className="btn-primary"
            style={{ padding: '0.45rem 0.9rem', fontSize: '0.8125rem' }}
            title="Refresh health status"
          >
            <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
            <span>Check</span>
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-tagline">
          <Sparkles size={16} />
          <span>Big Data & NLP Intelligence Platform</span>
        </div>
        <h2 className="hero-title">
          Unstructured Content into<br />Actionable Linguistic Insights
        </h2>
        <p className="hero-subtitle">
          Phase 2 Core Analytics Engine active. Process raw text with deterministic tokenization, frequency distributions, word-length statistics, and bigram collocation discovery.
        </p>
      </section>

      {/* Text Analysis Workspace (Phase 2) */}
      <section className="analyzer-section">
        <div className="section-title">
          <BookOpen size={20} color="var(--primary)" />
          <span>Interactive Text Analysis Workspace</span>
        </div>
        <p className="section-desc">
          Paste or write text below to execute high-performance deterministic word analytics.
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
          </div>

          <div className="buttons-group">
            <button
              onClick={() => setInputText(SAMPLE_TEXT)}
              className="btn-secondary"
              title="Load sample content"
            >
              <RotateCcw size={14} />
              <span>Sample</span>
            </button>
            <button
              onClick={() => { setInputText(''); setAnalysisResult(null); }}
              className="btn-secondary"
              title="Clear input"
            >
              <span>Clear</span>
            </button>
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="btn-primary"
            >
              <Play size={15} />
              <span>{isAnalyzing ? 'Analyzing...' : 'Analyze Text'}</span>
            </button>
          </div>
        </div>

        {analysisError && (
          <div style={{ marginTop: '1.25rem', padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={18} />
            <span>{analysisError}</span>
          </div>
        )}
      </section>

      {/* Analysis Results View */}
      {analysisResult && (
        <div className="results-container">
          {/* Metrics Summary Cards */}
          <div className="metrics-summary-grid">
            <div className="metric-card">
              <div className="metric-header">
                <span>Total Tokens</span>
                <Hash size={16} color="var(--primary)" />
              </div>
              <div className="metric-value">{analysisResult.total_tokens.toLocaleString()}</div>
              <div className="metric-sub">Processed word count</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span>Unique Words</span>
                <Sparkles size={16} color="var(--accent-cyan)" />
              </div>
              <div className="metric-value">{analysisResult.unique_tokens.toLocaleString()}</div>
              <div className="metric-sub">
                {analysisResult.total_tokens > 0 
                  ? `${Math.round((analysisResult.unique_tokens / analysisResult.total_tokens) * 100)}% vocabulary variety`
                  : '0% variety'}
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span>Avg Word Length</span>
                <AlignLeft size={16} color="var(--accent-emerald)" />
              </div>
              <div className="metric-value">{analysisResult.average_word_length}</div>
              <div className="metric-sub">Characters per token</div>
            </div>

            <div className="metric-card">
              <div className="metric-header">
                <span>Raw Characters</span>
                <Activity size={16} color="var(--accent-amber)" />
              </div>
              <div className="metric-value">{analysisResult.metadata.raw_character_count.toLocaleString()}</div>
              <div className="metric-sub">Includes whitespace & symbols</div>
            </div>
          </div>

          {/* Two-Column Results Display */}
          <div className="results-columns">
            {/* Top Words Frequency Table */}
            <div className="table-card">
              <div className="section-title" style={{ fontSize: '1.1rem' }}>
                <BarChart3 size={18} color="var(--primary)" />
                <span>Word Frequency Ranking (Top {analysisResult.top_words.length})</span>
              </div>

              <table className="data-table">
                <thead>
                  <tr>
                    <th style={{ width: '40px' }}>#</th>
                    <th>Word</th>
                    <th style={{ width: '70px' }}>Count</th>
                    <th>Frequency</th>
                  </tr>
                </thead>
                <tbody>
                  {analysisResult.top_words.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ color: 'var(--text-dim)', fontFamily: 'monospace' }}>{idx + 1}</td>
                      <td style={{ fontWeight: 600, color: 'var(--text-main)' }}>{item.word}</td>
                      <td style={{ fontFamily: 'monospace', color: '#c7d2fe' }}>{item.count}</td>
                      <td>
                        <div className="freq-bar-container">
                          <div className="freq-bar-bg">
                            <div
                              className="freq-bar-fill"
                              style={{ width: `${Math.min(100, item.percentage * 2.5)}%` }}
                            />
                          </div>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: '45px', textAlign: 'right' }}>
                            {item.percentage}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Word Length Distribution & Bigrams */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              {/* Length Distribution */}
              <div className="table-card">
                <div className="section-title" style={{ fontSize: '1.1rem' }}>
                  <Compass size={18} color="var(--accent-cyan)" />
                  <span>Word Length Distribution</span>
                </div>
                <div className="length-bars">
                  {analysisResult.word_length_distribution.map((item, idx) => {
                    const maxCount = Math.max(...analysisResult.word_length_distribution.map(d => d.count), 1);
                    const pct = Math.round((item.count / maxCount) * 100);
                    return (
                      <div key={idx} className="length-bar-row">
                        <span className="length-label">{item.length} chars</span>
                        <div className="freq-bar-bg">
                          <div className="freq-bar-fill" style={{ width: `${pct}%`, background: 'linear-gradient(90deg, #06b6d4, #6366f1)' }} />
                        </div>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: '30px', textAlign: 'right' }}>
                          {item.count}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Bigram Collocations */}
              <div className="table-card">
                <div className="section-title" style={{ fontSize: '1.1rem' }}>
                  <Sparkles size={18} color="var(--accent-emerald)" />
                  <span>Frequent Bigrams (2-Word Phrases)</span>
                </div>
                {analysisResult.bigrams.length > 0 ? (
                  <div className="bigram-grid">
                    {analysisResult.bigrams.map((bg, idx) => (
                      <div key={idx} className="bigram-pill">
                        <span>{bg.bigram}</span>
                        <span className="bigram-count">{bg.count}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p style={{ color: 'var(--text-dim)', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                    Insufficient words to generate bigrams.
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Diagnostics / Connection Panel */}
      <div className="diagnostics-panel">
        <div className="diagnostics-header">
          <div className="diagnostics-title">
            <Server size={18} color="var(--primary)" />
            <span>System Verification & Diagnostics</span>
          </div>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-dim)' }}>
            Last checked: {healthState.lastChecked || 'Pending'}
          </span>
        </div>

        <div className="diagnostics-list">
          <div className="diag-item">
            <span className="diag-label">Backend Status</span>
            <span className="diag-val" style={{ color: healthState.status === 'connected' ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
              {healthState.status === 'connected' ? 'OK (200)' : healthState.status === 'disconnected' ? 'UNREACHABLE' : 'CHECKING'}
            </span>
          </div>

          <div className="diag-item">
            <span className="diag-label">API Service</span>
            <span className="diag-val">{healthState.data?.app || 'Word Intelligence'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Active Phase</span>
            <span className="diag-val" style={{ color: 'var(--accent-cyan)' }}>Phase 2: Core Analytics</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Network Latency</span>
            <span className="diag-val">{healthState.latencyMs !== null ? `${healthState.latencyMs} ms` : 'N/A'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Endpoint Contract</span>
            <span className="diag-val">POST /api/v1/analysis</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Word Intelligence v0.4 — Big Data & NLP Analytics Engine. Phase 2 Verified.</p>
      </footer>
    </div>
  );
}
