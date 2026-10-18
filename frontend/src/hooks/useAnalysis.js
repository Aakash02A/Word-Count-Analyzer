import { useState, useCallback } from 'react';
import { analyzeText, analyzeFile, analyzeImage, analyzeUrl, exportAnalysisCsv } from '../services/api';

const SAMPLE_TEXT = `Apache PySpark provides a robust, high-performance distributed DataFrame framework for big data processing. Word Intelligence integrates PySpark analytics with Natural Language Processing heuristics to transform unstructured content into structured insights. Analyzing token frequencies, bigrams, and word-length distributions allows researchers to understand linguistic patterns rapidly.`;

/**
 * Shared hook for analysis logic.
 * Each analysis page uses this with its specific input mode.
 * @param {'text' | 'file' | 'image' | 'url'} defaultMode
 */
export default function useAnalysis(defaultMode = 'text') {
  const [inputText, setInputText] = useState(defaultMode === 'text' ? SAMPLE_TEXT : '');
  const [selectedFile, setSelectedFile] = useState(null);
  const [inputUrl, setInputUrl] = useState('');
  const [topN, setTopN] = useState(10);
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [engine, setEngine] = useState('python');

  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const [freqViewMode, setFreqViewMode] = useState('table');
  const [lengthViewMode, setLengthViewMode] = useState('bars');
  const [isExporting, setIsExporting] = useState(false);

  const handleAnalyze = useCallback(async (mode) => {
    const activeMode = mode || defaultMode;
    setAnalysisError(null);
    setIsAnalyzing(true);

    let result;

    if (activeMode === 'text') {
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
    } else if (activeMode === 'file') {
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
    } else if (activeMode === 'image') {
      if (!selectedFile) {
        setAnalysisError('Please choose an image (.png, .jpg, .jpeg, or .webp) to upload.');
        setIsAnalyzing(false);
        return;
      }
      result = await analyzeImage({
        file: selectedFile,
        top_n: topN,
        case_sensitive: caseSensitive,
        engine,
      });
    } else if (activeMode === 'url') {
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
  }, [inputText, selectedFile, inputUrl, topN, caseSensitive, engine, defaultMode]);

  const handleClear = useCallback((mode) => {
    const activeMode = mode || defaultMode;
    if (activeMode === 'text') setInputText('');
    else if (activeMode === 'file' || activeMode === 'image') setSelectedFile(null);
    else if (activeMode === 'url') setInputUrl('');
    setAnalysisResult(null);
    setAnalysisError(null);
  }, [defaultMode]);

  const handleExportCsv = useCallback(async () => {
    if (!analysisResult) return;
    setIsExporting(true);
    await exportAnalysisCsv(analysisResult);
    setIsExporting(false);
  }, [analysisResult]);

  const loadSample = useCallback(() => {
    setInputText(SAMPLE_TEXT);
  }, []);

  return {
    // Input state
    inputText, setInputText,
    selectedFile, setSelectedFile,
    inputUrl, setInputUrl,
    topN, setTopN,
    caseSensitive, setCaseSensitive,
    engine, setEngine,

    // Execution state
    isAnalyzing,
    analysisResult,
    analysisError,

    // View mode state
    freqViewMode, setFreqViewMode,
    lengthViewMode, setLengthViewMode,
    isExporting,

    // Actions
    handleAnalyze,
    handleClear,
    handleExportCsv,
    loadSample,

    // Constants
    SAMPLE_TEXT,
  };
}
