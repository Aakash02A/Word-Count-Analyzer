import { useState, useEffect, useCallback } from 'react';
import { checkHealth } from '../services/api';

/**
 * Shared hook for backend health polling.
 * Used by AppLayout to provide health state across all pages.
 */
export default function useHealth() {
  const [healthState, setHealthState] = useState({
    status: 'checking',
    data: null,
    error: null,
    latencyMs: null,
    lastChecked: null,
  });
  const [isRefreshing, setIsRefreshing] = useState(false);

  const fetchHealth = useCallback(async () => {
    setIsRefreshing(true);
    const startTime = performance.now();
    const result = await checkHealth();
    const endTime = performance.now();
    const latency = Math.round(endTime - startTime);

    if (result.success) {
      setHealthState({
        status: 'connected',
        data: result.data,
        error: null,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    } else {
      setHealthState({
        status: 'disconnected',
        data: null,
        error: result.error,
        latencyMs: latency,
        lastChecked: new Date().toLocaleTimeString(),
      });
    }
    setIsRefreshing(false);
  }, []);

  useEffect(() => {
    fetchHealth();
  }, [fetchHealth]);

  return { healthState, isRefreshing, fetchHealth };
}
