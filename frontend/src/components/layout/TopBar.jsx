import { useState } from 'react';
import {
  AppBar, Toolbar, IconButton, Typography, Box,
  Menu, MenuItem, Avatar, Divider, Badge, Tooltip,
} from '@mui/material';
import MenuRoundedIcon from '@mui/icons-material/MenuRounded';
import NotificationsNoneRoundedIcon from '@mui/icons-material/NotificationsNoneRounded';
import LogoutRoundedIcon from '@mui/icons-material/LogoutRounded';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const PAGE_TITLES = {
  '/app/insights':     'Insights Dashboard',
  '/app/teams':        'Teams',
  '/app/members':      'Members',
  '/app/achievements': 'Achievements',
};

export default function TopBar({ onMenuClick, notifCount }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState(null);

  const pageTitle = PAGE_TITLES[location.pathname] ?? 'TeamHub';

  const handleLogout = () => {
    setAnchorEl(null);
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="sticky" elevation={0}>
      <Toolbar sx={{ gap: 1 }}>
        {/* Mobile hamburger */}
        <IconButton
          onClick={onMenuClick}
          sx={{ display: { md: 'none' } }}
          size="small"
        >
          <MenuRoundedIcon />
        </IconButton>

        {/* Page title */}
        <Typography variant="h6" sx={{ flex: 1, fontWeight: 700 }}>
          {pageTitle}
        </Typography>

        {/* Notification bell */}
        <Tooltip title="Recent events">
          <IconButton size="small">
            <Badge badgeContent={notifCount || 0} color="error" max={9}>
              <NotificationsNoneRoundedIcon fontSize="small" />
            </Badge>
          </IconButton>
        </Tooltip>

        {/* User avatar menu */}
        <Tooltip title="Account">
          <IconButton
            size="small"
            onClick={(e) => setAnchorEl(e.currentTarget)}
          >
            <Avatar
              sx={{ width: 32, height: 32, fontSize: '0.8rem', bgcolor: 'primary.main' }}
            >
              {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
            </Avatar>
          </IconButton>
        </Tooltip>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={() => setAnchorEl(null)}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          PaperProps={{ sx: { width: 200, mt: 0.5 } }}
        >
          <Box sx={{ px: 2, py: 1.5 }}>
            <Typography variant="subtitle2">{user?.name}</Typography>
            <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
          </Box>
          <Divider />
          <MenuItem onClick={() => setAnchorEl(null)}>
            <PersonRoundedIcon fontSize="small" sx={{ mr: 1.5, color: 'text.secondary' }} />
            <Typography variant="body2">Profile</Typography>
          </MenuItem>
          <MenuItem onClick={handleLogout} sx={{ color: 'error.main' }}>
            <LogoutRoundedIcon fontSize="small" sx={{ mr: 1.5 }} />
            <Typography variant="body2">Logout</Typography>
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
}
