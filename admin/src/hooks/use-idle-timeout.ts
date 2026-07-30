'use client';

import { useEffect, useRef } from 'react';
import { useAuth } from '../providers/AuthProvider';

interface IdleTimeoutOptions {
  timeoutMs?: number; // Inactivity timeout in ms (default: 30 minutes)
  onIdle?: () => void;
}

export function useIdleTimeout({ timeoutMs = 30 * 60 * 1000, onIdle }: IdleTimeoutOptions = {}) {
  const { isAuthenticated, logout } = useAuth();
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const resetTimer = () => {
    if (timerRef.current) clearTimeout(timerRef.current);

    if (isAuthenticated) {
      timerRef.current = setTimeout(() => {
        if (onIdle) {
          onIdle();
        } else {
          logout();
        }
      }, timeoutMs);
    }
  };

  useEffect(() => {
    if (!isAuthenticated) return;

    const events = ['mousemove', 'keydown', 'click', 'scroll', 'touchstart'];
    const handleUserActivity = () => resetTimer();

    events.forEach((event) => window.addEventListener(event, handleUserActivity));
    resetTimer();

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      events.forEach((event) => window.removeEventListener(event, handleUserActivity));
    };
  }, [isAuthenticated, timeoutMs]);
}
