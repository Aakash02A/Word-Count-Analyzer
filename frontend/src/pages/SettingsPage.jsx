import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Settings, Server, Cpu, Database, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import SystemDiagnostics from '../components/SystemDiagnostics';
import { checkReadiness } from '../services/api';

export default function SettingsPage() {
  const context = useOutletContext() || {};
  const healthState = context.healthState || {
    status: 'checking',
    data: null,
    error: null,
    latencyMs: null,
    lastChecked: null,
  };
  const refreshHealth = context.refreshHealth;

  const [readiness, setReadiness] = useState(null);
  const [isCheckingReadiness, setIsCheckingReadiness] = useState(false);

  const fetchReadiness = async () => {
    setIsCheckingReadiness(true);
    const res = await checkReadiness();
    setIsCheckingReadiness(false);
    if (res.success) {
      setReadiness(res.data);
    }
  };

  useEffect(() => {
    fetchReadiness();
  }, []);

  const handleFullRefresh = () => {
    if (refreshHealth) refreshHealth();
    fetchReadiness();
  };

  const isDbConnected = readiness?.database?.connected;
  const dbLatency = readiness?.database?.latency_ms;

  return (
    <div className="page-content">
      <PageHeader
        icon={<Settings size={22} color="var(--primary)" />}
        title="Settings & System Diagnostics"
        description="Inspect backend connectivity, engine configurations, diagnostic metadata, and operational status."
      >
        <button
          onClick={handleFullRefresh}
          className="btn-secondary"
          style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <RefreshCw size={14} className={isCheckingReadiness ? 'spin' : ''} />
          <span>Check Connectivity</span>
        </button>
      </PageHeader>

      {/* Diagnostics Panel */}
      <SystemDiagnostics healthState={healthState} activePhase="Phase 6: MySQL Database & History" />

      {/* Engine & Architecture Cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
          gap: '1.5rem',
          marginTop: '1.5rem',
        }}
      >
        {/* Python Engine Card */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.5rem',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(99, 102, 241, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Cpu size={20} color="var(--primary)" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>Python In-Memory Engine</h4>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-emerald)', fontWeight: 600 }}>Active & Default</span>
            </div>
          </div>
          <p style={{ margin: '0 0 1rem 0', fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            High-speed native Python engine leveraging regex tokenizers, Counter maps, TextBlob NLP heurism, and optimized memory processing for rapid response times.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Target Latency:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>&lt; 50ms</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Memory Footprint:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Low</span>
            </div>
          </div>
        </div>

        {/* PySpark Engine Card */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.5rem',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(6, 182, 212, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Server size={20} color="var(--accent-cyan)" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>Apache PySpark Engine</h4>
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-cyan)', fontWeight: 600 }}>Available (Distributed)</span>
            </div>
          </div>
          <p style={{ margin: '0 0 1rem 0', fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Distributed big-data computation engine using PySpark DataFrames, lazy transformations, and map-reduce aggregation for large-scale document collections.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Execution Mode:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>local[2] / Spark 4.2</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Fallback Strategy:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Graceful Python fallback</span>
            </div>
          </div>
        </div>

        {/* Database Persistence Card */}
        <div
          style={{
            background: 'var(--bg-card)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '1.5rem',
            boxShadow: 'var(--shadow-card)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div
              style={{
                width: '38px',
                height: '38px',
                borderRadius: 'var(--radius-sm)',
                background: 'rgba(245, 158, 11, 0.12)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Database size={20} color="var(--accent-amber)" />
            </div>
            <div>
              <h4 style={{ margin: 0, fontSize: '0.95rem', color: 'var(--text-main)' }}>MySQL Relational Storage</h4>
              <span
                style={{
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  color: isDbConnected ? 'var(--accent-emerald)' : 'var(--accent-rose)',
                }}
              >
                {isDbConnected ? 'Connected (Online)' : 'Connecting / Offline'}
              </span>
            </div>
          </div>
          <p style={{ margin: '0 0 1rem 0', fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Relational storage archiving analysis runs, word metrics, and sentiment scores via SQLAlchemy ORM and Alembic migrations.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Database Name:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>
                {readiness?.database?.database || 'word_intelligence'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Latency:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>
                {dbLatency !== undefined && dbLatency !== null ? `${dbLatency} ms` : 'N/A'}
              </span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Schema Migrations:</span>
              <span style={{ color: 'var(--accent-emerald)', fontWeight: 500 }}>
                Alembic Head (Up to Date)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
