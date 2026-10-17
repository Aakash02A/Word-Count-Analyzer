import React, { useState, useEffect } from 'react';
import { checkHealth, analyzeText, analyzeFile, analyzeUrl, exportAnalysisCsv } from './services/api';
import Header from './components/Header';
import AnalysisWorkspace from './components/AnalysisWorkspace';
import MetricsCards from './components/MetricsCards';
import FrequencyTable from './components/FrequencyTable';
import WordFrequencyChart from './components/WordFrequencyChart';
import LengthDistribution from './components/LengthDistribution';
import LengthDistributionChart from './components/LengthDistributionChart';
import BigramPills from './components/BigramPills';
import SentimentCard from './components/SentimentCard';
import NounPhrasesPills from './components/NounPhrasesPills';
import SystemDiagnostics from './components/SystemDiagnostics';
import { Sparkles, FileText, Globe, Upload, Download, BarChart2, Table, Activity } from 'lucide-react';

const SAMPLE_TEXT = `Apache PySpark provides a robust, high-performance distributed DataFrame framework for big data processing. Word Intelligence integrates PySpark analytics with Natural Language Processing heuristics to transform unstructured content into structured insights. Analyzing token frequencies, bigrams, and word-length distributions allows researchers to understand linguistic patterns rapidly.`;

