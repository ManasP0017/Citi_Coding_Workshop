import { createTheme, alpha } from '@mui/material/styles';

const P = '#3B5BDB';   // brand primary — indigo-blue
const S = '#0CA678';   // brand secondary — teal

export const theme = createTheme({
  palette: {
    primary:    { main: P, light: '#748FFC', dark: '#2F4AC0', contrastText: '#fff' },
    secondary:  { main: S, light: '#38D9A9', dark: '#099268' },
    background: { default: '#F0F4FF', paper: '#FFFFFF' },
    text:       { primary: '#1C2536', secondary: '#637381' },
    error:      { main: '#FF5630' },
    warning:    { main: '#FFAB00' },
    success:    { main: '#36B37E' },
    info:       { main: '#00B8D9' },
    divider: 'rgba(145,158,171,0.18)',
  },

  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica Neue", sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.02em' },
    h5: { fontWeight: 700, letterSpacing: '-0.01em' },
    h6: { fontWeight: 600 },
    subtitle1: { fontWeight: 600 },
    subtitle2: { fontWeight: 600, color: '#637381' },
    button: { fontWeight: 600, textTransform: 'none', letterSpacing: 0 },
    caption: { color: '#637381' },
  },

  shape: { borderRadius: 12 },

  shadows: [
    'none',
    '0 1px 3px rgba(0,0,0,0.06)',
    '0 2px 8px rgba(0,0,0,0.08)',
    '0 4px 16px rgba(0,0,0,0.08)',
    '0 8px 24px rgba(0,0,0,0.08)',
    '0 12px 32px rgba(0,0,0,0.1)',
    ...Array(19).fill('0 12px 32px rgba(0,0,0,0.1)'),
  ],

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*, *::before, *::after': { boxSizing: 'border-box' },
        body: {
          margin: 0,
          fontFamily: '"Inter", sans-serif',
          scrollbarWidth: 'thin',
          scrollbarColor: '#c1c8d4 transparent',
        },
      },
    },

    MuiButton: {
      defaultProps: { disableElevation: true },
      styleOverrides: {
        root: { borderRadius: 8, padding: '8px 20px' },
        contained: {
          '&:hover': { boxShadow: `0 8px 16px ${alpha(P, 0.28)}` },
        },
        containedError: {
          '&:hover': { boxShadow: `0 8px 16px ${alpha('#FF5630', 0.28)}` },
        },
        outlined: { borderColor: alpha(P, 0.4) },
        sizeSmall: { padding: '5px 14px', fontSize: '0.8rem' },
      },
    },

    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
        rounded: { borderRadius: 12 },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
          transition: 'box-shadow 0.2s ease, transform 0.2s ease',
          '&:hover': {
            boxShadow: '0 6px 24px rgba(59,91,219,0.12)',
            transform: 'translateY(-1px)',
          },
        },
      },
    },

    MuiCardContent: {
      styleOverrides: { root: { '&:last-child': { paddingBottom: 16 } } },
    },

    MuiTextField: {
      defaultProps: { size: 'small' },
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': { borderRadius: 8 },
        },
      },
    },

    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: alpha(P, 0.6),
          },
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: { fontWeight: 600, borderRadius: 6 },
      },
    },

    MuiTableHead: {
      styleOverrides: {
        root: {
          '& .MuiTableCell-head': {
            fontWeight: 600,
            fontSize: '0.72rem',
            textTransform: 'uppercase',
            letterSpacing: '0.06em',
            color: '#637381',
            backgroundColor: '#F9FAFB',
            borderBottom: '1px solid rgba(145,158,171,0.2)',
          },
        },
      },
    },

    MuiTableRow: {
      styleOverrides: {
        root: {
          '&:last-child td': { borderBottom: 0 },
          '&:hover td': { backgroundColor: alpha(P, 0.03) },
          transition: 'background 0.15s',
        },
      },
    },

    MuiTableCell: {
      styleOverrides: {
        root: { borderColor: 'rgba(145,158,171,0.14)', padding: '12px 16px' },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: '1px solid rgba(145,158,171,0.16)',
          boxShadow: 'none',
        },
      },
    },

    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          margin: '2px 8px',
          width: 'calc(100% - 16px)',
          padding: '9px 12px',
          '&.Mui-selected': {
            backgroundColor: alpha(P, 0.1),
            color: P,
            '& .MuiListItemIcon-root': { color: P },
            '&:hover': { backgroundColor: alpha(P, 0.14) },
          },
          '&:hover': { backgroundColor: alpha(P, 0.06) },
        },
      },
    },

    MuiListItemIcon: {
      styleOverrides: { root: { minWidth: 36, color: '#637381' } },
    },

    MuiDialog: {
      styleOverrides: {
        paper: { borderRadius: 16, padding: '4px' },
      },
    },

    MuiAlert: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: { borderRadius: 6, fontWeight: 500, fontSize: '0.78rem' },
      },
    },

    MuiSkeleton: {
      defaultProps: { animation: 'wave' },
      styleOverrides: { root: { borderRadius: 6 } },
    },

    MuiLinearProgress: {
      styleOverrides: {
        root: { borderRadius: 4, height: 6 },
      },
    },

    MuiDivider: {
      styleOverrides: { root: { borderColor: 'rgba(145,158,171,0.18)' } },
    },

    MuiAvatar: {
      styleOverrides: {
        root: {
          fontWeight: 700,
          backgroundColor: P,
        },
      },
    },

    MuiBadge: {
      styleOverrides: { badge: { fontWeight: 700 } },
    },

    MuiIconButton: {
      styleOverrides: {
        root: { borderRadius: 8 },
      },
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#FFFFFF',
          color: '#1C2536',
          boxShadow: '0 1px 0 rgba(145,158,171,0.16)',
        },
      },
    },
  },
});
