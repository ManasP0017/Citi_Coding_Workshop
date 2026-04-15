import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import TeamsTab from '../components/TeamsTab';
import MembersTab from '../components/MembersTab';
import AchievementsTab from '../components/AchievementsTab';
import InsightsTab from '../components/InsightsTab';
import LiveNotifications from '../components/LiveNotifications';

export default function Dashboard() {
  const [tabValue, setTabValue] = useState(0);
  const [insightsKey, setInsightsKey] = useState(0);
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleWsEvent = useCallback((msg) => {
    if (['member.created', 'member.updated', 'member.deleted',
         'team.created', 'team.updated', 'team.deleted'].includes(msg.event)) {
      setInsightsKey(k => k + 1);
    }
  }, []);

  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            Team Management — {user?.name} ({user?.role})
          </Typography>
          <Button color="inherit" onClick={handleLogout}>
            Logout
          </Button>
        </Toolbar>
      </AppBar>
      <Container maxWidth="xl" sx={{ mt: 4 }}>
        <Paper elevation={3} sx={{ mb: 3 }}>
          <Tabs
            value={tabValue}
            onChange={(e, newValue) => setTabValue(newValue)}
            centered
          >
            <Tab label="Teams" />
            <Tab label="Members" />
            <Tab label="Achievements" />
            <Tab label="Insights" />
          </Tabs>
        </Paper>
        <Box sx={{ mt: 3 }}>
          {tabValue === 0 && <TeamsTab />}
          {tabValue === 1 && <MembersTab />}
          {tabValue === 2 && <AchievementsTab />}
          {tabValue === 3 && <InsightsTab key={insightsKey} />}
        </Box>
      </Container>
      <LiveNotifications onEvent={handleWsEvent} />
    </>
  );
}
