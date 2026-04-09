/**
 * NIVARAN — Home Page
 * Landing page with module selector cards for Civic-Ease and Rent-Right.
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const navigate = useNavigate();

  return (
    <div className="page" id="home-page">
      <div className="container">
        {/* Hero Section */}
        <section className="home-hero">
          <div className="home-hero-badge">
            🤖 AI-Powered &bull; Rule-Based &bull; Privacy-First
          </div>
          <h1>
            Your <span>AI Companion</span> for
            <br />Civic & Legal Inclusion
          </h1>
          <p className="home-hero-subtitle">
            NIVARAN bridges the gap between complex bureaucratic documents and the common citizen.
            Upload a government notice or rental agreement — get instant, explainable analysis.
          </p>
        </section>

        {/* Module Cards */}
        <section className="home-modules" id="module-selector">
          {/* Civic-Ease Card */}
          <div
            className="module-card civic"
            onClick={() => navigate('/civic-ease')}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && navigate('/civic-ease')}
            id="module-civic-ease"
          >
            <span className="module-card-emoji">🏛️</span>
            <h3>Civic-Ease</h3>
            <p className="module-card-desc">
              For elderly users and those unfamiliar with official language.
              Upload a government notice and hear a simple Hindi audio explanation.
            </p>
            <ul className="module-card-features">
              <li>Hindi audio summaries using Text-to-Speech</li>
              <li>Extracts due dates, amounts, and required actions</li>
              <li>High contrast, large-button UI for accessibility</li>
              <li>Supports electricity bills, tax notices, bank letters</li>
            </ul>
            <button className="btn btn-civic btn-large" id="btn-goto-civic">
              Open Civic-Ease →
            </button>
          </div>

          {/* Rent-Right Card */}
          <div
            className="module-card rent"
            onClick={() => navigate('/rent-right')}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && navigate('/rent-right')}
            id="module-rent-right"
          >
            <span className="module-card-emoji">🏠</span>
            <h3>Rent-Right</h3>
            <p className="module-card-desc">
              For students and tenants. Upload your rental agreement and instantly
              scan for predatory clauses and legal violations.
            </p>
            <ul className="module-card-features">
              <li>Risk Score (0-10) with Red/Amber/Green rating</li>
              <li>Flags violations of Model Tenancy Act, 2021</li>
              <li>Legal citations for every flagged clause</li>
              <li>Detects no-refund, excess deposit, and penalty traps</li>
            </ul>
            <button className="btn btn-rent btn-large" id="btn-goto-rent">
              Open Rent-Right →
            </button>
          </div>
        </section>

        {/* How it Works */}
        <section style={{ textAlign: 'center', padding: 'var(--space-2xl) 0' }}>
          <h2 style={{ marginBottom: 'var(--space-xl)' }}>How NIVARAN Works</h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: 'var(--space-lg)',
          }}>
            {[
              { icon: '📄', title: 'Upload', desc: 'Drop your document — PDF or image' },
              { icon: '🔍', title: 'Extract', desc: 'Gemini Flash OCR reads the text' },
              { icon: '🧠', title: 'Analyze', desc: 'SpaCy NER + Rule Engine audits it' },
              { icon: '✅', title: 'Result', desc: 'Get actionable, explainable output' },
            ].map((step, i) => (
              <div key={i} className="glass-card" style={{ textAlign: 'center', padding: '24px' }}>
                <span style={{ fontSize: '2.5rem', display: 'block', marginBottom: '12px' }}>{step.icon}</span>
                <h4 style={{ marginBottom: '8px' }}>{step.title}</h4>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{step.desc}</p>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

export default Home;
