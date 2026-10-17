import React from 'react';
import { Layers, RefreshCw } from 'lucide-react';
import StatusBadge from './StatusBadge';

export default function Header({ healthState, isRefreshing, onRefresh }) {
  return (
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
          onClick={onRefresh}
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
  );
}
