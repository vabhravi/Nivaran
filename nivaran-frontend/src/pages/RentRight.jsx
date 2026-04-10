/**
 * NIVARAN — Rent-Right Page
 * Student/tenant rental agreement scanner with risk scoring UI.
 * Shows Risk Dial, flagged clause cards, and legal citations.
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
  const [retryCountdown, setRetryCountdown] = useState(0);
  const [demoMode, setDemoMode] = useState(false);

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
    setRetryCountdown(0);
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setError(null);
    setResult(null);
    setProgressMessages([]);
    setProgressPercent(0);

    // Demo mode: fast local route, no Gemini API
    if (demoMode) {
      try {
        setProgressMessages(['⚡ Demo Mode: Running local AI analysis...']);
        setProgressPercent(30);
        const formData = new FormData();
        formData.append('document', selectedFile);
        formData.append('mode', 'rent');
        const res = await fetch('/api/demo/scan', { method: 'POST', body: formData });
        const data = await res.json();
        setProgressPercent(100);
        if (!res.ok) { setError(data.error || 'Demo scan failed.'); return; }
        setResult(data);
      } catch (err) {
        setError(`Demo mode error: ${err.message}`);
      } finally {
        setIsProcessing(false);
      }
      return;
    }

    // Standard mode: Gemini API route
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 150000);

    try {
      const formData = new FormData();
      formData.append('document', selectedFile);
      const sid = getSocketId();
      if (sid) formData.append('sid', sid);

      const response = await fetch('/api/rent-right/upload', {
        method: 'POST',
        body: formData,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      const data = await response.json();

      if (!response.ok) {
        if (response.status === 429) {
          const waitSecs = data.retry_after || 60;
          setError(data.error || '⏳ Rate limit hit. Please wait and retry.');
          setRetryCountdown(waitSecs);
          const interval = setInterval(() => {
            setRetryCountdown(prev => {
              if (prev <= 1) { clearInterval(interval); return 0; }
              return prev - 1;
            });
          }, 1000);
        } else {
          setError(data.error || 'An error occurred during analysis.');
        }
        return;
      }
      setResult(data);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        setError('Request timed out. Try Demo Mode for instant offline analysis.');
      } else {
        setError(`Network error: ${err.message}. Please ensure the backend is running.`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  if (!disclaimerAccepted) {
    return <DisclaimerModal onAccept={handleDisclaimerAccept} />;
  }

  return (
    <div className="page" id="rent-right-page">
      <div className="container">
        {/* Page Header */}
        <header className="page-header">
          <span className="page-header-icon">🏠</span>
          <h1>Rent-Right</h1>
          <p>
            Upload your rental agreement to scan for predatory clauses and
            legal violations under the Model Tenancy Act, 2021.
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

        {/* File Upload */}
        <div style={{ maxWidth: '700px', margin: '0 auto' }}>
          <FileUploader
            onFileSelect={handleFileSelect}
            disabled={isProcessing}
            acceptLabel="Drop your rental agreement here — PDF or image"
          />

          {/* Upload Button */}
          {selectedFile && !isProcessing && !result && (
            <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
              <button
                className="btn btn-rent btn-large"
                onClick={handleUpload}
                id="upload-btn"
              >
                {demoMode ? '⚡ Demo Scan (Instant)' : '🔍 Scan Agreement'}
              </button>
              {demoMode && (
                <p style={{ marginTop: '8px', fontSize: '0.8rem', color: '#a78bfa' }}>
                  ⚡ Local AI — zero API calls, works offline
                </p>
              )}
            </div>
          )}

          {/* Progress Stream */}
          {isProcessing && (
            <div style={{ marginTop: 'var(--space-xl)' }}>
              <ProgressStream messages={progressMessages} percent={progressPercent} />
              <div style={{ textAlign: 'center', marginTop: 'var(--space-md)' }}>
                <div className="spinner" style={{ margin: '0 auto' }} />
              </div>
            </div>
          )}

          {/* Error / Rate Limit Display */}
          {error && (
            retryCountdown > 0 ? (
              <div style={{
                marginTop: 'var(--space-xl)',
                padding: 'var(--space-lg)',
                background: 'rgba(251, 191, 36, 0.1)',
                border: '1px solid rgba(251, 191, 36, 0.4)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'center',
              }}>
                <p style={{ fontSize: '1.4rem', marginBottom: '8px' }}>⏳</p>
                <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fbbf24' }}>AI quota limit hit — please wait</p>
                <p style={{ fontSize: '2.5rem', fontWeight: 800, color: '#fbbf24', margin: '12px 0' }}>
                  {retryCountdown}s
                </p>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                  The free tier resets every minute. You can retry when the timer reaches 0.
                </p>
              </div>
            ) : retryCountdown === 0 && error.startsWith('⏳') ? (
              <div style={{
                marginTop: 'var(--space-xl)',
                padding: 'var(--space-lg)',
                background: 'rgba(52, 211, 153, 0.1)',
                border: '1px solid rgba(52, 211, 153, 0.4)',
                borderRadius: 'var(--radius-md)',
                textAlign: 'center',
              }}>
                <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399' }}>✅ Ready to retry! Click "Scan Agreement" again.</p>
              </div>
            ) : (
              <div style={{
                marginTop: 'var(--space-xl)',
                padding: 'var(--space-lg)',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--danger-400)',
                textAlign: 'center',
              }}>
                <p style={{ fontSize: '1.1rem', fontWeight: 600 }}>❌ {error}</p>
              </div>
            )
          )}
        </div>

        {/* Results */}
        {result && (
          <div className="results-section" id="rent-results">
            {/* Low Confidence Warning */}
            {result.low_confidence_warning && (
              <div className="low-confidence-warning">
                <span>⚠️</span>
                <span>
                  <strong>Low Confidence Warning:</strong> The document quality is below threshold.
                  Some clauses may have been missed. Please upload a clearer document for accurate results.
                </span>
              </div>
            )}

            {/* Risk Score + Flagged Clauses Grid */}
            <div className="results-grid" style={{ marginTop: 'var(--space-xl)' }}>
              {/* Left: Risk Dial */}
              <div style={{ position: 'sticky', top: '100px' }}>
                <RiskDial score={result.risk_score} level={result.risk_level} />

                {/* Severity Breakdown */}
                <div className="glass-card" style={{ marginTop: 'var(--space-lg)', padding: 'var(--space-md)' }}>
                  <h4 style={{ fontSize: '0.85rem', marginBottom: 'var(--space-sm)', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Findings
                  </h4>
                  {Object.entries(result.severity_breakdown || {}).map(([sev, count]) => (
                    count > 0 && (
                      <div key={sev} style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        padding: '6px 0',
                        fontSize: '0.85rem',
                      }}>
                        <span className={`clause-card-severity severity-${sev.toLowerCase()}`} style={{ fontSize: '0.7rem' }}>
                          {sev}
                        </span>
                        <span style={{ color: 'var(--text-secondary)' }}>{count}</span>
                      </div>
                    )
                  ))}
                  {result.total_flags === 0 && (
                    <p style={{ fontSize: '0.85rem', color: 'var(--success-400)' }}>
                      ✅ No violations found
                    </p>
                  )}
                </div>

                {/* Extracted Values */}
                <div className="glass-card" style={{ marginTop: 'var(--space-md)', padding: 'var(--space-md)' }}>
                  <h4 style={{ fontSize: '0.85rem', marginBottom: 'var(--space-sm)', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                    Extracted Values
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '0.85rem' }}>
                    {result.extracted_entities?.rent_amount && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-tertiary)' }}>Rent</span>
                        <span>₹{result.extracted_entities.rent_amount.toLocaleString()}</span>
                      </div>
                    )}
                    {result.extracted_entities?.deposit_amount && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-tertiary)' }}>Deposit</span>
                        <span>₹{result.extracted_entities.deposit_amount.toLocaleString()}</span>
                      </div>
                    )}
                    {result.extracted_entities?.lock_in_period && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-tertiary)' }}>Lock-in</span>
                        <span>{result.extracted_entities.lock_in_period} months</span>
                      </div>
                    )}
                    {result.extracted_entities?.notice_period && (
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ color: 'var(--text-tertiary)' }}>Notice</span>
                        <span>{result.extracted_entities.notice_period} days</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Right: Flagged Clauses */}
              <div>
                <h3 style={{ marginBottom: 'var(--space-md)' }}>
                  {result.total_flags > 0
                    ? `⚠️ ${result.total_flags} Issue${result.total_flags > 1 ? 's' : ''} Found`
                    : '✅ Agreement Looks Clean'
                  }
                </h3>

                {result.total_flags > 0 ? (
                  <div className="flagged-clauses-list">
                    {result.flagged_clauses.map((clause, index) => (
                      <ClauseCard key={index} clause={clause} />
                    ))}
                  </div>
                ) : (
                  <div className="glass-card" style={{ textAlign: 'center', padding: 'var(--space-2xl)' }}>
                    <span style={{ fontSize: '3rem', display: 'block', marginBottom: 'var(--space-md)' }}>🎉</span>
                    <h3>No Major Violations Detected</h3>
                    <p style={{ color: 'var(--text-secondary)', marginTop: 'var(--space-sm)' }}>
                      Your rental agreement appears to comply with the Model Tenancy Act, 2021.
                      However, we recommend having a legal professional review it before signing.
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* OCR Text Preview (Collapsible) */}
            <div className="ocr-preview" style={{ marginTop: 'var(--space-2xl)' }}>
              <div
                className="ocr-preview-toggle"
                onClick={() => setShowOcrText(!showOcrText)}
                id="ocr-toggle"
              >
                <span>📝 View Raw Extracted Text</span>
                <span>{showOcrText ? '▲' : '▼'}</span>
              </div>
              {showOcrText && (
                <div className="ocr-preview-text">{result.ocr_text}</div>
              )}
            </div>

            {/* Try Again Button */}
            <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
              <button
                className="btn btn-outline btn-large"
                onClick={() => {
                  setResult(null);
                  setSelectedFile(null);
                  setProgressMessages([]);
                  setProgressPercent(0);
                }}
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
