import React, { useState, useRef, useEffect } from 'react';
import { Image as ImageIcon, Play, AlertTriangle, Eye, RefreshCw, CheckCircle2, Sparkles, X } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import AnalysisResults from '../components/AnalysisResults';
import useAnalysis from '../hooks/useAnalysis';

export default function ImagesPage() {
  const analysis = useAnalysis('image');
  const fileInputRef = useRef(null);
  const [imagePreviewUrl, setImagePreviewUrl] = useState(null);

  // Manage thumbnail object URL
  useEffect(() => {
    if (analysis.selectedFile) {
      const objectUrl = URL.createObjectURL(analysis.selectedFile);
      setImagePreviewUrl(objectUrl);
      return () => URL.revokeObjectURL(objectUrl);
    } else {
      setImagePreviewUrl(null);
    }
  }, [analysis.selectedFile]);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      const validTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
      if (!validTypes.includes(file.type) && !/\.(png|jpe?g|webp)$/i.test(file.name)) {
        analysis.setAnalysisError('Unsupported image format. Please select a PNG, JPG, JPEG, or WEBP image.');
        return;
      }
      if (file.size > 10 * 1024 * 1024) {
        analysis.setAnalysisError('Image upload exceeds maximum allowed size of 10 MB.');
        return;
      }
      analysis.setSelectedFile(file);
    }
  };

  const handleClearImage = () => {
    analysis.handleClear('image');
    if (fileInputRef.current) fileInputRef.current.value = '';
    setImagePreviewUrl(null);
  };

  return (
    <div className="page-content">
      <PageHeader
        icon={<ImageIcon size={22} color="var(--accent-amber)" />}
        title="Image Text Extraction (OCR)"
        description="Upload photographs, screenshots, or scanned documents containing printed text. The system performs Tesseract OCR extraction and NLP analytics."
      />

      <section className="analyzer-section">
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/png,image/jpeg,image/webp,.png,.jpg,.jpeg,.webp"
          style={{ display: 'none' }}
        />

        {/* Dropzone / Preview Area */}
        <div
          className="file-dropzone"
          style={{
            cursor: 'pointer',
            minHeight: imagePreviewUrl ? '220px' : '160px',
            position: 'relative',
          }}
          onClick={() => !analysis.selectedFile && fileInputRef.current?.click()}
        >
          {imagePreviewUrl ? (
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: '0.85rem',
                width: '100%',
              }}
            >
              <div
                style={{
                  position: 'relative',
                  maxHeight: '180px',
                  borderRadius: 'var(--radius-md)',
                  overflow: 'hidden',
                  border: '1px solid var(--border-subtle)',
                  boxShadow: '0 4px 16px rgba(0,0,0,0.4)',
                }}
              >
                <img
                  src={imagePreviewUrl}
                  alt="Upload preview"
                  style={{
                    maxHeight: '160px',
                    maxWidth: '100%',
                    objectFit: 'contain',
                    display: 'block',
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '0.9rem' }}>
                  {analysis.selectedFile.name}
                </span>
                <span
                  style={{
                    fontSize: '0.75rem',
                    padding: '0.15rem 0.5rem',
                    background: 'rgba(245, 158, 11, 0.15)',
                    color: 'var(--accent-amber)',
                    borderRadius: '999px',
                    fontWeight: 600,
                  }}
                >
                  {Math.round(analysis.selectedFile.size / 1024)} KB
                </span>
                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    fileInputRef.current?.click();
                  }}
                  className="btn-secondary"
                  style={{ padding: '0.25rem 0.6rem', fontSize: '0.75rem' }}
                >
                  Change Image
                </button>
              </div>
            </div>
          ) : (
            <>
              <div
                style={{
                  width: '54px',
                  height: '54px',
                  borderRadius: 'var(--radius-md)',
                  background: 'rgba(245, 158, 11, 0.12)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ImageIcon size={28} color="var(--accent-amber)" />
              </div>
              <span style={{ fontWeight: 600, color: 'var(--text-main)', fontSize: '1rem' }}>
                Click or Drag & Drop Image Here
              </span>
              <span style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                Supports PNG, JPG, JPEG, and WEBP images containing printed text (up to 10 MB)
              </span>
            </>
          )}
        </div>

        <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>
          Tesseract Optical Character Recognition processes high-contrast printed text best.
          Handwriting recognition and complex multi-column layouts are not guaranteed.
        </p>

        {/* Controls Row */}
        <div className="controls-row">
          <div className="options-group">
            <label className="option-item">
              <input
                type="checkbox"
                checked={analysis.caseSensitive}
                onChange={(e) => analysis.setCaseSensitive(e.target.checked)}
              />
              <span>Case Sensitive</span>
            </label>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <span>Top Words:</span>
              <select
                className="option-select"
                value={analysis.topN}
                onChange={(e) => analysis.setTopN(Number(e.target.value))}
              >
                <option value={5}>Top 5</option>
                <option value={10}>Top 10</option>
                <option value={20}>Top 20</option>
                <option value={50}>Top 50</option>
              </select>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>
              <span>Engine:</span>
              <select
                className="option-select"
                value={analysis.engine}
                onChange={(e) => analysis.setEngine(e.target.value)}
                style={{ fontWeight: 500 }}
              >
                <option value="python">Python In-Memory (Ultra Fast)</option>
                <option value="pyspark">Apache PySpark (DataFrame)</option>
              </select>
            </div>
          </div>

          <div className="buttons-group">
            <button onClick={handleClearImage} className="btn-secondary">
              <span>Clear</span>
            </button>
            <button
              onClick={() => analysis.handleAnalyze('image')}
              disabled={analysis.isAnalyzing || !analysis.selectedFile}
              className="btn-primary"
              style={{
                background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                color: '#ffffff',
                border: 'none',
              }}
            >
              <Play size={15} />
              <span>{analysis.isAnalyzing ? 'Extracting via OCR...' : 'Extract & Analyze Text'}</span>
            </button>
          </div>
        </div>

        {/* Error Notification */}
        {analysis.analysisError && (
          <div className="error-banner" style={{ marginTop: '1.25rem' }}>
            <AlertTriangle size={18} />
            <span>{analysis.analysisError}</span>
          </div>
        )}
      </section>

      {/* Analysis Results Display */}
      {analysis.analysisResult && (
        <AnalysisResults
          analysisResult={analysis.analysisResult}
          freqViewMode={analysis.freqViewMode}
          setFreqViewMode={analysis.setFreqViewMode}
          lengthViewMode={analysis.lengthViewMode}
          setLengthViewMode={analysis.setLengthViewMode}
          isExporting={analysis.isExporting}
          onExportCsv={analysis.handleExportCsv}
        />
      )}
    </div>
  );
}
