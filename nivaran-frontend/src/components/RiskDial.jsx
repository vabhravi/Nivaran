/**
 * NIVARAN — RiskDial Component
 * Animated 0-10 risk score dial with Red/Amber/Green color coding.
 */

import React, { useState, useEffect } from 'react';

function RiskDial({ score, level }) {
  const [animatedScore, setAnimatedScore] = useState(0);

  // Animate the score from 0 to the actual value
  useEffect(() => {
    if (score === null || score === undefined) return;

    let start = 0;
    const end = score;
    const duration = 1500; // ms
    const startTime = Date.now();

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      const current = start + (end - start) * eased;

      setAnimatedScore(parseFloat(current.toFixed(1)));

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [score]);

  const getColorClass = () => {
    if (!level) {
      if (score <= 4) return 'red';
      if (score <= 7) return 'amber';
      return 'green';
    }
    return level.toLowerCase();
  };

  const getLevelText = () => {
    const cls = getColorClass();
    if (cls === 'red') return 'HIGH RISK';
    if (cls === 'amber') return 'MODERATE RISK';
    return 'LOW RISK';
  };

  const colorClass = getColorClass();
  const dialPercent = `${(animatedScore / 10) * 100}%`;

  return (
    <div className={`risk-dial ${colorClass}`} id="risk-dial">
      <div
        className="risk-dial-circle"
        style={{ '--dial-percent': dialPercent }}
      >
        <span className="risk-dial-score">{animatedScore}</span>
      </div>
      <span className="risk-dial-label">{getLevelText()}</span>
      <span style={{
        fontSize: '0.8rem',
        color: 'var(--text-tertiary)',
        marginTop: '-4px'
      }}>
        out of 10
      </span>
    </div>
  );
}

export default RiskDial;
