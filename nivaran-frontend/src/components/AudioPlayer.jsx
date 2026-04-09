/**
 * NIVARAN — AudioPlayer Component
 * Simple, accessible audio playback component for civic notice summaries.
 * Designed for elderly users: large controls, clear visual feedback.
 */

import React, { useRef, useState } from 'react';

function AudioPlayer({ audioUrl, summaryText }) {
  const audioRef = useRef(null);
  const [isPlaying, setIsPlaying] = useState(false);

  const togglePlay = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleEnded = () => setIsPlaying(false);

  if (!audioUrl) return null;

  return (
    <div className="audio-player" id="audio-player">
      <span className="audio-player-icon">
        {isPlaying ? '🔊' : '🔈'}
      </span>
      <h3 className="audio-player-title">
        Aapki Suchna Ka Saransh (Your Notice Summary)
      </h3>

      {/* Large play button for elderly users */}
      <button
        className="btn btn-civic btn-large"
        onClick={togglePlay}
        style={{ marginBottom: '20px', fontSize: '1.2rem', minWidth: '200px' }}
        id="audio-play-btn"
      >
        {isPlaying ? '⏸ Ruko (Pause)' : '▶ Suniye (Listen)'}
      </button>

      {/* Native audio controls as fallback */}
      <div style={{ position: 'relative', zIndex: 1 }}>
        <audio
          ref={audioRef}
          src={audioUrl}
          controls
          onEnded={handleEnded}
          onPlay={() => setIsPlaying(true)}
          onPause={() => setIsPlaying(false)}
          style={{ width: '100%', maxWidth: '500px' }}
          id="audio-element"
        >
          Your browser does not support audio playback.
        </audio>
      </div>

      {/* Text summary (secondary) */}
      {summaryText && (
        <div style={{
          marginTop: '20px',
          padding: '16px',
          background: 'rgba(255,255,255,0.03)',
          borderRadius: '12px',
          position: 'relative',
          zIndex: 1,
          textAlign: 'left',
        }}>
          <p style={{
            fontSize: '0.8rem',
            color: 'var(--text-tertiary)',
            textTransform: 'uppercase',
            letterSpacing: '1px',
            marginBottom: '8px',
            fontWeight: 600
          }}>
            Text Summary
          </p>
          <p style={{
            fontSize: '1rem',
            color: 'var(--text-secondary)',
            lineHeight: 1.7
          }}>
            {summaryText}
          </p>
        </div>
      )}
    </div>
  );
}

export default AudioPlayer;
