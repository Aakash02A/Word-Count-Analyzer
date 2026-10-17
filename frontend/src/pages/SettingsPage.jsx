import React from 'react';
import { useOutletContext } from 'react-router-dom';
import { Settings, Server, Cpu, Database, RefreshCw, CheckCircle2, XCircle, Clock } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import SystemDiagnostics from '../components/SystemDiagnostics';

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

  return (
    <div className="page-content">
      <PageHeader
        icon={<Settings size={22} color="var(--primary)" />}
        title="Settings & System Diagnostics"
        description="Inspect backend connectivity, engine configurations, diagnostic metadata, and operational status."
      >
        {refreshHealth && (
          <button
            onClick={refreshHealth}
            className="btn-secondary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <RefreshCw size={14} />
            <span>Check Connectivity</span>
          </button>
        )}
      </PageHeader>

      {/* Diagnostics Panel */}
      <SystemDiagnostics healthState={healthState} activePhase="Phase 5.5: UI Navigation" />

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
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>local[*] / Cluster</span>
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
              <span style={{ fontSize: '0.75rem', color: 'var(--accent-amber)', fontWeight: 600 }}>Phase 6 Target</span>
            </div>
          </div>
          <p style={{ margin: '0 0 1rem 0', fontSize: '0.8125rem', color: 'var(--text-muted)', lineHeight: '1.5' }}>
            Relational storage for archiving analysis runs, execution metadata, word distributions, and sentiment metrics with SQLAlchemy ORM and Alembic migrations.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.8125rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Schema Version:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>v0.4 (Pending Migration)</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-dim)' }}>
              <span>Status:</span>
              <span style={{ color: 'var(--text-main)', fontWeight: 500 }}>Ready for Phase 6</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
