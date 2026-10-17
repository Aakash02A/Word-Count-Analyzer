import React, { useState, useEffect } from 'react';
import { checkHealth, analyzeText, analyzeFile, analyzeUrl } from './services/api';
import Header from './components/Header';
import AnalysisWorkspace from './components/AnalysisWorkspace';
import MetricsCards from './components/MetricsCards';
import FrequencyTable from './components/FrequencyTable';
import LengthDistribution from './components/LengthDistribution';
import BigramPills from './components/BigramPills';
import SentimentCard from './components/SentimentCard';
import NounPhrasesPills from './components/NounPhrasesPills';
import SystemDiagnostics from './components/SystemDiagnostics';
import { Sparkles, FileText, Globe, Upload } from 'lucide-react';

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
          Phase 4 Multi-Source Ingestion & NLP Engine active. Ingest raw text, documents (TXT, PDF, DOCX), or secure URLs with sentiment and noun phrase intelligence.
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
          {/* Source Identification Banner */}
          {analysisResult.metadata.source_name && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.02)', padding: '0.5rem 1rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-subtle)' }}>
              {analysisResult.metadata.source_type === 'file' ? <Upload size={16} color="var(--accent-emerald)" /> : <Globe size={16} color="var(--accent-cyan)" />}
              <span>Source Analyzed: <strong style={{ color: 'var(--text-main)' }}>{analysisResult.metadata.source_name}</strong> ({analysisResult.metadata.source_type.toUpperCase()})</span>
            </div>
          )}

          {/* Metric Summary Cards */}
          <MetricsCards result={analysisResult} />

          {/* Two-Column Detail View */}
          <div className="results-columns">
            {/* Left Column: Frequency Ranking & Noun Phrases */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <FrequencyTable topWords={analysisResult.top_words} />
              <NounPhrasesPills phrases={analysisResult.noun_phrases} />
            </div>

            {/* Right Column: Sentiment, Length Distribution, Bigrams */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <SentimentCard sentiment={analysisResult.sentiment} />
              <LengthDistribution distribution={analysisResult.word_length_distribution} />
              <BigramPills bigrams={analysisResult.bigrams} />
            </div>
          </div>
        </div>
      )}

      {/* System Diagnostics */}
      <SystemDiagnostics healthState={healthState} activePhase="Phase 4: Ingestion & NLP" />

      {/* Footer */}
      <footer className="footer">
        <p>Word Intelligence v0.4 — Big Data & NLP Analytics Engine.</p>
      </footer>
    </div>
  );
}
