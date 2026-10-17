import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import useHealth from './hooks/useHealth';
import AppLayout from './components/layout/AppLayout';
import DashboardPage from './pages/DashboardPage';
import AnalyzePage from './pages/AnalyzePage';
import DocumentsPage from './pages/DocumentsPage';
import UrlAnalysisPage from './pages/UrlAnalysisPage';
import HistoryPage from './pages/HistoryPage';
import SettingsPage from './pages/SettingsPage';
import NotFoundPage from './pages/NotFoundPage';

/**
 * Main application router container.
 * Hosts navigation, route hierarchy, and shared health polling.
 */
export default function App() {
  const { healthState, fetchHealth } = useHealth();

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<AppLayout healthState={healthState} refreshHealth={fetchHealth} />}
        >
          <Route index element={<DashboardPage />} />
          <Route path="analyze" element={<AnalyzePage />} />
          <Route path="documents" element={<DocumentsPage />} />
          <Route path="url" element={<UrlAnalysisPage />} />
          <Route path="history" element={<HistoryPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