export default function App() {
  const [healthState, setHealthState] = useState({
    status: 'checking',
    data: null,
    error: null,
    latencyMs: null,
    lastChecked: null,
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Ingestion & options state
  const [inputMode, setInputMode] = useState('text'); // 'text' | 'file' | 'url'
  const [inputText, setInputText] = useState(SAMPLE_TEXT);
  const [selectedFile, setSelectedFile] = useState(null);
  const [inputUrl, setInputUrl] = useState('');
  const [topN, setTopN] = useState(10);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [engine, setEngine] = useState('python');

  // Execution state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  // Interactive Phase 5 view states
  const [freqViewMode, setFreqViewMode] = useState('table'); // 'table' | 'chart'
  const [lengthViewMode, setLengthViewMode] = useState('bars'); // 'bars' | 'chart'
  const [isExporting, setIsExporting] = useState(false);

  const fetchHealth = async () => {
    setIsRefreshing(true);
    const startTime = performance.now();
    const result = await checkHealth();
    const endTime = performance.now();
    const latency = Math.round(endTime - startTime);

    if (result.success) {
      setHealthState({
        status: 'connected',
        data: result.data,
        error: null,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    } else {
      setHealthState({
        status: 'disconnected',
        data: null,
        error: result.error,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    }
    setIsRefreshing(false);
  };

  const handleAnalyze = async () => {
    setAnalysisError(null);
    setIsAnalyzing(true);

    let result;

    if (inputMode === 'text') {
      if (!inputText.trim()) {
        setAnalysisError('Please enter or paste text to analyze.');
        setIsAnalyzing(false);
        return;
      }
      result = await analyzeText({
        text: inputText,
        top_n: topN,
        case_sensitive: caseSensitive,
        engine,
      });
    } else if (inputMode === 'file') {
      if (!selectedFile) {
        setAnalysisError('Please choose a document (.txt, .pdf, or .docx) to upload.');
        setIsAnalyzing(false);
        return;
      }
      result = await analyzeFile({
        file: selectedFile,
        top_n: topN,
        case_sensitive: caseSensitive,
        engine,
      });
    } else if (inputMode === 'url') {
      if (!inputUrl.trim()) {
        setAnalysisError('Please enter a public HTTP/HTTPS webpage URL to analyze.');
        setIsAnalyzing(false);
        return;
      }
      result = await analyzeUrl({
        url: inputUrl,
        top_n: topN,
        case_sensitive: caseSensitive,
        engine,
      });
    }

    if (result && result.success) {
      setAnalysisResult(result.data);
    } else if (result) {
      setAnalysisError(result.error);
    }
    setIsAnalyzing(false);
  };

  const handleClear = () => {
    if (inputMode === 'text') setInputText('');
    else if (inputMode === 'file') setSelectedFile(null);
    else if (inputMode === 'url') setInputUrl('');
    setAnalysisResult(null);
    setAnalysisError(null);
  };

  const handleExportCsv = async () => {
    if (!analysisResult) return;
    setIsExporting(true);
    await exportAnalysisCsv(analysisResult);
    setIsExporting(false);
  };

  useEffect(() => {
    fetchHealth();
    handleAnalyze();
  }, []);

  return (
    <div className="app-container">
      {/* Modular Header */}
      <Header
        healthState={healthState}
        isRefreshing={isRefreshing}
        onRefresh={fetchHealth}
      />

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-tagline">
          <Sparkles size={16} />
          <span>Big Data & NLP Intelligence Platform</span>
        </div>
        <h2 className="hero-title">
          Unstructured Content into<br />Actionable Linguistic Insights
        </h2>
        <p className="hero-subtitle">
          Phase 5 Interactive Dashboard & CSV Export. High-performance charts, searchable ranking distributions, and formula-safe RFC 4180 export.
        </p>
      </section>

      {/* Modular Workspace */}
      <AnalysisWorkspace
        inputMode={inputMode}
        setInputMode={setInputMode}
        inputText={inputText}
        setInputText={setInputText}
        selectedFile={selectedFile}
        setSelectedFile={setSelectedFile}
        inputUrl={inputUrl}
        setInputUrl={setInputUrl}
        caseSensitive={caseSensitive}
        setCaseSensitive={setCaseSensitive}
        topN={topN}
        setTopN={setTopN}
        engine={engine}
        setEngine={setEngine}
        isAnalyzing={isAnalyzing}
        onAnalyze={handleAnalyze}
        onLoadSample={() => setInputText(SAMPLE_TEXT)}
        onClear={handleClear}
        error={analysisError}
      />

      {/* Analysis Results View */}
      {analysisResult && (
        <div className="results-container">
          {/* Action & Meta Header Bar */}
          <div className="results-header-bar">
            <div className="results-meta-badge">
              {analysisResult.metadata.source_type === 'file' ? (
                <Upload size={16} color="var(--accent-emerald)" />
              ) : analysisResult.metadata.source_type === 'url' ? (
                <Globe size={16} color="var(--accent-cyan)" />
              ) : (
                <FileText size={16} color="var(--primary)" />
              )}
              <span>
                Source: <strong style={{ color: 'var(--text-main)' }}>{analysisResult.metadata.source_name || 'Direct Input'}</strong>
                {' '}({analysisResult.metadata.source_type.toUpperCase()})
              </span>
              <span style={{ color: 'var(--border-subtle)' }}>•</span>
              <span style={{ fontFamily: 'monospace', color: 'var(--text-dim)' }}>
                {analysisResult.metadata.engine_used} ({analysisResult.metadata.execution_time_ms || 0}ms)
              </span>
            </div>

            <button
              className="btn-export"
              onClick={handleExportCsv}
              disabled={isExporting}
            >
              <Download size={15} />
              <span>{isExporting ? 'Exporting...' : 'Export CSV Report'}</span>
            </button>
          </div>

          {/* Metric Summary Cards */}
          <MetricsCards result={analysisResult} />

          {/* Two-Column Detail View */}
          <div className="results-columns">
            {/* Left Column: Frequency Ranking (Table or Visual Chart) & Noun Phrases */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.5rem', gap: '0.25rem' }}>
                  <button
                    className={`view-toggle-btn ${freqViewMode === 'table' ? 'active' : ''}`}
                    onClick={() => setFreqViewMode('table')}
                  >
                    <Table size={13} />
                    <span>Table</span>
                  </button>
                  <button
                    className={`view-toggle-btn ${freqViewMode === 'chart' ? 'active' : ''}`}
                    onClick={() => setFreqViewMode('chart')}
                  >
                    <BarChart2 size={13} />
                    <span>Chart</span>
                  </button>
                </div>

                {freqViewMode === 'table' ? (
                  <FrequencyTable topWords={analysisResult.top_words} />
                ) : (
                  <WordFrequencyChart topWords={analysisResult.top_words} />
                )}
              </div>

              <NounPhrasesPills phrases={analysisResult.noun_phrases} />
            </div>

            {/* Right Column: Sentiment, Length Distribution (Bars or Chart Curve), Bigrams */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <SentimentCard sentiment={analysisResult.sentiment} />

              <div>
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '0.5rem', gap: '0.25rem' }}>
                  <button
                    className={`view-toggle-btn ${lengthViewMode === 'bars' ? 'active' : ''}`}
                    onClick={() => setLengthViewMode('bars')}
                  >
                    <Table size={13} />
                    <span>Bars</span>
                  </button>
                  <button
                    className={`view-toggle-btn ${lengthViewMode === 'chart' ? 'active' : ''}`}
                    onClick={() => setLengthViewMode('chart')}
                  >
                    <Activity size={13} />
                    <span>Curve</span>
                  </button>
                </div>

                {lengthViewMode === 'bars' ? (
                  <LengthDistribution distribution={analysisResult.word_length_distribution} />
                ) : (
                  <LengthDistributionChart distribution={analysisResult.word_length_distribution} />
                )}
              </div>

              <BigramPills bigrams={analysisResult.bigrams} />
            </div>
          </div>
        </div>
      )}

      {/* System Diagnostics */}
      <SystemDiagnostics healthState={healthState} activePhase="Phase 5: Interactive Dashboard & CSV Export" />

      {/* Footer */}
      <footer className="footer">
        <p>Word Intelligence v0.4 — Big Data & NLP Analytics Engine.</p>
      </footer>
    </div>
  );
}
