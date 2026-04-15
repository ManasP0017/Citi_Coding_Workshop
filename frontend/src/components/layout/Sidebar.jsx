import { Box, Drawer, List, ListItem, ListItemButton, ListItemIcon, ListItemText, Typography, Divider, Avatar, Chip, Tooltip, useMediaQuery } from '@mui/material';
import { useTheme, alpha } from '@mui/material/styles';
import { NavLink, useLocation } from 'react-router-dom';
import DashboardRoundedIcon from '@mui/icons-material/DashboardRounded';
import GroupsRoundedIcon from '@mui/icons-material/GroupsRounded';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
import EmojiEventsRoundedIcon from '@mui/icons-material/EmojiEventsRounded';
import { useAuth } from '../../contexts/AuthContext';

export const DRAWER_WIDTH = 260;

const NAV_ITEMS = [
  { label: 'Insights',      icon: DashboardRoundedIcon,    path: '/app/insights'      },
  { label: 'Teams',         icon: GroupsRoundedIcon,        path: '/app/teams'         },
  { label: 'Members',       icon: PersonRoundedIcon,        path: '/app/members'       },
  { label: 'Achievements',  icon: EmojiEventsRoundedIcon,   path: '/app/achievements'  },
];

const ROLE_COLORS = {
  admin:       { bg: '#EEF2FF', color: '#3B5BDB' },
  manager:     { bg: '#F0FDF4', color: '#15803D' },
  contributor: { bg: '#FFF7ED', color: '#C2410C' },
  viewer:      { bg: '#F1F5F9', color: '#475569' },
};

function SidebarContent({ onClose }) {
  const { user } = useAuth();
  const location = useLocation();
  const roleStyle = ROLE_COLORS[user?.role] ?? ROLE_COLORS.viewer;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%', backgroundColor: '#FFFFFF' }}>
      {/* Logo */}
      <Box sx={{ px: 3, py: 2.5, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 36, height: 36, borderRadius: '10px',
            background: 'linear-gradient(135deg, #3B5BDB 0%, #748FFC 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
          }}
        >
          <GroupsRoundedIcon sx={{ color: '#fff', fontSize: 20 }} />
        </Box>
        <Typography variant="h6" sx={{ fontWeight: 800, letterSpacing: '-0.02em', color: '#1C2536' }}>
          TeamHub
        </Typography>
      </Box>

      <Divider />

      {/* Nav items */}
      <Box sx={{ flex: 1, overflowY: 'auto', py: 1 }}>
        <List disablePadding>
          {NAV_ITEMS.map(({ label, icon: Icon, path }) => {
            const active = location.pathname === path || location.pathname.startsWith(path + '/');
            return (
              <ListItem key={path} disablePadding>
                <ListItemButton
                  component={NavLink}
                  to={path}
                  onClick={onClose}
                  selected={active}
                  sx={{ gap: 0.5 }}
                >
                  <ListItemIcon>
                    <Icon fontSize="small" />
                  </ListItemIcon>
                  <ListItemText
                    primary={label}
                    primaryTypographyProps={{ fontWeight: active ? 600 : 500, fontSize: '0.9rem' }}
                  />
                  {active && (
                    <Box
                      sx={{
                        width: 4, height: 4, borderRadius: '50%',
                        backgroundColor: 'primary.main', ml: 'auto',
                      }}
                    />
                  )}
                </ListItemButton>
              </ListItem>
            );
          })}
        </List>
      </Box>

      <Divider />

      {/* User info */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Avatar sx={{ width: 36, height: 36, fontSize: '0.85rem', bgcolor: 'primary.main' }}>
          {user?.name?.charAt(0)?.toUpperCase() ?? 'U'}
        </Avatar>
        <Box sx={{ flex: 1, minWidth: 0 }}>
          <Typography variant="body2" fontWeight={600} noWrap>{user?.name}</Typography>
          <Chip
            label={user?.role}
            size="small"
            sx={{
              height: 18, fontSize: '0.68rem', fontWeight: 700,
              backgroundColor: roleStyle.bg, color: roleStyle.color,
              mt: 0.25,
            }}
          />
        </Box>
      </Box>
    </Box>
  );
}

export default function Sidebar({ open, onClose }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  if (isMobile) {
    return (
      <Drawer
        variant="temporary"
        open={open}
        onClose={onClose}
        ModalProps={{ keepMounted: true }}
        sx={{ '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}
      >
        <SidebarContent onClose={onClose} />
      </Drawer>
    );
  }

  return (
    <Drawer
      variant="permanent"
      open
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': { width: DRAWER_WIDTH, position: 'relative', height: '100%' },
      }}
    >
      <SidebarContent onClose={() => {}} />
    </Drawer>
  );
}
