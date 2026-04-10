/**
 * NIVARAN — Civic-Ease Page
 * Elderly-friendly upload + audio UI for government notice simplification.
 * High contrast, large buttons, audio-first output.
 */

import React, { useState, useEffect } from 'react';
import FileUploader from '../components/FileUploader';
import ProgressStream from '../components/ProgressStream';
import AudioPlayer from '../components/AudioPlayer';
import DisclaimerModal from '../components/DisclaimerModal';
import { getSocket, getSocketId } from '../utils/socket';

function CivicEase() {
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
      if (data.module === 'civic-ease') {
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
        formData.append('mode', 'civic');
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

    // Standard mode: Gemini API
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 150000);

    try {
      const formData = new FormData();
      formData.append('document', selectedFile);
      const sid = getSocketId();
      if (sid) formData.append('sid', sid);

      const response = await fetch('/api/civic-ease/upload', {
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
          setError(data.error || 'An error occurred during processing.');
        }
        return;
      }
      setResult(data);
    } catch (err) {
      clearTimeout(timeoutId);
      if (err.name === 'AbortError') {
        setError('Request timed out. Try Demo Mode for instant offline analysis.');
      } else {
        setError(`Network error: ${err.message}`);
      }
    } finally {
      setIsProcessing(false);
    }
  };

  if (!disclaimerAccepted) {
    return <DisclaimerModal onAccept={handleDisclaimerAccept} />;
  }

  return (
    <div className="page civic-page" id="civic-ease-page">
      <div className="container" style={{ maxWidth: '800px' }}>
        {/* Page Header */}
        <header className="page-header">
          <span className="page-header-icon">🏛️</span>
          <h1>Civic-Ease</h1>
          <p>
            Apna sarkari notice upload karein — Hindi mein audio saransh sunein
            <br />
            <span style={{ fontSize: '0.9rem' }}>
              (Upload your government notice — hear a Hindi audio summary)
            </span>
          </p>
          {/* Demo Mode Toggle */}
          <button
            onClick={() => setDemoMode(d => !d)}
            id="demo-toggle-btn"
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
        <FileUploader
          onFileSelect={handleFileSelect}
          disabled={isProcessing}
          acceptLabel="Yahan apna dastavez dalein ya click karein (Drop your document here or click to browse)"
        />

        {/* Upload Button */}
        {selectedFile && !isProcessing && !result && (
          <div style={{ textAlign: 'center', marginTop: 'var(--space-xl)' }}>
            <button
              className="btn btn-civic btn-large"
              onClick={handleUpload}
              id="upload-btn"
              style={{ fontSize: '1.2rem', padding: '18px 48px' }}
            >
              {demoMode ? '⚡ Demo Scan (Instant)' : '📤 Jaanch Shuru Karein (Start Analysis)'}
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
              <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399' }}>✅ Ready to retry! Click the button below.</p>
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

        {/* Results */}
        {result && (
          <div className="results-section" id="civic-results">
            {/* Low Confidence Warning */}
            {result.low_confidence_warning && (
              <div className="low-confidence-warning">
                <span>⚠️</span>
                <span>
                  <strong>Low Confidence Warning:</strong> The document quality is low.
                  Results may be inaccurate. Please upload a clearer image.
                </span>
              </div>
            )}

            {/* Audio Player (Primary Output) */}
            <div style={{ marginTop: 'var(--space-xl)' }}>
              <AudioPlayer
                audioUrl={result.audio_url}
                summaryText={result.summary_text}
              />
            </div>

            {/* Extracted Entities */}
            {result.extracted_entities && (
              <div style={{ marginTop: 'var(--space-xl)' }}>
                <div className="glass-card">
                  <h3 style={{ marginBottom: 'var(--space-md)' }}>📋 Extracted Information</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--space-md)' }}>
                    {result.extracted_entities.amounts?.length > 0 && (
                      <div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '4px', fontWeight: 600 }}>Amount</p>
                        <div className="entity-tags">
                          {result.extracted_entities.amounts.map((a, i) => (
                            <span key={i} className="entity-tag">₹ {a}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {result.extracted_entities.dates?.length > 0 && (
                      <div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '4px', fontWeight: 600 }}>Dates</p>
                        <div className="entity-tags">
                          {result.extracted_entities.dates.map((d, i) => (
                            <span key={i} className="entity-tag">📅 {d}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {result.extracted_entities.organizations?.length > 0 && (
                      <div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '4px', fontWeight: 600 }}>Organization</p>
                        <div className="entity-tags">
                          {result.extracted_entities.organizations.map((o, i) => (
                            <span key={i} className="entity-tag">🏢 {o}</span>
                          ))}
                        </div>
                      </div>
                    )}
                    {result.extracted_entities.actions?.length > 0 && (
                      <div>
                        <p style={{ fontSize: '0.8rem', color: 'var(--text-tertiary)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '4px', fontWeight: 600 }}>Actions Required</p>
                        <div className="entity-tags">
                          {result.extracted_entities.actions.map((a, i) => (
                            <span key={i} className="entity-tag">⚡ {a}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* OCR Text Preview (Collapsible) */}
            <div className="ocr-preview" style={{ marginTop: 'var(--space-lg)' }}>
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
                🔄 Naya Dastavez Dalein (Upload New Document)
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default CivicEase;
