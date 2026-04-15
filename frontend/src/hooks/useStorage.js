import { useState, useCallback, useRef, useEffect } from 'react';
import { getStorageStats } from '../api/client';

/**
 * Hook for polling storage stats from the server.
 */
export function useStorage(pollInterval = 30000) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const intervalRef = useRef(null);

  const refresh = useCallback(async () => {
    try {
      const data = await getStorageStats();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial fetch + polling
  useEffect(() => {
    refresh();
    intervalRef.current = setInterval(refresh, pollInterval);
    return () => clearInterval(intervalRef.current);
  }, [refresh, pollInterval]);

  // Allow manual start of faster polling during backup
  const startFastPoll = useCallback(() => {
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(refresh, 5000);
  }, [refresh]);

  const stopFastPoll = useCallback(() => {
    clearInterval(intervalRef.current);
    intervalRef.current = setInterval(refresh, pollInterval);
  }, [refresh, pollInterval]);

  return { stats, loading, error, refresh, startFastPoll, stopFastPoll };
}
