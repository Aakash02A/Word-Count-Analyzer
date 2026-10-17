import React from 'react';

/**
 * StatusBadge component
 * Displays connection state with pulsing indicators
 */
export default function StatusBadge({ status, message }) {
  let badgeClass = 'status-badge';
  let label = message || 'Checking...';

  if (status === 'connected') {
    badgeClass += ' connected';
    label = message || 'Backend Online';
  } else if (status === 'disconnected') {
    badgeClass += ' disconnected';
    label = message || 'Backend Offline';
  } else {
    badgeClass += ' checking';
    label = message || 'Connecting...';
  }

  return (
    <div className={badgeClass} title={`Backend connection: ${status}`}>
      <span className="status-dot"></span>
      <span>{label}</span>
    </div>
  );
}
