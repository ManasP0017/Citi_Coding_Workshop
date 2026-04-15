import { Box, Typography, Chip } from '@mui/material';

/**
 * Reusable page header.
 * Props:
 *   title      — string
 *   subtitle   — string (optional)
 *   count      — number (shows a chip badge)
 *   action     — ReactNode (button/s in the top-right)
 */
export default function PageHeader({ title, subtitle, count, action }) {
  return (
    <Box
      sx={{
        display: 'flex', alignItems: 'flex-start',
        justifyContent: 'space-between', mb: 3, flexWrap: 'wrap', gap: 2,
      }}
    >
      <Box>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Typography variant="h5">{title}</Typography>
          {count !== undefined && (
            <Chip
              label={count}
              size="small"
              color="primary"
              sx={{ fontWeight: 700, height: 22, fontSize: '0.72rem' }}
            />
          )}
        </Box>
        {subtitle && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            {subtitle}
          </Typography>
        )}
      </Box>
      {action && <Box sx={{ flexShrink: 0 }}>{action}</Box>}
    </Box>
  );
}
