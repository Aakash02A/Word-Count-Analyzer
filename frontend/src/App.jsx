import React, { useState, useEffect } from 'react';
import { checkHealth, analyzeText } from './services/api';
import Header from './components/Header';
import AnalysisWorkspace from './components/AnalysisWorkspace';
import MetricsCards from './components/MetricsCards';
import FrequencyTable from './components/FrequencyTable';
import LengthDistribution from './components/LengthDistribution';
import BigramPills from './components/BigramPills';
import SystemDiagnostics from './components/SystemDiagnostics';
import { Sparkles } from 'lucide-react';

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

  const [inputText, setInputText] = useState(SAMPLE_TEXT);
  const [topN, setTopN] = useState(10);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [engine, setEngine] = useState('python');
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
    if (!inputText.trim()) {
      setAnalysisError('Please enter or paste text to analyze.');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

    const result = await analyzeText({
      text: inputText,
      top_n: topN,
      case_sensitive: caseSensitive,
      engine,
    });

    if (result.success) {
      setAnalysisResult(result.data);
    } else {
      setAnalysisError(result.error);
    }
    setIsAnalyzing(false);
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
          Modular analytics architecture. Extract word metrics, frequency distributions, and bigram patterns across large text corpora with Python & Apache PySpark.
        </p>
      </section>

      {/* Modular Text Analysis Workspace */}
      <AnalysisWorkspace
        inputText={inputText}
        setInputText={setInputText}
        caseSensitive={caseSensitive}
        setCaseSensitive={setCaseSensitive}
        topN={topN}
        setTopN={setTopN}
        engine={engine}
        setEngine={setEngine}
        isAnalyzing={isAnalyzing}
        onAnalyze={handleAnalyze}
        onLoadSample={() => setInputText(SAMPLE_TEXT)}
        onClear={() => { setInputText(''); setAnalysisResult(null); }}
        error={analysisError}
      />

      {/* Analysis Results */}
      {analysisResult && (
        <div className="results-container">
          {/* Summary Metric Cards */}
          <MetricsCards result={analysisResult} />

          {/* Two-Column Detail View */}
          <div className="results-columns">
            <FrequencyTable topWords={analysisResult.top_words} />
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
              <LengthDistribution distribution={analysisResult.word_length_distribution} />
              <BigramPills bigrams={analysisResult.bigrams} />
            </div>
          </div>
        </div>
      )}

      {/* System Diagnostics */}
      <SystemDiagnostics healthState={healthState} activePhase="Phase 3: PySpark Integration" />

      {/* Footer */}
      <footer className="footer">
        <p>Word Intelligence v0.4 — Big Data & NLP Analytics Engine.</p>
      </footer>
    </div>
  );
}
