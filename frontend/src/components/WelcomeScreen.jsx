import React, { useEffect, useState } from 'react';
import { getQRCodeUrl, getApplianceStatus } from '../api/client';

/**
 * Welcome screen — shown on first visit or from a connected display.
 * Displays a QR code linking to the PWA install URL.
 */
export function WelcomeScreen({ onContinue }) {
  const [qrUrl, setQrUrl] = useState(null);
  const [appStatus, setAppStatus] = useState(null);
  const [installPrompt, setInstallPrompt] = useState(null);

  // Fetch QR code
  useEffect(() => {
    getQRCodeUrl()
      .then(setQrUrl)
      .catch(() => setQrUrl(null));
  }, []);

  // Fetch appliance status
  useEffect(() => {
    getApplianceStatus()
      .then(setAppStatus)
      .catch(() => {});
  }, []);

  // Listen for PWA install prompt
  useEffect(() => {
    const handler = (e) => {
      e.preventDefault();
      setInstallPrompt(e);
    };
    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = async () => {
    if (installPrompt) {
      await installPrompt.prompt();
      setInstallPrompt(null);
    }
  };

  return (
    <div className="welcome-screen stagger" id="welcome-screen">
      {/* Connection Status */}
      <div>
        {appStatus?.storage_connected ? (
          <div className="status-badge status-badge--connected">
            <span className="status-dot status-dot--green" />
            Storage Connected
          </div>
        ) : (
          <div className="status-badge status-badge--disconnected">
            <span className="status-dot status-dot--red" />
            No Storage Detected
          </div>
        )}
      </div>

      {/* QR Code */}
      {qrUrl && (
        <div className="glass-card qr-wrapper">
          <img src={qrUrl} alt="Scan to open SnapStash" />
        </div>
      )}

      {/* Instructions */}
      <div className="welcome-instructions">
        <p>
          <strong>Scan the QR code</strong> with your phone camera to open
          SnapStash and start backing up your photos.
        </p>
        <p className="mt-2" style={{ color: 'var(--color-text-muted)' }}>
          Your photos are stored locally on the connected hard drive —
          no cloud, no subscriptions, fully private.
        </p>
      </div>

      {/* Photo count if available */}
      {appStatus && appStatus.photo_count > 0 && (
        <div className="file-count-badge">
          📸 <span>{appStatus.photo_count}</span> photos already backed up
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col gap-2" style={{ width: '100%', maxWidth: '300px' }}>
        <button className="btn btn-primary btn-large" onClick={onContinue} id="btn-continue">
          📱 Start Backup
        </button>

        {installPrompt && (
          <button className="btn btn-secondary" onClick={handleInstall} id="btn-install">
            ⬇️ Install App
          </button>
        )}
      </div>
    </div>
  );
}
