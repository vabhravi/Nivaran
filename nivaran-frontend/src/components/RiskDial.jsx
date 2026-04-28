/**
 * NIVARAN — RiskDial Component
 * SVG-based animated 0-10 risk score gauge with Red/Amber/Green arc.
 * Uses stroke-dashoffset animation for smooth, cross-browser rendering.
 */

import React, { useState, useEffect } from 'react';

function RiskDial({ score, level }) {
  const [animatedScore, setAnimatedScore] = useState(0);
  const [showLabel, setShowLabel] = useState(false);

  // SVG arc parameters
  const size = 200;
  const strokeWidth = 14;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2 - 4;
  const circumference = 2 * Math.PI * radius;

  // Animate the score from 0 to final value
  useEffect(() => {
    if (score === null || score === undefined) return;

    let start = 0;
    const end = score;
    const duration = 1800;
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
      } else {
        setShowLabel(true);
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

  const getLevelDescription = () => {
    const cls = getColorClass();
    if (cls === 'red') return 'Serious violations detected. Do not sign without legal review.';
    if (cls === 'amber') return 'Some concerns found. Review flagged clauses carefully.';
    return 'Agreement appears compliant with tenancy law.';
  };

  const colorClass = getColorClass();
  const strokeOffset = circumference - (animatedScore / 10) * circumference;

  // Get the stroke color based on risk level
  const getStrokeColor = () => {
    if (colorClass === 'red') return '#ef4444';
    if (colorClass === 'amber') return '#f59e0b';
    return '#22c55e';
  };

  const getGlowColor = () => {
    if (colorClass === 'red') return 'rgba(239, 68, 68, 0.3)';
    if (colorClass === 'amber') return 'rgba(245, 158, 11, 0.3)';
    return 'rgba(34, 197, 94, 0.3)';
  };

  return (
    <div className={`risk-dial-v2 ${colorClass}`} id="risk-dial">
      {/* SVG Gauge */}
      <div
        className="risk-dial-v2-svg-wrap"
        style={{ filter: `drop-shadow(0 0 20px ${getGlowColor()})` }}
      >
        <svg
          width={size}
          height={size}
          viewBox={`0 0 ${size} ${size}`}
          className="risk-dial-v2-svg"
        >
          {/* Background track */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="rgba(148, 163, 184, 0.1)"
            strokeWidth={strokeWidth}
          />
          {/* Animated arc */}
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={getStrokeColor()}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={strokeOffset}
            strokeLinecap="round"
            transform={`rotate(-90 ${center} ${center})`}
            className="risk-dial-v2-arc"
          />
          {/* Inner decorative circle */}
          <circle
            cx={center}
            cy={center}
            r={radius - strokeWidth - 4}
            fill="rgba(26, 26, 62, 0.5)"
            stroke="rgba(148, 163, 184, 0.06)"
            strokeWidth="1"
          />
        </svg>

        {/* Score overlay */}
        <div className="risk-dial-v2-center">
          <span className="risk-dial-v2-score">{animatedScore}</span>
          <span className="risk-dial-v2-max">/ 10</span>
        </div>
      </div>

      {/* Label */}
      <div className={`risk-dial-v2-label ${showLabel ? 'visible' : ''}`}>
        <span className="risk-dial-v2-level">{getLevelText()}</span>
        <span className="risk-dial-v2-desc">{getLevelDescription()}</span>
      </div>
    </div>
  );
}

export default RiskDial;
