/**
 * useSSE — React hook for the /api/events Server-Sent Events stream.
 *
 * Why SSE over WebSocket for this dashboard:
 *  • Simpler protocol — server-push only, no bidirectional handshake needed
 *  • Works through HTTP/2 multiplexing and most corporate proxies
 *  • Native browser auto-reconnect via EventSource
 *  • No extra library required
 *
 * Usage:
 *   import useSSE from '../hooks/useSSE';
 *
 *   function MyComponent() {
 *     useSSE((msg) => {
 *       console.log(msg.event, msg.resource, msg.data);
 *     });
 *   }
 *
 * @param {(msg: {event: string, resource: string, data: any, ts: string}) => void} onMessage
 *   Called for every event pushed by the server (including heartbeats are filtered out).
 *
 * Raw EventSource pattern (no hook needed):
 *   const token = localStorage.getItem('token');
 *   const es = new EventSource(`${API_BASE}/api/events?token=${token}`);
 *
 *   // Listen to specific named events
 *   es.addEventListener('team.created',        e => refreshTeams());
 *   es.addEventListener('member.created',      e => refreshMembers());
 *   es.addEventListener('achievement.created', e => refreshAchievements());
 *   es.addEventListener('connected', e => console.log('Stream ready', JSON.parse(e.data)));
 *
 *   // Cleanup
 *   es.close();
 */

import { useEffect, useRef, useCallback } from 'react';

const API_BASE  = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:3001';
const SSE_URL   = `${API_BASE}/api/events`;
const MIN_DELAY = 1_000;   // ms
const MAX_DELAY = 30_000;  // ms

export default function useSSE(onMessage) {
  const esRef    = useRef(null);
  const timerRef = useRef(null);
  const delay    = useRef(MIN_DELAY);
  const cbRef    = useRef(onMessage);

  // Keep callback ref current without re-running the effect
  useEffect(() => { cbRef.current = onMessage; }, [onMessage]);

  const connect = useCallback(() => {
    const token = localStorage.getItem('token');
    if (!token) return;

    const url = `${SSE_URL}?token=${encodeURIComponent(token)}`;
    const es  = new EventSource(url);
    esRef.current = es;

    es.onopen = () => {
      delay.current = MIN_DELAY;   // reset back-off on successful connect
    };

    // Generic message handler (catches events without a specific 'event' field)
    es.onmessage = (e) => {
      try { cbRef.current(JSON.parse(e.data)); } catch { /* ignore non-JSON */ }
    };

    // Named-event listeners — map each backend event type
    const EVENTS = [
      'connected',
      'team.created',   'team.updated',   'team.deleted',
      'member.created', 'member.updated', 'member.deleted',
      'achievement.created', 'achievement.updated', 'achievement.deleted',
    ];
    EVENTS.forEach((evtName) => {
      es.addEventListener(evtName, (e) => {
        try { cbRef.current(JSON.parse(e.data)); } catch { /* ignore */ }
      });
    });

    es.onerror = () => {
      es.close();
      esRef.current = null;
      // Exponential back-off reconnect
      timerRef.current = setTimeout(() => {
        delay.current = Math.min(delay.current * 2, MAX_DELAY);
        connect();
      }, delay.current);
    };
  }, []);   // no deps — stable across renders

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(timerRef.current);
      esRef.current?.close();
    };
  }, [connect]);
}
