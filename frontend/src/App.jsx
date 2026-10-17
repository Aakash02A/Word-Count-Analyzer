import React, { useState, useEffect } from 'react';
import { checkHealth } from './services/api';
import StatusBadge from './components/StatusBadge';
import {
  FileText,
  Cpu,
  BarChart3,
  Sparkles,
  RefreshCw,
  Server,
  Globe,
  Layers,
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

export default function App() {
  const [healthState, setHealthState] = useState({
    status: 'checking', // 'checking' | 'connected' | 'disconnected'
    data: null,
    error: null,
    latencyMs: null,
    lastChecked: null,
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

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

  useEffect(() => {
    fetchHealth();
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
          Phase 1 Foundation established. High-performance FastAPI backend paired with modern React Vite frontend, ready for multi-source ingestion, PySpark analytics, and sentiment processing.
        </p>
      </section>

      {/* Diagnostics / Connection Banner */}
      <div className="diagnostics-panel">
        <div className="diagnostics-header">
          <div className="diagnostics-title">
            <Server size={18} color="var(--primary)" />
            <span>Phase 1 System Verification & Diagnostics</span>
          </div>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-dim)' }}>
            Last checked: {healthState.lastChecked || 'Pending'}
          </span>
        </div>

        <div className="diagnostics-list">
          <div className="diag-item">
            <span className="diag-label">Backend Liveness</span>
            <span className="diag-val" style={{ color: healthState.status === 'connected' ? 'var(--accent-emerald)' : 'var(--accent-rose)' }}>
              {healthState.status === 'connected' ? 'OK (200)' : healthState.status === 'disconnected' ? 'UNREACHABLE' : 'CHECKING'}
            </span>
          </div>

          <div className="diag-item">
            <span className="diag-label">API Service</span>
            <span className="diag-val">{healthState.data?.app || 'Word Intelligence'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Service Version</span>
            <span className="diag-val">{healthState.data?.version || '0.4.0'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Runtime Environment</span>
            <span className="diag-val">{healthState.data?.environment || 'development'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Network Latency</span>
            <span className="diag-val">{healthState.latencyMs !== null ? `${healthState.latencyMs} ms` : 'N/A'}</span>
          </div>

          <div className="diag-item">
            <span className="diag-label">Client Host</span>
            <span className="diag-val">Vite (127.0.0.1:5173)</span>
          </div>
        </div>

        {healthState.status === 'disconnected' && (
          <div style={{ marginTop: '1rem', padding: '0.75rem 1rem', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.25)', borderRadius: 'var(--radius-sm)', color: '#fb7185', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <AlertTriangle size={18} />
            <span>Connection note: {healthState.error}. Ensure backend is running via <code>python -m uvicorn app.main:app --port 8000</code>.</span>
          </div>
        )}
      </div>

      {/* Architecture Pillars Grid */}
      <div className="grid">
        <div className="card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'rgba(6, 182, 212, 0.15)', color: 'var(--accent-cyan)' }}>
              <FileText size={20} />
            </div>
            <h3 className="card-title">Multi-Source Ingestion</h3>
          </div>
          <p className="card-desc">
            Direct text pasting, TXT, PDF, DOCX file extraction via pypdf and python-docx, plus SSRF-guarded URL extraction.
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)' }}>
              <Cpu size={20} />
            </div>
            <h3 className="card-title">PySpark Analytics</h3>
          </div>
          <p className="card-desc">
            Deterministic token metrics, word frequency rankings, length distributions, and high-performance DataFrame operations.
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'rgba(168, 85, 247, 0.15)', color: '#c084fc' }}>
              <Sparkles size={20} />
            </div>
            <h3 className="card-title">NLP Intelligence</h3>
          </div>
          <p className="card-desc">
            Sentiment polarity heuristics, subjectivity estimates, n-gram patterns, and noun-phrase discovery powered by TextBlob & NLTK.
          </p>
        </div>

        <div className="card">
          <div className="card-header">
            <div className="card-icon" style={{ background: 'rgba(16, 185, 129, 0.15)', color: 'var(--accent-emerald)' }}>
              <BarChart3 size={20} />
            </div>
            <h3 className="card-title">Dynamic Visualizations</h3>
          </div>
          <p className="card-desc">
            Interactive charts, filterable frequency tables, and sanitized CSV exports rendered natively through React.
          </p>
        </div>
      </div>

      {/* Footer */}
      <footer className="footer">
        <p>Word Intelligence v0.4 — Engineered for Big Data Analytics & NLP. Phase 1 Foundation Verified.</p>
      </footer>
    </div>
  );
}
