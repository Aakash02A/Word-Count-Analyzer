import React from 'react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Globe,
  ArrowRight,
  BarChart2,
  Sparkles,
  Shield,
} from 'lucide-react';

const QUICK_ACTIONS = [
  {
    to: '/analyze',
    icon: FileText,
    color: 'var(--primary)',
    bg: 'rgba(99, 102, 241, 0.12)',
    border: 'rgba(99, 102, 241, 0.25)',
    title: 'Analyze Text',
    desc: 'Paste or type raw text for word frequency, sentiment, bigram, and NLP analysis.',
  },
  {
    to: '/documents',
    icon: Upload,
    color: 'var(--accent-emerald)',
    bg: 'rgba(16, 185, 129, 0.12)',
    border: 'rgba(16, 185, 129, 0.25)',
    title: 'Upload Document',
    desc: 'Upload TXT, PDF, or DOCX files for automatic text extraction and analysis.',
  },
  {
    to: '/url',
    icon: Globe,
    color: 'var(--accent-cyan)',
    bg: 'rgba(6, 182, 212, 0.12)',
    border: 'rgba(6, 182, 212, 0.25)',
    title: 'Analyze Webpage',
    desc: 'Provide a public URL and the system will safely fetch and analyze its text content.',
  },
];

const CAPABILITIES = [
  { icon: BarChart2, label: 'Word frequency ranking with search & sort' },
  { icon: Sparkles, label: 'Sentiment analysis & noun phrase extraction' },
  { icon: Shield, label: 'SSRF-protected URL fetching with DNS validation' },
];

export default function DashboardPage() {
  return (
    <div className="page-content">
      <PageHeader
        icon={<LayoutDashboard size={22} color="var(--primary)" />}
        title="Dashboard"
        description="Word Intelligence analytics overview. Select an analysis method below to get started."
      />

      {/* Quick Action Cards */}
      <div className="dashboard-actions-grid">
        {QUICK_ACTIONS.map(({ to, icon: Icon, color, bg, border, title, desc }) => (
          <Link key={to} to={to} className="dashboard-action-card" style={{ '--action-bg': bg, '--action-border': border }}>
            <div className="dashboard-action-icon" style={{ background: bg, borderColor: border }}>
              <Icon size={24} color={color} />
            </div>
            <div className="dashboard-action-body">
              <h3 className="dashboard-action-title">{title}</h3>
              <p className="dashboard-action-desc">{desc}</p>
            </div>
            <ArrowRight size={18} color="var(--text-dim)" className="dashboard-action-arrow" />
          </Link>
        ))}
      </div>

      {/* Platform Capabilities */}
      <div className="dashboard-section">
        <h3 className="dashboard-section-title">Platform Capabilities</h3>
        <div className="dashboard-capabilities">
          {CAPABILITIES.map(({ icon: Icon, label }, idx) => (
            <div key={idx} className="dashboard-capability">
              <Icon size={16} color="var(--accent-cyan)" />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Engine Info */}
      <div className="dashboard-section">
        <h3 className="dashboard-section-title">Supported Engines</h3>
        <div className="dashboard-engines">
          <div className="dashboard-engine-card">
            <span className="dashboard-engine-badge python">Python</span>
            <span className="dashboard-engine-label">In-Memory (Ultra Fast)</span>
          </div>
          <div className="dashboard-engine-card">
            <span className="dashboard-engine-badge spark">PySpark</span>
            <span className="dashboard-engine-label">Apache Spark DataFrame</span>
          </div>
        </div>
      </div>
    </div>
  );
}
