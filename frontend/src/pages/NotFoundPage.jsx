import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, Home, ArrowLeft } from 'lucide-react';

export default function NotFoundPage() {
  return (
    <div
      className="page-content"
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '60vh',
        textAlign: 'center',
      }}
    >
      <div
        style={{
          width: '72px',
          height: '72px',
          borderRadius: '50%',
          background: 'rgba(244, 63, 94, 0.1)',
          border: '1px solid rgba(244, 63, 94, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.5rem',
        }}
      >
        <AlertTriangle size={36} color="var(--accent-rose)" />
      </div>

      <h1 style={{ fontSize: '2.5rem', fontWeight: 800, margin: '0 0 0.5rem 0', color: 'var(--text-main)' }}>
        404
      </h1>
      <h2 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0 0 1rem 0', color: 'var(--text-muted)' }}>
        Page Not Found
      </h2>
      <p style={{ maxWidth: '420px', margin: '0 0 2rem 0', color: 'var(--text-dim)', fontSize: '0.9rem', lineHeight: '1.6' }}>
        The route you requested does not exist or may have been relocated in the v0.4 navigation refactor.
      </p>

      <div style={{ display: 'flex', gap: '1rem' }}>
        <Link to="/" className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
          <Home size={16} />
          <span>Back to Dashboard</span>
        </Link>
        <Link to="/analyze" className="btn-secondary" style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem', textDecoration: 'none' }}>
          <ArrowLeft size={16} />
          <span>Analyze Text</span>
        </Link>
      </div>
    </div>
  );
}
