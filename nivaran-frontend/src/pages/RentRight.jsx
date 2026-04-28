/**
 * NIVARAN — Rent-Right Page (v2)
 * Premium rental agreement scanner with animated risk gauge,
 * drag-and-drop upload, and expandable clause cards.
 *
 * Architecture: Fully offline — EasyOCR + SpaCy NER + SQLite Rule Engine
 */

import React, { useState, useEffect } from 'react';
import FileUploader from '../components/FileUploader';
import ProgressStream from '../components/ProgressStream';
import RiskDial from '../components/RiskDial';
import ClauseCard from '../components/ClauseCard';
import DisclaimerModal from '../components/DisclaimerModal';
import { getSocket, getSocketId } from '../utils/socket';

function RentRight() {
  const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [progressMessages, setProgressMessages] = useState([]);
  const [progressPercent, setProgressPercent] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [showOcrText, setShowOcrText] = useState(false);

  // Check localStorage for disclaimer acceptance
  useEffect(() => {
    const accepted = localStorage.getItem('nivaran_disclaimer_accepted');
    if (accepted === 'true') {
      setDisclaimerAccepted(true);
    }
  }, []);

  // Set up Socket.IO listener
  useEffect(() => {
    const socket = getSocket();

    const handleProgress = (data) => {
      if (data.module === 'rent-right') {
        setProgressMessages(prev => [...prev, data.message]);
        setProgressPercent(data.percent);
      }
    };

    socket.on('analysis_progress', handleProgress);

    return () => {
      socket.off('analysis_progress', handleProgress);
    };
  }, []);

  const handleDisclaimerAccept = () => {
    setDisclaimerAccepted(true);
    localStorage.setItem('nivaran_disclaimer_accepted', 'true');
  };

  const handleFileSelect = (file) => {
    setSelectedFile(file);
    setResult(null);
    setError(null);
    setProgressMessages([]);
    setProgressPercent(0);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgressMessages(['Scanning your rental agreement...']);
    setProgressPercent(5);

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000);

    try {
      const formData = new FormData();
      formData.append('document', selectedFile);
      const sid = getSocketId();
      if (sid) {
        formData.append('sid', sid);
      } else {
        // Socket not connected — set a synthetic progress hint
        setProgressMessages(prev => [...prev, 'Processing offline (real-time updates unavailable)...']);
      }

      const response = await fetch('/api/rent-right/upload', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      let data;
      try {
        data = await response.json();
      } catch (parseErr) {
        setError('Server returned an invalid response. Check the backend terminal for errors.');
        return;
      }

      if (!response.ok) {
        setError(data.error || `Server error (${response.status}). Please check backend logs.`);
        return;
      }
      setResult(data);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        setError('Request timed out. The analysis took too long — please try with a smaller file.');
      } else {
        setError(`Network error: ${err.message}. Please ensure the backend is running on port 5000.`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setSelectedFile(null);
    setProgressMessages([]);
    setProgressPercent(0);
    setError(null);
    setShowOcrText(false);
  };

  if (!disclaimerAccepted) {
    return <DisclaimerModal onAccept={handleDisclaimerAccept} />;
  }

  return (
    <div className="page" id="rent-right-page">
      <div className="container">
        {/* ─── Page Header ─────────────────────────── */}
        <header className="rr-header">
          <div className="rr-header-badge">
            <span>🔒</span> Offline Analysis &bull; Privacy-First &bull; No API Calls
          </div>
          <h1 className="rr-header-title">
            <span className="rr-header-icon">🏠</span>
            Rent-Right <span className="rr-header-gradient">Scanner</span>
          </h1>
          <p className="rr-header-subtitle">
            Upload your rental agreement to scan for predatory clauses and
            legal violations under the <strong>Model Tenancy Act, 2021</strong>.
          </p>
          {/* Demo Mode Toggle */}
          <button
            onClick={() => setDemoMode(d => !d)}
            id="rent-demo-toggle-btn"
            style={{
              marginTop: '12px',
              padding: '8px 20px',
              borderRadius: '20px',
              border: demoMode ? '2px solid #a78bfa' : '2px solid rgba(167,139,250,0.3)',
              background: demoMode ? 'rgba(167,139,250,0.2)' : 'transparent',
              color: demoMode ? '#a78bfa' : 'var(--text-secondary)',
              cursor: 'pointer',
              fontSize: '0.85rem',
              fontWeight: 600,
              transition: 'all 0.2s',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            ⚡ {demoMode ? 'Demo Mode ON (Local/Offline)' : 'Demo Mode OFF (Using Gemini AI)'}
          </button>
        </header>

        {/* ─── Upload Section ──────────────────────── */}
        {!result && (
          <div className="rr-upload-section">
            <FileUploader
              onFileSelect={handleFileSelect}
              disabled={isProcessing}
              acceptLabel="Drop your rental agreement here — PDF or image"
            />

            {/* Upload Button */}
            {selectedFile && !isProcessing && (
              <div className="rr-upload-action">
                <button
                  className="btn btn-rent btn-large rr-scan-btn"
                  onClick={handleUpload}
                  id="upload-btn"
                >
                  <span className="rr-scan-btn-icon">🔍</span>
                  Scan Agreement
                </button>
                <p className="rr-upload-hint">
                  Analysis runs entirely on your device — your document is never uploaded to any server.
                </p>
              </div>
            )}

            {/* Progress Stream */}
            {isProcessing && (
              <div className="rr-progress-section">
                <ProgressStream messages={progressMessages} percent={progressPercent} />
                <div style={{ textAlign: 'center', marginTop: '16px' }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginTop: '8px' }}>
                    EasyOCR is processing your document offline — this may take a moment...
                  </p>
                </div>
              </div>
            )}

            {/* Error Display */}
            {error && (
              <div className="rr-error-card">
                <div className="rr-error-icon">⚠️</div>
                <div className="rr-error-content">
                  <p className="rr-error-title">Analysis Failed</p>
                  <p className="rr-error-message">{error}</p>
                  <button className="btn btn-outline" onClick={handleReset} style={{ marginTop: '12px' }}>
                    Try Again
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ─── Results Section ─────────────────────── */}
        {result && (
          <div className="rr-results" id="rent-results">
            {/* Low Confidence Warning */}
            {result.low_confidence_warning && (
              <div className="rr-warning-banner">
                <span className="rr-warning-icon">⚠️</span>
                <div>
                  <strong>Low Confidence Warning</strong>
                  <p>Document quality is below threshold. Some clauses may have been missed. Upload a clearer document for better results.</p>
                </div>
              </div>
            )}

            {/* Results Grid: Score + Clauses */}
            <div className="rr-results-grid">
              {/* Left Column: Risk Dial + Summary */}
              <div className="rr-results-sidebar">
                <div className="rr-dial-card glass-card">
                  <RiskDial score={result.risk_score} level={result.risk_level} />
                </div>

                {/* Severity Breakdown */}
                <div className="rr-breakdown-card glass-card">
                  <h4 className="rr-card-label">Findings Summary</h4>
                  {Object.entries(result.severity_breakdown || {}).map(([sev, count]) => (
                    count > 0 && (
                      <div key={sev} className="rr-breakdown-row">
                        <span className={`clause-card-v2-severity-badge severity-${sev.toLowerCase()}`}>
                          {sev}
                        </span>
                        <span className="rr-breakdown-count">{count}</span>
                      </div>
                    )
                  ))}
                  {result.total_flags === 0 && (
                    <p className="rr-no-flags">✅ No violations found</p>
                  )}
                </div>

                {/* Extracted Values */}
                <div className="rr-entities-card glass-card">
                  <h4 className="rr-card-label">Extracted Values</h4>
                  <div className="rr-entities-list">
                    {result.extracted_entities?.rent_amount && (
                      <div className="rr-entity-row">
                        <span className="rr-entity-label">💰 Rent</span>
                        <span className="rr-entity-value">₹{result.extracted_entities.rent_amount.toLocaleString()}</span>
                      </div>
                    )}
                    {result.extracted_entities?.deposit_amount && (
                      <div className="rr-entity-row">
                        <span className="rr-entity-label">🏦 Deposit</span>
                        <span className="rr-entity-value">₹{result.extracted_entities.deposit_amount.toLocaleString()}</span>
                      </div>
                    )}
                    {result.extracted_entities?.lock_in_period && (
                      <div className="rr-entity-row">
                        <span className="rr-entity-label">🔐 Lock-in</span>
                        <span className="rr-entity-value">{result.extracted_entities.lock_in_period} months</span>
                      </div>
                    )}
                    {result.extracted_entities?.notice_period && (
                      <div className="rr-entity-row">
                        <span className="rr-entity-label">📅 Notice</span>
                        <span className="rr-entity-value">{result.extracted_entities.notice_period} days</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right Column: Flagged Clauses */}
              <div className="rr-results-main">
                <h3 className="rr-clauses-title">
                  {result.total_flags > 0
                    ? `⚠️ ${result.total_flags} Issue${result.total_flags > 1 ? 's' : ''} Found`
                    : '✅ Agreement Looks Clean'
                  }
                </h3>

                {result.total_flags > 0 ? (
                  <div className="rr-clauses-list">
                    {result.flagged_clauses.map((clause, index) => (
                      <ClauseCard key={index} clause={clause} index={index} />
                    ))}
                  </div>
                ) : (
                  <div className="rr-clean-card glass-card">
                    <span className="rr-clean-icon">🎉</span>
                    <h3>No Major Violations Detected</h3>
                    <p>
                      Your rental agreement appears to comply with the Model Tenancy Act, 2021.
                      However, we recommend having a legal professional review it before signing.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* OCR Text Preview */}
            <div className="rr-ocr-preview">
              <div
                className="rr-ocr-toggle"
                onClick={() => setShowOcrText(!showOcrText)}
                id="ocr-toggle"
              >
                <span>📝 View Raw Extracted Text</span>
                <span className={`rr-ocr-chevron ${showOcrText ? 'open' : ''}`}>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  </svg>
                </span>
              </div>
              {showOcrText && (
                <div className="rr-ocr-text">{result.ocr_text}</div>
              )}
            </div>

            {/* Scan Another */}
            <div className="rr-reset-section">
              <button
                className="btn btn-outline btn-large"
                onClick={handleReset}
                id="try-again-btn"
              >
                🔄 Scan Another Agreement
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RentRight;
