/**
 * NIVARAN — ProgressStream Component (v2)
 * Stage-based visual flow with icons, check marks, and pulsing indicators.
 */

import React, { useEffect, useRef } from 'react';

const STAGE_CONFIG = {
  ocr:       { icon: '📄', label: 'Scanning Document', color: 'var(--primary-400)' },
  ocr_done:  { icon: '✅', label: 'Text Extracted', color: 'var(--success-400)' },
  ner:       { icon: '🔍', label: 'Identifying Clauses', color: 'var(--primary-400)' },
  ner_done:  { icon: '✅', label: 'Entities Found', color: 'var(--success-400)' },
  rules:     { icon: '⚖️', label: 'Checking Legal Rules', color: 'var(--accent-400)' },
  rule_check:{ icon: '📋', label: 'Evaluating Clause', color: 'var(--accent-400)' },
  complete:  { icon: '🎯', label: 'Analysis Complete', color: 'var(--success-400)' },
  error:     { icon: '❌', label: 'Error', color: 'var(--danger-400)' },
};

function ProgressStream({ messages, percent }) {
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (!messages || messages.length === 0) return null;

  // Determine current stage from the latest message content
  const getStageFromMessage = (msg) => {
    if (msg.includes('Scanning')) return 'ocr';
    if (msg.includes('extracted successfully')) return 'ocr_done';
    if (msg.includes('Identifying')) return 'ner';
    if (msg.includes('Found:') || msg.includes('Extracting clause')) return 'ner_done';
    if (msg.includes('Checking against')) return 'rules';
    if (msg.includes('🔴') || msg.includes('🟠') || msg.includes('🟡') || msg.includes('🟢') || msg.includes('⚪')) return 'rule_check';
    if (msg.includes('No major violations')) return 'rule_check';
    if (msg.includes('complete')) return 'complete';
    if (msg.includes('fail') || msg.includes('error')) return 'error';
    return 'ocr';
  };

  return (
    <div className="progress-stream-v2" id="progress-stream">
      {/* Progress Bar */}
      <div className="progress-bar-v2-container">
        <div
          className="progress-bar-v2-fill"
          style={{ width: `${percent || 0}%` }}
          role="progressbar"
          aria-valuenow={percent || 0}
          aria-valuemin="0"
          aria-valuemax="100"
        />
        <span className="progress-bar-v2-percent">{percent || 0}%</span>
      </div>

      {/* Stage-based messages */}
      <div className="progress-messages-v2">
        {messages.map((msg, index) => {
          const stage = getStageFromMessage(msg);
          const config = STAGE_CONFIG[stage] || STAGE_CONFIG.ocr;
          const isLatest = index === messages.length - 1;

          return (
            <div
              key={index}
              className={`progress-message-v2 ${isLatest ? 'current' : 'completed'}`}
            >
              <span className={`progress-message-v2-icon ${isLatest ? 'pulsing' : ''}`}>
                {isLatest ? config.icon : '✓'}
              </span>
              <span className="progress-message-v2-text">{msg}</span>
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ProgressStream;
