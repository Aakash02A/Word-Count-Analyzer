import React from 'react';
import { Clock, Database, Search, Filter, AlertCircle, Sparkles } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';

export default function HistoryPage() {
  return (
    <div className="page-content">
      <PageHeader
        icon={<Clock size={22} color="var(--accent-amber)" />}
        title="Analysis History"
        description="Review previously executed linguistic analyses, search past runs, and view historical insights."
      />

      {/* Phase 6 Notice Banner */}
      <div
        style={{
          background: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem',
          marginBottom: '1.5rem',
          display: 'flex',
          gap: '1rem',
          alignItems: 'flex-start',
        }}
      >
        <Database size={24} color="var(--accent-amber)" style={{ flexShrink: 0, marginTop: '2px' }} />
        <div>
          <h4 style={{ margin: '0 0 0.35rem 0', color: 'var(--text-main)', fontSize: '0.95rem' }}>
            MySQL Database Persistence (Phase 6)
          </h4>
          <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.85rem', lineHeight: '1.5' }}>
            Analysis persistence is being introduced in Phase 6. Once database migrations are active,
            every analyzed document, URL, and raw text corpus will be automatically cataloged here with full metrics,
            exportable reports, and filtering capabilities.
          </p>
        </div>
      </div>

      {/* History Preview / Empty State */}
      <div
        style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          padding: '3rem 2rem',
          textAlign: 'center',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: 'rgba(99, 102, 241, 0.1)',
            border: '1px solid rgba(99, 102, 241, 0.25)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto 1.25rem auto',
          }}
        >
          <Clock size={28} color="var(--primary)" />
        </div>
        <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-main)', fontSize: '1.125rem' }}>
          No Stored Records Found
        </h3>
        <p style={{ margin: '0 auto 1.5rem auto', color: 'var(--text-muted)', maxWidth: '460px', fontSize: '0.875rem' }}>
          Run your first analysis from the Analyze Text, Documents, or Webpage URL sections.
          Database persistence will automatically archive future executions.
        </p>

        {/* Planned Features Preview */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1rem',
            maxWidth: '680px',
            margin: '2rem auto 0 auto',
            textAlign: 'left',
          }}
        >
          <div
            style={{
              padding: '1rem',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <Search size={16} color="var(--primary)" />
              <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>Full-Text Search</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Quickly locate runs by filename, source URL, or analyzed keywords.
            </p>
          </div>

          <div
            style={{
              padding: '1rem',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <Filter size={16} color="var(--accent-cyan)" />
              <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>Source Filtering</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Filter by engine (Python / PySpark), sentiment classification, or date range.
            </p>
          </div>

          <div
            style={{
              padding: '1rem',
              background: 'var(--bg-secondary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.35rem' }}>
              <Sparkles size={16} color="var(--accent-emerald)" />
              <span style={{ fontWeight: 600, fontSize: '0.8125rem' }}>Instant Replay</span>
            </div>
            <p style={{ margin: 0, fontSize: '0.75rem', color: 'var(--text-dim)' }}>
              Reload full interactive charts and tables from historical runs with one click.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
