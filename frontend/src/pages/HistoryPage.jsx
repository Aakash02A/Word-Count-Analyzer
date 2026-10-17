import React, { useState, useEffect, useCallback } from 'react';
import {
  Clock,
  Database,
  Search,
  Filter,
  Trash2,
  Eye,
  RefreshCw,
  FileText,
  Upload,
  Globe,
  ArrowLeft,
  Calendar,
  Layers,
  Sparkles,
  BarChart2,
  AlertTriangle,
} from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import AnalysisResults from '../components/AnalysisResults';
import {
  fetchHistory,
  fetchHistoryStats,
  fetchHistoryDetail,
  deleteHistoryRecord,
  exportAnalysisCsv,
} from '../services/api';

export default function HistoryPage() {
  const [records, setRecords] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [search, setSearch] = useState('');
  const [sourceType, setSourceType] = useState('all');
  const [engine, setEngine] = useState('all');

  // Detail / Replay state
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [isLoadingDetail, setIsLoadingDetail] = useState(false);
  const [detailError, setDetailError] = useState(null);

  // Replay results view toggle states
  const [freqViewMode, setFreqViewMode] = useState('table');
  const [lengthViewMode, setLengthViewMode] = useState('bars');
  const [isExporting, setIsExporting] = useState(false);

  const loadHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [histRes, statsRes] = await Promise.all([
        fetchHistory({
          skip: 0,
          limit: 50,
          source_type: sourceType,
          engine: engine,
          search: search,
        }),
        fetchHistoryStats(),
      ]);

      if (histRes.success) {
        setRecords(histRes.data.items || []);
        setTotalCount(histRes.data.total || 0);
      } else {
        setError(histRes.error || 'Failed to retrieve analysis history.');
      }

      if (statsRes.success) {
        setStats(statsRes.data);
      }
    } catch (err) {
      setError(err.message || 'Error communicating with database.');
    } finally {
      setIsLoading(false);
    }
  }, [sourceType, engine, search]);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const handleViewDetail = async (id) => {
    setIsLoadingDetail(true);
    setDetailError(null);
    const res = await fetchHistoryDetail(id);
    setIsLoadingDetail(false);

    if (res.success) {
      setSelectedRecord(res.data);
      // scroll to top smoothly
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      setDetailError(res.error || `Could not load record #${id}`);
    }
  };

  const handleDelete = async (e, id) => {
    e.stopPropagation();
    if (!window.confirm(`Delete analysis record #${id}?`)) {
      return;
    }
    const res = await deleteHistoryRecord(id);
    if (res.success) {
      setRecords((prev) => prev.filter((r) => r.id !== id));
      setTotalCount((prev) => Math.max(0, prev - 1));
      if (selectedRecord && selectedRecord.id === id) {
        setSelectedRecord(null);
      }
    } else {
      alert(res.error || 'Failed to delete record.');
    }
  };

  const handleExportCsv = async () => {
    if (!selectedRecord?.result) return;
    setIsExporting(true);
    try {
      await exportAnalysisCsv(selectedRecord.result);
    } finally {
      setIsExporting(false);
    }
  };

  const renderSourceIcon = (type) => {
    switch (type) {
      case 'file':
        return <Upload size={14} color="var(--accent-emerald)" />;
      case 'url':
        return <Globe size={14} color="var(--accent-cyan)" />;
      case 'text':
      default:
        return <FileText size={14} color="var(--primary)" />;
    }
  };

  const renderSentimentBadge = (label) => {
    if (!label) return <span style={{ color: 'var(--text-dim)' }}>—</span>;
    const isPositive = label === 'positive';
    const isNegative = label === 'negative';
    const bg = isPositive
      ? 'rgba(16, 185, 129, 0.15)'
      : isNegative
      ? 'rgba(244, 63, 94, 0.15)'
      : 'rgba(245, 158, 11, 0.15)';
    const color = isPositive
      ? '#34d399'
      : isNegative
      ? '#fb7185'
      : '#fbbf24';

    return (
      <span
        style={{
          display: 'inline-block',
          padding: '0.15rem 0.55rem',
          borderRadius: '999px',
          fontSize: '0.75rem',
          fontWeight: 600,
          background: bg,
          color: color,
          textTransform: 'capitalize',
        }}
      >
        {label}
      </span>
    );
  };

  return (
    <div className="page-content">
      <PageHeader
        icon={<Clock size={22} color="var(--accent-amber)" />}
        title={selectedRecord ? `History Record #${selectedRecord.id}` : 'Analysis History'}
        description={
          selectedRecord
            ? `Viewing historical analysis results for ${selectedRecord.source_name} executed on ${new Date(
                selectedRecord.created_at,
              ).toLocaleString()}.`
            : 'Review, search, and replay previously executed text, document, and webpage linguistic analyses archived in MySQL.'
        }
      >
        {selectedRecord ? (
          <button
            onClick={() => setSelectedRecord(null)}
            className="btn-secondary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <ArrowLeft size={16} />
            <span>Back to History List</span>
          </button>
        ) : (
          <button
            onClick={loadHistory}
            className="btn-secondary"
            disabled={isLoading}
            style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
          >
            <RefreshCw size={14} className={isLoading ? 'spin' : ''} />
            <span>Refresh</span>
          </button>
        )}
      </PageHeader>

      {/* If Replay View is active */}
      {selectedRecord ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Header Info Bar */}
          <div
            style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-lg)',
              padding: '1.25rem 1.5rem',
              display: 'flex',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
              gap: '1rem',
              boxShadow: 'var(--shadow-card)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-sm)',
                  background: 'rgba(245, 158, 11, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Database size={22} color="var(--accent-amber)" />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '1rem' }}>
                    {selectedRecord.source_name}
                  </span>
                  <span
                    style={{
                      fontSize: '0.6875rem',
                      fontWeight: 600,
                      padding: '0.1rem 0.45rem',
                      borderRadius: '999px',
                      background: 'rgba(99, 102, 241, 0.15)',
                      color: '#818cf8',
                    }}
                  >
                    {selectedRecord.engine === 'pyspark' ? 'PySpark' : 'Python'}
                  </span>
                </div>
                <span style={{ fontSize: '0.8125rem', color: 'var(--text-dim)' }}>
                  Analyzed on {new Date(selectedRecord.created_at).toLocaleString()} • {selectedRecord.total_words} tokens
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <button
                onClick={handleExportCsv}
                disabled={isExporting}
                className="btn-export"
                title="Download CSV report"
              >
                <Upload size={14} style={{ transform: 'rotate(180deg)' }} />
                <span>{isExporting ? 'Exporting...' : 'Export CSV Report'}</span>
              </button>
            </div>
          </div>

          {/* Reconstructed Interactive Results */}
          {selectedRecord.result && (
            <AnalysisResults
              analysisResult={selectedRecord.result}
              freqViewMode={freqViewMode}
              setFreqViewMode={setFreqViewMode}
              lengthViewMode={lengthViewMode}
              setLengthViewMode={setLengthViewMode}
              isExporting={isExporting}
              onExportCsv={handleExportCsv}
            />
          )}
        </div>
      ) : (
        <>
          {/* Stats Bar */}
          {stats && (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '1rem',
              }}
            >
              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                }}
              >
                <div
                  style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(99, 102, 241, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Database size={20} color="var(--primary)" />
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Archived Runs
                  </span>
                  <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {stats.total_runs}
                  </h3>
                </div>
              </div>

              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                }}
              >
                <div
                  style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(16, 185, 129, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <BarChart2 size={20} color="var(--accent-emerald)" />
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Words Analyzed
                  </span>
                  <h3 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-main)' }}>
                    {stats.total_words_analyzed.toLocaleString()}
                  </h3>
                </div>
              </div>

              <div
                style={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  padding: '1.25rem',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '1rem',
                }}
              >
                <div
                  style={{
                    width: '42px',
                    height: '42px',
                    borderRadius: 'var(--radius-sm)',
                    background: 'rgba(6, 182, 212, 0.12)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <Calendar size={20} color="var(--accent-cyan)" />
                </div>
                <div>
                  <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Latest Run
                  </span>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-main)', marginTop: '0.2rem' }}>
                    {stats.latest_run_at ? new Date(stats.latest_run_at).toLocaleDateString() : 'N/A'}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Filter & Search Bar */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '1rem',
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '1rem 1.25rem',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flex: 1, minWidth: '240px' }}>
              <div style={{ position: 'relative', width: '100%', maxWidth: '340px' }}>
                <input
                  type="text"
                  className="table-search-input"
                  style={{ width: '100%', paddingLeft: '2.25rem' }}
                  placeholder="Search by source label..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                />
                <Search size={15} color="var(--text-dim)" style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)' }} />
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                <span>Source:</span>
                <select
                  className="table-sort-select"
                  value={sourceType}
                  onChange={(e) => setSourceType(e.target.value)}
                >
                  <option value="all">All Sources</option>
                  <option value="text">Raw Text</option>
                  <option value="file">Document File</option>
                  <option value="url">Webpage URL</option>
                </select>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                <span>Engine:</span>
                <select
                  className="table-sort-select"
                  value={engine}
                  onChange={(e) => setEngine(e.target.value)}
                >
                  <option value="all">All Engines</option>
                  <option value="python">Python In-Memory</option>
                  <option value="pyspark">Apache PySpark</option>
                </select>
              </div>
            </div>
          </div>

          {/* Records Table */}
          {error ? (
            <div
              style={{
                padding: '1.5rem',
                background: 'rgba(244, 63, 94, 0.1)',
                border: '1px solid rgba(244, 63, 94, 0.25)',
                borderRadius: 'var(--radius-md)',
                color: '#fb7185',
                display: 'flex',
                alignItems: 'center',
                gap: '0.75rem',
              }}
            >
              <AlertTriangle size={20} />
              <span>{error}</span>
            </div>
          ) : records.length === 0 ? (
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
              <Database size={36} color="var(--primary)" style={{ opacity: 0.8, marginBottom: '1rem' }} />
              <h3 style={{ margin: '0 0 0.5rem 0', color: 'var(--text-main)', fontSize: '1.15rem' }}>
                {search || sourceType !== 'all' || engine !== 'all'
                  ? 'No Matching Historical Records'
                  : 'No Analysis Runs Archived Yet'}
              </h3>
              <p style={{ margin: 0, color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                Run an analysis from the Analyze Text, Documents, or Webpage URL tabs to automatically archive results.
              </p>
            </div>
          ) : (
            <div
              style={{
                background: 'var(--bg-card)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-lg)',
                overflow: 'hidden',
                boxShadow: 'var(--shadow-card)',
              }}
            >
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table" style={{ margin: 0 }}>
                  <thead>
                    <tr>
                      <th style={{ width: '60px' }}>ID</th>
                      <th>Source</th>
                      <th>Timestamp</th>
                      <th>Engine</th>
                      <th style={{ textAlign: 'right' }}>Total Words</th>
                      <th style={{ textAlign: 'right' }}>Unique Words</th>
                      <th>Sentiment</th>
                      <th style={{ textAlign: 'center', width: '130px' }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {records.map((r) => (
                      <tr key={r.id}>
                        <td style={{ color: 'var(--text-dim)', fontFamily: 'monospace' }}>#{r.id}</td>
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                            {renderSourceIcon(r.source_type)}
                            <span style={{ fontWeight: 600, color: 'var(--text-main)', maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={r.source_name}>
                              {r.source_name}
                            </span>
                          </div>
                        </td>
                        <td style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                          {r.created_at ? new Date(r.created_at).toLocaleString() : 'N/A'}
                        </td>
                        <td>
                          <span
                            style={{
                              fontSize: '0.75rem',
                              fontWeight: 600,
                              color: r.engine === 'pyspark' ? 'var(--accent-cyan)' : 'var(--primary)',
                            }}
                          >
                            {r.engine === 'pyspark' ? 'PySpark' : 'Python'}
                          </span>
                        </td>
                        <td style={{ textAlign: 'right', fontWeight: 600, color: 'var(--text-main)' }}>
                          {r.total_words.toLocaleString()}
                        </td>
                        <td style={{ textAlign: 'right', color: 'var(--text-muted)' }}>
                          {r.unique_words.toLocaleString()}
                        </td>
                        <td>{renderSentimentBadge(r.sentiment_label)}</td>
                        <td style={{ textAlign: 'center' }}>
                          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                            <button
                              onClick={() => handleViewDetail(r.id)}
                              className="view-toggle-btn active"
                              style={{ padding: '0.3rem 0.6rem' }}
                              title="Replay full analysis"
                            >
                              <Eye size={14} />
                              <span>View</span>
                            </button>
                            <button
                              onClick={(e) => handleDelete(e, r.id)}
                              className="view-toggle-btn"
                              style={{ padding: '0.3rem 0.5rem', color: 'var(--accent-rose)' }}
                              title="Delete record"
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
