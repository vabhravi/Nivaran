/**
 * NIVARAN — ClauseCard Component
 * Expandable card showing flagged rental agreement violations.
 * Displays: severity badge, violation description, legal citation, recommended action.
 */

import React, { useState } from 'react';

function ClauseCard({ clause }) {
  const [expanded, setExpanded] = useState(false);

  const severityClass = `severity-${clause.severity.toLowerCase()}`;

  return (
    <div
      className={`clause-card ${expanded ? 'expanded' : ''}`}
      id={`clause-card-${clause.rule_id}`}
    >
      <div
        className="clause-card-header"
        onClick={() => setExpanded(!expanded)}
        role="button"
        tabIndex={0}
        aria-expanded={expanded}
        onKeyDown={(e) => e.key === 'Enter' && setExpanded(!expanded)}
      >
        <div className="clause-card-left">
          <span className={`clause-card-severity ${severityClass}`}>
            {clause.severity}
          </span>
          <span className="clause-card-title">{clause.rule_name}</span>
        </div>
        <span className="clause-card-chevron">▼</span>
      </div>

      <div className="clause-card-body">
        <div className="clause-card-content">
          {/* Violation Description */}
          <div className="clause-detail">
            <div className="clause-detail-label">Violation</div>
            <div className="clause-detail-text">{clause.violation_description}</div>
          </div>

          {/* Detected Value */}
          {clause.detected_value && (
            <div className="clause-detail">
              <div className="clause-detail-label">What We Found</div>
              <div className="clause-detail-text">{clause.detected_value}</div>
            </div>
          )}

          {/* Clause Text */}
          {clause.clause_text && (
            <div className="clause-detail">
              <div className="clause-detail-label">Clause Text</div>
              <div className="clause-detail-text" style={{ fontStyle: 'italic' }}>
                "{clause.clause_text}"
              </div>
            </div>
          )}

          {/* Legal Citation */}
          <div className="clause-detail" style={{ borderLeftColor: 'var(--accent-500)' }}>
            <div className="clause-detail-label">Legal Reference</div>
            <div className="clause-detail-text">{clause.legal_citation}</div>
          </div>

          {/* Recommended Action */}
          <div className="clause-detail" style={{ borderLeftColor: 'var(--success-500)' }}>
            <div className="clause-detail-label">Recommended Action</div>
            <div className="clause-detail-text">{clause.recommended_action}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ClauseCard;
