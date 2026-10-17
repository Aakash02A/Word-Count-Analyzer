import React from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import MobileNav from './MobileNav';

/**
 * Root application layout providing persistent sidebar,
 * mobile navigation, and scrollable main content area.
 */
export default function AppLayout({ healthState, refreshHealth }) {
  return (
    <div className="app-layout">
      {/* Desktop sidebar — hidden on mobile via CSS */}
      <Sidebar healthState={healthState} />

      {/* Mobile nav — visible only on small screens via CSS */}
      <MobileNav />

      {/* Main scrollable content area */}
      <main className="main-content">
        <Outlet context={{ healthState, refreshHealth }} />

        <footer className="footer">
          <p>Word Intelligence v0.4 — Big Data & NLP Analytics Engine.</p>
        </footer>
      </main>
    </div>
  );
}
