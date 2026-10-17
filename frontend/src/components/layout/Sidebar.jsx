import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Globe,
  Clock,
  Settings,
  Layers,
} from 'lucide-react';
import StatusBadge from '../StatusBadge';

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/analyze', label: 'Analyze Text', icon: FileText },
  { to: '/documents', label: 'Documents', icon: Upload },
  { to: '/url', label: 'Webpage URL', icon: Globe },
  { to: '/history', label: 'History', icon: Clock },
  { to: '/settings', label: 'Settings', icon: Settings },
];

export default function Sidebar({ healthState }) {
  return (
    <aside className="sidebar">
      {/* Brand */}
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Layers size={22} color="#ffffff" />
        </div>
        <div className="sidebar-brand-text">
          <span className="sidebar-brand-title">Word Intelligence</span>
          <span className="brand-version">v0.4</span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/'}
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'active' : ''}`
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      {/* Bottom Status */}
      <div className="sidebar-footer">
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
      </div>
    </aside>
  );
}

export { NAV_ITEMS };
