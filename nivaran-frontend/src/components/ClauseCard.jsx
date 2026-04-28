/**
 * NIVARAN — ClauseCard Component (v2)
 * Enhanced expandable card with severity stripe, icons,
 * smooth height animation, and copy citation button.
 */

import React, { useState, useRef } from 'react';

const SEVERITY_CONFIG = {
  CRITICAL: { icon: '🔴', color: 'var(--danger-400)', bg: 'rgba(239, 68, 68, 0.08)', stripe: '#ef4444' },
  HIGH:     { icon: '🟠', color: 'var(--warning-400)', bg: 'rgba(249, 115, 22, 0.08)', stripe: '#f97316' },
  MEDIUM:   { icon: '🟡', color: 'var(--accent-400)', bg: 'rgba(251, 191, 36, 0.08)', stripe: '#fbbf24' },
  LOW:      { icon: '🟢', color: 'var(--success-400)', bg: 'rgba(34, 197, 94, 0.08)', stripe: '#22c55e' },
};

function ClauseCard({ clause, index }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const bodyRef = useRef(null);

  const config = SEVERITY_CONFIG[clause.severity] || SEVERITY_CONFIG.MEDIUM;
  const severityClass = `severity-${clause.severity.toLowerCase()}`;

  const handleCopyCitation = (e) => {
    e.stopPropagation();
    navigator.clipboard.writeText(clause.legal_citation).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div
      className={`clause-card-v2 ${expanded ? 'expanded' : ''}`}
      id={`clause-card-${clause.rule_id}`}
      style={{
        '--stripe-color': config.stripe,
        animationDelay: `${(index || 0) * 0.08}s`,
      }}
    >
      {/* Severity stripe */}
      <div className="clause-card-v2-stripe" />

      {/* Header */}
      <div
        className="clause-card-v2-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        aria-expanded={expanded}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div className="clause-card-v2-left">
          <span className="clause-card-v2-severity-icon">{config.icon}</span>
          <span className={`clause-card-v2-severity-badge ${severityClass}`}>
            {clause.severity}
          </span>
          <span className="clause-card-v2-title">{clause.rule_name}</span>
        </div>
        <span className="clause-card-v2-chevron">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path d="M4 6L8 10L12 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </span>
      </div>

      {/* Expandable Body */}
      <div
        className="clause-card-v2-body"
        ref={bodyRef}
        style={{
          maxHeight: expanded ? `${bodyRef.current?.scrollHeight || 600}px` : '0px',
        }}
      >
        <div className="clause-card-v2-content">
          {/* Violation */}
          <div className="clause-card-v2-section">
            <div className="clause-card-v2-section-label">
              <span>⚠️</span> What's Wrong
            </div>
            <p className="clause-card-v2-section-text">{clause.violation_description}</p>
          </div>

          {/* Detected Value */}
          {clause.detected_value && (
            <div className="clause-card-v2-section" style={{ background: config.bg }}>
              <div className="clause-card-v2-section-label">
                <span>🔍</span> What We Found
              </div>
              <p className="clause-card-v2-section-text">{clause.detected_value}</p>
            </div>
          )}

          {/* Clause Text */}
          {clause.clause_text && (
            <div className="clause-card-v2-section clause-card-v2-quote">
              <div className="clause-card-v2-section-label">
                <span>📝</span> From the Agreement
              </div>
              <blockquote className="clause-card-v2-blockquote">
                "{clause.clause_text}"
              </blockquote>
            </div>
          )}

          {/* Divider */}
          <div className="clause-card-v2-divider" />

          {/* Legal Citation */}
          <div className="clause-card-v2-section clause-card-v2-legal">
            <div className="clause-card-v2-section-label">
              <span>⚖️</span> Legal Reference
              <button
                className="clause-card-v2-copy-btn"
                onClick={handleCopyCitation}
                title="Copy citation"
              >
                {copied ? '✓ Copied' : '📋 Copy'}
              </button>
            </div>
            <p className="clause-card-v2-section-text">{clause.legal_citation}</p>
          </div>

          {/* Recommended Action */}
          <div className="clause-card-v2-section clause-card-v2-action">
            <div className="clause-card-v2-section-label">
              <span>💡</span> Recommended Action
            </div>
            <p className="clause-card-v2-section-text">{clause.recommended_action}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ClauseCard;
