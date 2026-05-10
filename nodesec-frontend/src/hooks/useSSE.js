import { useRef, useEffect, useCallback, useState } from 'react';
import { useAuthStore } from '../store/authStore';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function useSSE(scanId, enabled = true) {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const [done, setDone] = useState(false);
  const abortRef = useRef(null);

  const connect = useCallback(() => {
    if (!scanId || !enabled) return;

    const token = useAuthStore.getState().token;
    const controller = new AbortController();
    abortRef.current = controller;

    setEvents([]);
    setDone(false);

    fetch(`${API_URL}/api/v1/scan/${scanId}/stream`, {
      headers: { Authorization: `Bearer ${token}` },
      signal: controller.signal,
    })
      .then(async (response) => {
        setConnected(true);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const event = JSON.parse(line.slice(6));
                setEvents((prev) => [...prev, event]);
                if (event.event === 'complete' || event.event === 'error') {
                  setDone(true);
                  return;
                }
              } catch {
                // skip malformed events
              }
            }
          }
        }
      })
      .catch((err) => {
        if (err.name !== 'AbortError') {
          console.error('SSE error:', err);
        }
      })
      .finally(() => {
        setConnected(false);
      });
  }, [scanId, enabled]);

  useEffect(() => {
    connect();
    return () => {
      abortRef.current?.abort();
    };
  }, [connect]);

  return { events, connected, done };
}