import React, { useState, useEffect } from 'react';
import { Link, useOutletContext } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Globe,
  ArrowRight,
  BarChart2,
  Sparkles,
  Shield,
  Database,
  Cpu,
  Server,
  Zap,
  Activity,
  Clock,
  CheckCircle2,
  ExternalLink,
  Image as ImageIcon,
} from 'lucide-react';
import { fetchHistoryStats, fetchHistory } from '../services/api';

const QUICK_ACTIONS = [
  {
    to: '/analyze',
    icon: FileText,
    color: 'var(--primary)',
    bg: 'rgba(99, 102, 241, 0.12)',
    border: 'rgba(99, 102, 241, 0.25)',
    title: 'Analyze Text',
    desc: 'Paste or type raw text for word frequency, sentiment, bigrams, and NLP analysis.',
    tags: ['Frequency Ranking', 'Bigrams', 'Sentiment NLP'],
    actionText: 'Open Workspace',
  },
  {
    to: '/documents',
    icon: Upload,
    color: 'var(--accent-emerald)',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.25)',
    title: 'Upload Documents',
    desc: 'Upload multi-page PDFs, Word DOCX, or TXT files for automated text extraction.',
    tags: ['PDF (pypdf)', 'DOCX', 'TXT Support'],
    actionText: 'Upload Files',
  },
  {
    to: '/url',
    icon: Globe,
    color: 'var(--accent-cyan)',
    bg: 'rgba(6, 182, 212, 0.12)',
    border: 'rgba(6, 182, 212, 0.25)',
    title: 'Analyze Webpage',
    desc: 'Extract and analyze text from public websites protected by anti-SSRF DNS pinning.',
    tags: ['SSRF Shield', 'DNS Validation', 'HTML Cleaner'],
    actionText: 'Extract Webpage',
  },
  {
    to: '/images',
    icon: ExternalLink,
    color: 'var(--accent-amber)',
    bg: 'rgba(245, 158, 11, 0.12)',
    border: 'rgba(245, 158, 11, 0.25)',
    title: 'Image OCR Extraction',
    desc: 'Upload photos, screenshots, or scanned images to extract and analyze printed text.',
    tags: ['Tesseract OCR', 'PNG/JPG/WEBP', 'Linguistic NLP'],
    actionText: 'Extract Image',
  },
];

