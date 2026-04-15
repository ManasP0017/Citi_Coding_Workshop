import { useState, useCallback } from 'react';
import { Box } from '@mui/material';
import { Outlet } from 'react-router-dom';
import Sidebar, { DRAWER_WIDTH } from './Sidebar';
import TopBar from './TopBar';
import LiveNotifications from '../LiveNotifications';

export default function AppLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifCount, setNotifCount] = useState(0);

  const handleEvent = useCallback(() => {
    setNotifCount(n => n + 1);
  }, []);

  return (
    <Box sx={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main column */}
      <Box
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden',
          minWidth: 0,
        }}
      >
        <TopBar
          onMenuClick={() => setSidebarOpen(o => !o)}
          notifCount={notifCount}
        />

        {/* Page content */}
        <Box
          component="main"
          className="animate-fade-in"
          sx={{
            flex: 1,
            overflowY: 'auto',
            backgroundColor: 'background.default',
            p: { xs: 2, sm: 3 },
          }}
        >
          <Outlet />
        </Box>
      </Box>

      {/* Global live notifications */}
      <LiveNotifications
        onEvent={handleEvent}
      />
    </Box>
  );
}
