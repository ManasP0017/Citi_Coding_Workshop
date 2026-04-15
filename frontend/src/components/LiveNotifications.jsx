/**
 * LiveNotifications — real-time toast notifications via SSE.
 *
 * Connects to GET /api/events using the authenticated user's JWT.
 * Shows a bottom-right snackbar whenever the server pushes an event.
 * Calls `onEvent(msg)` so the parent (Dashboard) can react (e.g. refresh Insights).
 *
 * InsightsTab integration example (raw EventSource, no hook):
 *   useEffect(() => {
 *     const token = localStorage.getItem('token');
 *     const es = new EventSource(`http://localhost:8000/api/events?token=${token}`);
 *     es.addEventListener('member.created', () => fetchInsights());
 *     es.addEventListener('team.created',   () => fetchInsights());
 *     return () => es.close();
 *   }, []);
 */

import { useState, useCallback } from 'react';
import { Snackbar, Alert, Typography, Chip, Box } from '@mui/material';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import useSSE from '../hooks/useSSE';

const EVENT_LABELS = {
  'team.created':        { label: 'New team created',    icon: '🏢', sev: 'success' },
  'team.updated':        { label: 'Team updated',        icon: '✏️', sev: 'info'    },
  'team.deleted':        { label: 'Team deleted',        icon: '🗑️', sev: 'warning' },
  'member.created':      { label: 'New member added',    icon: '👤', sev: 'success' },
  'member.updated':      { label: 'Member updated',      icon: '✏️', sev: 'info'    },
  'member.deleted':      { label: 'Member removed',      icon: '🗑️', sev: 'warning' },
  'achievement.created': { label: 'Achievement awarded', icon: '🏆', sev: 'success' },
  'achievement.updated': { label: 'Achievement updated', icon: '✏️', sev: 'info'    },
  'achievement.deleted': { label: 'Achievement removed', icon: '🗑️', sev: 'warning' },
};

export default function LiveNotifications({ onEvent }) {
  const [notification, setNotification] = useState(null);
  const [connected,    setConnected]    = useState(false);

  const handleMessage = useCallback((msg) => {
    if (msg.event === 'connected') {
      setConnected(true);
      return;
    }
    const meta = EVENT_LABELS[msg.event];
    if (!meta) return;
    const name = msg.data?.name || msg.data?.title || '';
    setNotification({ ...meta, name });
    onEvent?.(msg);
  }, [onEvent]);

  useSSE(handleMessage);

  return (
    <>
      {/* SSE connection status pill — top-right corner */}
      <Box sx={{ position: 'fixed', top: 72, right: 16, zIndex: 1300 }}>
        <Chip
          size="small"
          icon={<FiberManualRecordIcon sx={{ fontSize: '10px !important',
                  color: connected ? '#4caf50' : '#f44336' }} />}
          label={connected ? 'Live' : 'Connecting…'}
          variant="outlined"
          sx={{ fontSize: '0.7rem', height: 22,
                borderColor: connected ? '#4caf50' : '#f44336',
                color:       connected ? '#4caf50' : '#f44336' }}
        />
      </Box>

      {/* Event toast */}
      <Snackbar
        open={!!notification}
        autoHideDuration={3500}
        onClose={() => setNotification(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert
          onClose={() => setNotification(null)}
          severity={notification?.sev || 'info'}
          variant="filled"
          sx={{ minWidth: 280 }}
        >
          <Typography variant="body2" fontWeight="bold">
            {notification?.icon} {notification?.label}
          </Typography>
          {notification?.name && (
            <Typography variant="caption" sx={{ opacity: 0.9 }}>
              {notification.name}
            </Typography>
          )}
        </Alert>
      </Snackbar>
    </>
  );
}
