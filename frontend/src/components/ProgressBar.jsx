import React from 'react';

/**
 * Animated progress bar with shimmer effect.
 */
export function ProgressBar({ progress = 0, label = '', currentFile = '', speed = 0, eta = 0, filesDone = 0, filesTotal = 0 }) {
  const formatSpeed = (bytesPerSec) => {
    if (bytesPerSec === 0) return '—';
    if (bytesPerSec > 1024 * 1024) return `${(bytesPerSec / (1024 * 1024)).toFixed(1)} MB/s`;
    if (bytesPerSec > 1024) return `${(bytesPerSec / 1024).toFixed(0)} KB/s`;
    return `${bytesPerSec.toFixed(0)} B/s`;
  };

  const formatEta = (seconds) => {
    if (seconds <= 0) return '—';
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  return (
    <div className="progress-container" id="progress-bar">
      <div className="progress-header">
        <span className="progress-label">{label || 'Progress'}</span>
        <span className="progress-percentage">{Math.round(progress)}%</span>
      </div>

      <div className="progress-track">
        <div
          className="progress-fill"
          style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
        />
      </div>

      <div className="progress-details">
        <span>{filesDone} / {filesTotal} files</span>
        <span>{formatSpeed(speed)}</span>
        <span>ETA: {formatEta(eta)}</span>
      </div>

      {currentFile && (
        <div className="current-file">
          <span>📄</span>
          <span className="current-file__name">{currentFile}</span>
        </div>
      )}
    </div>
  );
}
