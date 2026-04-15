import { useState, useCallback, useRef, useEffect } from 'react';

/**
 * Hook for the Screen Wake Lock API.
 * Keeps the screen on during photo backup.
 */
export function useWakeLock() {
  const [isLocked, setIsLocked] = useState(false);
  const wakeLockRef = useRef(null);
  const isSupported = 'wakeLock' in navigator;

  const request = useCallback(async () => {
    if (!isSupported) return false;

    try {
      wakeLockRef.current = await navigator.wakeLock.request('screen');
      setIsLocked(true);

      wakeLockRef.current.addEventListener('release', () => {
        setIsLocked(false);
        wakeLockRef.current = null;
      });

      return true;
    } catch (err) {
      console.warn('Wake Lock request failed:', err.message);
      setIsLocked(false);
      return false;
    }
  }, [isSupported]);

  const release = useCallback(async () => {
    if (wakeLockRef.current) {
      await wakeLockRef.current.release();
      wakeLockRef.current = null;
      setIsLocked(false);
    }
  }, []);

  // Re-acquire on visibility change (OS may release it when tab is hidden)
  useEffect(() => {
    const handleVisibility = async () => {
      if (
        document.visibilityState === 'visible' &&
        isLocked &&
        !wakeLockRef.current
      ) {
        await request();
      }
    };

    document.addEventListener('visibilitychange', handleVisibility);
    return () =>
      document.removeEventListener('visibilitychange', handleVisibility);
  }, [isLocked, request]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (wakeLockRef.current) {
        wakeLockRef.current.release();
      }
    };
  }, []);

  return { isLocked, isSupported, request, release };
}
