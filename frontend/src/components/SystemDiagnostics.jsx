import React from 'react';
import { Server } from 'lucide-react';

export default function SystemDiagnostics({ healthState, activePhase = 'Phase 2: Core Analytics' }) {
  return (
    <div className="diagnostics-panel">
      <div className="diagnostics-header">
        <div className="diagnostics-title">
          <Server size={18} color="var(--primary)" />
          <span>System Diagnostics & Health</span>
        </div>
        <span style={{ fontSize: '0.8125rem', color: 'var(--text-dim)' }}>
          Last checked: {healthState.lastChecked || 'Pending'}
        </span>
      </div>

      <div className="diagnostics-list">
        <div className="diag-item">
          <span className="diag-label">Backend Status</span>
          <span
            className="diag-val"
            style={{
              color:
                healthState.status === 'connected'
                  ? 'var(--accent-emerald)'
                  : healthState.status === 'disconnected'
                  ? 'var(--accent-rose)'
                  : 'var(--accent-amber)',
            }}
          >
            {healthState.status === 'connected'
              ? 'OK (200)'
              : healthState.status === 'disconnected'
              ? 'OFFLINE'
              : 'CHECKING'}
          </span>
        </div>

        <div className="diag-item">
          <span className="diag-label">API Service</span>
          <span className="diag-val">{healthState.data?.app || 'Word Intelligence'}</span>
        </div>

        <div className="diag-item">
          <span className="diag-label">Active Phase</span>
          <span className="diag-val" style={{ color: 'var(--accent-cyan)' }}>
            {activePhase}
          </span>
        </div>

        <div className="diag-item">
          <span className="diag-label">Latency</span>
          <span className="diag-val">
            {healthState.latencyMs !== null ? `${healthState.latencyMs} ms` : 'N/A'}
          </span>
        </div>

        <div className="diag-item">
          <span className="diag-label">Endpoint Contract</span>
          <span className="diag-val">POST /api/v1/analysis</span>
        </div>
      </div>
    </div>
  );
}
