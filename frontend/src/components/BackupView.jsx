import React, { useState, useCallback } from 'react';
import { PhotoPicker } from './PhotoPicker';
import { ProgressBar } from './ProgressBar';
import { StorageIndicator } from './StorageIndicator';
import { useWakeLock } from '../hooks/useWakeLock';
import { useBackup } from '../hooks/useBackup';
import { useStorage } from '../hooks/useStorage';

/**
 * Main backup view — photo picker, "Night Shift" sync mode, progress, and storage.
 */
export function BackupView({ onBack }) {
  const [files, setFiles] = useState([]);
  const wakeLock = useWakeLock();
  const backup = useBackup();
  const storage = useStorage();

  const handleFilesSelected = useCallback((selectedFiles) => {
    setFiles(selectedFiles);
  }, []);

  const handleStartBackup = useCallback(async () => {
    if (files.length === 0) return;

    // Activate wake lock
    await wakeLock.request();

    // Start faster storage polling
    storage.startFastPoll();

    // Start the backup pipeline
    await backup.startBackup(files);

    // Release wake lock when done
    await wakeLock.release();
    storage.stopFastPoll();
    storage.refresh();
  }, [files, wakeLock, backup, storage]);

  const handleCancel = useCallback(() => {
    backup.cancelBackup();
    wakeLock.release();
    storage.stopFastPoll();
  }, [backup, wakeLock, storage]);

  const handleNewBackup = useCallback(() => {
    backup.reset();
    setFiles([]);
  }, [backup]);

  const isActive = ['hashing', 'diffing', 'uploading'].includes(backup.status);

  // "Night Shift" overlay during active backup
  if (isActive) {
    return (
      <div className="night-shift" id="night-shift-mode">
        <div className="night-shift__icon">🌙</div>
        <div className="night-shift__title">Night Shift Sync</div>
        <p className="night-shift__hint">
          Keep this screen on and plug in your phone. We'll handle the rest.
        </p>

        <div className="night-shift__progress">
          <ProgressBar
            progress={backup.progress}
            label={
              backup.status === 'hashing'
                ? 'Scanning files…'
                : backup.status === 'diffing'
                ? 'Checking for duplicates…'
                : 'Uploading…'
            }
            currentFile={backup.currentFile}
            speed={backup.speed}
            eta={backup.eta}
            filesDone={backup.filesDone}
            filesTotal={backup.filesTotal}
          />
        </div>

        {backup.skipped > 0 && (
          <div className="file-count-badge">
            ⏭️ <span>{backup.skipped}</span> already backed up
          </div>
        )}

        {wakeLock.isLocked && (
          <div className="status-badge status-badge--connected" style={{ marginTop: '0.5rem' }}>
            <span className="status-dot status-dot--green" />
            Screen Lock Active
          </div>
        )}

        <button className="btn btn-secondary" onClick={handleCancel} id="btn-cancel">
          ✕ Cancel
        </button>
      </div>
    );
  }

  return (
    <div className="backup-view stagger" id="backup-view">
      {/* Back button */}
      <button
        className="btn btn-secondary btn-icon"
        onClick={onBack}
        id="btn-back"
        style={{ alignSelf: 'flex-start' }}
      >
        ←
      </button>

      {/* Storage */}
      <StorageIndicator stats={storage.stats} />

      {/* Completion state */}
      {backup.status === 'complete' && (
        <div className="glass-card anim-scale-in" style={{ padding: 'var(--space-6)', textAlign: 'center' }}>
          <div style={{ fontSize: '3rem', marginBottom: 'var(--space-3)' }}>✅</div>
          <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 'var(--space-2)' }}>
            Backup Complete!
          </h2>
          <p className="text-muted" style={{ fontSize: 'var(--font-size-sm)' }}>
            {backup.filesDone} files backed up
            {backup.skipped > 0 && `, ${backup.skipped} skipped (already existed)`}
          </p>
          <button
            className="btn btn-primary mt-4"
            onClick={handleNewBackup}
            id="btn-new-backup"
          >
            📸 Back Up More
          </button>
        </div>
      )}

      {/* Error state */}
      {backup.status === 'error' && (
        <div className="glass-card" style={{ padding: 'var(--space-6)', textAlign: 'center', borderColor: 'rgba(248,113,113,0.3)' }}>
          <div style={{ fontSize: '3rem', marginBottom: 'var(--space-3)' }}>❌</div>
          <h2 style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, marginBottom: 'var(--space-2)', color: 'var(--color-danger)' }}>
            Backup Failed
          </h2>
          <p className="text-muted" style={{ fontSize: 'var(--font-size-sm)' }}>
            {backup.errorMessage}
          </p>
          <button
            className="btn btn-primary mt-4"
            onClick={handleNewBackup}
            id="btn-retry"
          >
            🔄 Try Again
          </button>
        </div>
      )}

      {/* File picker — only show in idle state */}
      {backup.status === 'idle' && (
        <>
          <PhotoPicker
            onFilesSelected={handleFilesSelected}
            disabled={isActive}
          />

          {files.length > 0 && (
            <button
              className="btn btn-primary btn-large anim-scale-in"
              onClick={handleStartBackup}
              style={{ width: '100%' }}
              id="btn-start-backup"
            >
              🚀 Start Backup ({files.length} files)
            </button>
          )}

          {!wakeLock.isSupported && (
            <p className="text-center text-muted" style={{ fontSize: 'var(--font-size-xs)' }}>
              ⚠️ Wake Lock not supported — keep your screen on manually during backup
            </p>
          )}
        </>
      )}
    </div>
  );
}
