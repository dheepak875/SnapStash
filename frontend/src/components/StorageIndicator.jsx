import React, { useMemo } from 'react';

/**
 * Donut chart showing storage capacity.
 * Color transitions green → yellow → red based on usage.
 */
export function StorageIndicator({ stats }) {
  if (!stats) {
    return (
      <div className="glass-card storage-indicator" id="storage-indicator">
        <div className="storage-donut">
          <svg width="100" height="100" viewBox="0 0 100 100">
            <circle className="storage-donut__track" cx="50" cy="50" r="42" />
          </svg>
          <div className="storage-donut__label">
            <div className="storage-donut__percent" style={{ color: 'var(--color-text-muted)' }}>—</div>
          </div>
        </div>
        <div className="storage-info">
          <div className="storage-info__title">Storage</div>
          <div className="storage-info__detail">Loading…</div>
        </div>
      </div>
    );
  }

  const { total_bytes, used_bytes, free_bytes, photo_count, percentage_used } = stats;

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
  };

  // Donut chart calculations
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (percentage_used / 100) * circumference;

  // Color based on usage
  const strokeColor = useMemo(() => {
    if (percentage_used < 60) return 'var(--color-success)';
    if (percentage_used < 85) return 'var(--color-warning)';
    return 'var(--color-danger)';
  }, [percentage_used]);

  return (
    <div className="glass-card storage-indicator" id="storage-indicator">
      <div className="storage-donut">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle className="storage-donut__track" cx="50" cy="50" r={radius} />
          <circle
            className="storage-donut__fill"
            cx="50"
            cy="50"
            r={radius}
            stroke={strokeColor}
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
          />
        </svg>
        <div className="storage-donut__label">
          <div className="storage-donut__percent">{Math.round(percentage_used)}%</div>
          <div className="storage-donut__unit">used</div>
        </div>
      </div>
      <div className="storage-info">
        <div className="storage-info__title">Storage</div>
        <div className="storage-info__detail">
          <strong>{formatBytes(used_bytes)}</strong> / {formatBytes(total_bytes)}
        </div>
        <div className="storage-info__detail">
          {formatBytes(free_bytes)} free
        </div>
        <div className="storage-info__detail">
          <strong>{photo_count}</strong> photos backed up
        </div>
      </div>
    </div>
  );
}
