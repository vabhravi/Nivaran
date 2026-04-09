/**
 * NIVARAN — ProgressStream Component
 * Displays real-time Socket.IO progress updates during document analysis.
 */

import React, { useEffect, useRef } from 'react';

function ProgressStream({ messages, percent }) {
  const messagesEndRef = useRef(null);

  // Auto-scroll to latest message
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  if (!messages || messages.length === 0) return null;

  return (
    <div className="progress-stream" id="progress-stream">
      {/* Progress Bar */}
      <div className="progress-bar-container">
        <div
          className="progress-bar-fill"
          style={{ width: `${percent || 0}%` }}
          role="progressbar"
          aria-valuenow={percent || 0}
          aria-valuemin="0"
          aria-valuemax="100"
        />
      </div>

      {/* Progress Messages */}
      <div className="progress-messages">
        {messages.map((msg, index) => (
          <div key={index} className="progress-message">
            <span className="progress-message-dot" />
            <span>{msg}</span>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
    </div>
  );
}

export default ProgressStream;
