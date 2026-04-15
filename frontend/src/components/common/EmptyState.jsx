import { Box, Typography, Button } from '@mui/material';
import InboxRoundedIcon from '@mui/icons-material/InboxRounded';

export default function EmptyState({ icon: Icon, title, message, actionLabel, onAction }) {
  const Ico = Icon ?? InboxRoundedIcon;
  return (
    <Box
      sx={{
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', py: 10, gap: 2,
      }}
    >
      <Box
        sx={{
          width: 80, height: 80, borderRadius: '50%',
          backgroundColor: 'rgba(59,91,219,0.08)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}
      >
        <Ico sx={{ fontSize: 40, color: 'primary.main', opacity: 0.7 }} />
      </Box>
      <Typography variant="h6" fontWeight={600} color="text.primary">
        {title ?? 'Nothing here yet'}
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 320, textAlign: 'center' }}>
        {message ?? 'Get started by adding your first item.'}
      </Typography>
      {actionLabel && onAction && (
        <Button variant="contained" onClick={onAction} sx={{ mt: 1 }}>
          {actionLabel}
        </Button>
      )}
    </Box>
  );
}