export default function DashboardPage() {
  const context = useOutletContext() || {};
  const healthState = context.healthState || { status: 'checking', latencyMs: null };

  const [stats, setStats] = useState(null);
  const [recentItems, setRecentItems] = useState([]);
  const [isLoadingFeed, setIsLoadingFeed] = useState(true);

  useEffect(() => {
    let isMounted = true;
    async function loadDashboardData() {
      try {
        const [statsRes, historyRes] = await Promise.all([
          fetchHistoryStats(),
          fetchHistory({ skip: 0, limit: 4 }),
        ]);

        if (isMounted) {
          if (statsRes.success) setStats(statsRes.data);
          if (historyRes.success) setRecentItems(historyRes.data.items || []);
        }
      } catch (err) {
        // graceful fallback to empty states
      } finally {
        if (isMounted) setIsLoadingFeed(false);
      }
    }
    loadDashboardData();
    return () => {
      isMounted = false;
    };
  }, []);

  const renderSentimentBadge = (label) => {
    if (!label) return null;
    const isPositive = label.toLowerCase() === 'positive';
    const isNegative = label.toLowerCase() === 'negative';
    const bg = isPositive
      ? 'rgba(16, 185, 129, 0.15)'
      : isNegative
      ? 'rgba(244, 63, 94, 0.15)'
      : 'rgba(245, 158, 11, 0.15)';
    const color = isPositive ? '#34d399' : isNegative ? '#fb7185' : '#fbbf24';

    return (
      <span
        style={{
          display: 'inline-block',
          padding: '0.15rem 0.5rem',
          borderRadius: '999px',
          fontSize: '0.7rem',
          fontWeight: 600,
          background: bg,
          color: color,
          textTransform: 'capitalize',
        }}
      >
        {label}
      </span>
    );
  };

  const renderSourceIcon = (sourceType) => {
    switch (sourceType) {
      case 'file':
        return <Upload size={16} color="var(--accent-emerald)" />;
      case 'url':
        return <Globe size={16} color="var(--accent-cyan)" />;
      case 'image':
        return <ImageIcon size={16} color="var(--accent-amber)" />;
      default:
        return <FileText size={16} color="var(--primary)" />;
    }
  };

  return (
    <div className="page-content">
      <PageHeader
        icon={<LayoutDashboard size={22} color="var(--primary)" />}
        title="Dashboard"
        description="Unified NLP and big-data text analytics overview. Select a workspace or review operational metrics."
      />

      {/* Hero Welcome Banner */}
      <div className="dashboard-hero-banner">
        <div className="dashboard-hero-text">
          <h1>Word Intelligence Engine</h1>
          <p>
            High-performance linguistic statistics, sentiment analysis, bigram frequencies, and
            distributed processing powered by Python and Apache PySpark.
          </p>
        </div>
        <div className="dashboard-hero-badges">
          <div className={`hero-pill ${healthState.status === 'connected' ? 'online' : ''}`}>
            <Activity size={13} />
            <span>Backend: {healthState.status === 'connected' ? 'Online' : 'Checking'}</span>
            {healthState.latencyMs !== null && <span>({healthState.latencyMs}ms)</span>}
          </div>
          <div className="hero-pill online">
            <Database size={13} />
            <span>MySQL Storage: Active</span>
          </div>
          <div className="hero-pill">
            <Server size={13} color="var(--accent-cyan)" />
            <span>PySpark: Spark 4.2</span>
          </div>
        </div>
      </div>

      {/* Real-time KPI Stats Grid */}
      <div className="dashboard-stats-grid">
        <div className="dashboard-stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(99, 102, 241, 0.12)' }}>
            <Database size={22} color="var(--primary)" />
          </div>
          <div className="stat-info">
            <span className="stat-label">Analyses Saved</span>
            <span className="stat-value">{stats ? stats.total_runs : '—'}</span>
            <span className="stat-sub">Persisted in MySQL history</span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(16, 185, 129, 0.12)' }}>
            <BarChart2 size={22} color="var(--accent-emerald)" />
          </div>
          <div className="stat-info">
            <span className="stat-label">Words Analyzed</span>
            <span className="stat-value">
              {stats && stats.total_words ? stats.total_words.toLocaleString() : '—'}
            </span>
            <span className="stat-sub">Aggregated word tokens</span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(6, 182, 212, 0.12)' }}>
            <Zap size={22} color="var(--accent-cyan)" />
          </div>
          <div className="stat-info">
            <span className="stat-label">Engine Latency</span>
            <span className="stat-value">
              {healthState.latencyMs !== null ? `${healthState.latencyMs} ms` : '< 50ms'}
            </span>
            <span className="stat-sub">Python in-memory response</span>
          </div>
        </div>

        <div className="dashboard-stat-card">
          <div className="stat-icon-wrapper" style={{ background: 'rgba(245, 158, 11, 0.12)' }}>
            <Shield size={22} color="var(--accent-amber)" />
          </div>
          <div className="stat-info">
            <span className="stat-label">Security Shield</span>
            <span className="stat-value" style={{ fontSize: '1.25rem', color: 'var(--accent-emerald)' }}>
              Active
            </span>
            <span className="stat-sub">Rate limits & SSRF pinning</span>
          </div>
        </div>
      </div>

      {/* Quick Launch Workspaces */}
      <div>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: '0.85rem',
          }}
        >
          <span
            style={{
              fontSize: '0.75rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              color: 'var(--text-dim)',
            }}
          >
            Analysis Workspaces
          </span>
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
            Select an ingestion method
          </span>
        </div>

        <div className="dashboard-actions-grid">
          {QUICK_ACTIONS.map(({ to, icon: Icon, color, bg, border, title, desc, tags, actionText }) => (
            <Link
              key={to}
              to={to}
              className="dashboard-action-card"
              style={{
                '--action-bg': bg,
                '--action-border': border,
                flexDirection: 'column',
                alignItems: 'flex-start',
                gap: '1rem',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                <div className="dashboard-action-icon" style={{ background: bg, borderColor: border }}>
                  <Icon size={24} color={color} />
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--primary)', fontSize: '0.8125rem', fontWeight: 600 }}>
                  <span>{actionText}</span>
                  <ArrowRight size={14} className="dashboard-action-arrow" />
                </div>
              </div>

              <div className="dashboard-action-body">
                <h3 className="dashboard-action-title" style={{ fontSize: '1.15rem' }}>{title}</h3>
                <p className="dashboard-action-desc" style={{ marginBottom: '0.5rem' }}>{desc}</p>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', width: '100%', paddingTop: '0.5rem', borderTop: '1px solid var(--border-subtle)' }}>
                {tags.map((tag, idx) => (
                  <span key={idx} className="feature-tag-chip">
                    {tag}
                  </span>
                ))}
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Recent Analyses Activity Section */}
      <div className="recent-activity-card">
        <div className="recent-activity-header">
          <div className="recent-activity-title">
            <Clock size={18} color="var(--accent-amber)" />
            <span>Recent Analysis Runs</span>
          </div>
          <Link to="/history" className="recent-activity-link">
            <span>View Full History</span>
            <ExternalLink size={13} />
          </Link>
        </div>

        {isLoadingFeed ? (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-dim)', fontSize: '0.875rem' }}>
            Loading recent activity...
          </div>
        ) : recentItems.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
            {recentItems.map((item) => (
              <div key={item.id} className="recent-item-row">
                <div className="recent-item-left">
                  <div
                    style={{
                      width: '32px',
                      height: '32px',
                      borderRadius: 'var(--radius-sm)',
                      background: 'rgba(255, 255, 255, 0.05)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    {renderSourceIcon(item.source_type)}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.15rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <span className="recent-item-name">{item.source_name}</span>
                      <span
                        style={{
                          fontSize: '0.65rem',
                          fontWeight: 600,
                          padding: '0.1rem 0.4rem',
                          borderRadius: '999px',
                          background: 'rgba(99, 102, 241, 0.15)',
                          color: '#818cf8',
                        }}
                      >
                        {item.engine === 'pyspark' ? 'Spark' : 'Python'}
                      </span>
                    </div>
                    <span className="recent-item-meta">
                      {item.total_words} tokens • {item.unique_words} unique •{' '}
                      {new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                </div>

                <div className="recent-item-right">
                  {renderSentimentBadge(item.sentiment_label)}
                  <Link
                    to="/history"
                    className="btn-secondary"
                    style={{
                      padding: '0.35rem 0.65rem',
                      fontSize: '0.75rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.3rem',
                    }}
                  >
                    <span>Inspect</span>
                    <ArrowRight size={12} />
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div
            style={{
              padding: '2rem',
              textAlign: 'center',
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: '0.75rem',
            }}
          >
            <div
              style={{
                width: '44px',
                height: '44px',
                borderRadius: '50%',
                background: 'rgba(99, 102, 241, 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <FileText size={20} color="var(--primary)" />
            </div>
            <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
              No analyses recorded yet. Run your first text, document, or webpage analysis above!
            </p>
            <Link
              to="/analyze"
              className="btn-secondary"
              style={{ fontSize: '0.8125rem', marginTop: '0.25rem' }}
            >
              Try Instant Text Analysis →
            </Link>
          </div>
        )}
      </div>

      {/* Dual Engine & Security Capability Grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
          gap: '1.25rem',
        }}
      >
        {/* Python In-Memory Card */}
        <div className="dashboard-section" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Cpu size={18} color="var(--primary)" />
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Python In-Memory Engine
            </span>
            <span className="dashboard-engine-badge python" style={{ marginLeft: 'auto' }}>
              Default
            </span>
          </div>
          <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Microsecond tokenization utilizing Python Counter structures, TextBlob polarity scoring, and
            stopword elimination optimized for rapid interactive web responses.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.25rem' }}>
            <span className="feature-tag-chip">Regex Tokenizer</span>
            <span className="feature-tag-chip">TextBlob Sentiment</span>
            <span className="feature-tag-chip">NLTK Stopwords</span>
            <span className="feature-tag-chip">Latency &lt; 50ms</span>
          </div>
        </div>

        {/* PySpark Engine Card */}
        <div className="dashboard-section" style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <Server size={18} color="var(--accent-cyan)" />
            <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-main)' }}>
              Apache PySpark Engine
            </span>
            <span className="dashboard-engine-badge spark" style={{ marginLeft: 'auto' }}>
              Spark 4.2
            </span>
          </div>
          <p style={{ margin: 0, fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Distributed Big Data engine utilizing PySpark DataFrames, lazy transformations, and parallel map-reduce
            grouping with automated graceful fallback to native Python.
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.35rem', marginTop: '0.25rem' }}>
            <span className="feature-tag-chip">Distributed DataFrames</span>
            <span className="feature-tag-chip">Map-Reduce</span>
            <span className="feature-tag-chip">Graceful Fallback</span>
            <span className="feature-tag-chip">JVM Bridge</span>
          </div>
        </div>
      </div>
    </div>
  );
}
