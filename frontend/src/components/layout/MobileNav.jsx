import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import { Menu, X, Layers } from 'lucide-react';
import { NAV_ITEMS } from './Sidebar';

export default function MobileNav() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Mobile Header Bar */}
      <div className="mobile-header">
        <div className="sidebar-brand" style={{ gap: '0.6rem' }}>
          <div className="brand-icon" style={{ width: '34px', height: '34px' }}>
            <Layers size={18} color="#ffffff" />
          </div>
          <span className="sidebar-brand-title" style={{ fontSize: '1.1rem' }}>Word Intelligence</span>
          <span className="brand-version">v0.4</span>
        </div>
        <button
          className="mobile-menu-btn"
          onClick={() => setIsOpen(!isOpen)}
          aria-label={isOpen ? 'Close navigation' : 'Open navigation'}
        >
          {isOpen ? <X size={22} /> : <Menu size={22} />}
        </button>
      </div>

      {/* Mobile Slide-Down Menu */}
      {isOpen && (
        <nav className="mobile-nav-menu">
          {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `mobile-nav-link ${isActive ? 'active' : ''}`
              }
              onClick={() => setIsOpen(false)}
            >
              <Icon size={18} />
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>
      )}
    </>
  );
}
