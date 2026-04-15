import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box, TextField, Button, Typography, Alert,
  InputAdornment, IconButton, CircularProgress,
} from '@mui/material';
import VisibilityRoundedIcon from '@mui/icons-material/VisibilityRounded';
import VisibilityOffRoundedIcon from '@mui/icons-material/VisibilityOffRounded';
import GroupsRoundedIcon from '@mui/icons-material/GroupsRounded';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [email, setEmail]       = useState('');
  const [password, setPassword] = useState('');
  const [showPw, setShowPw]     = useState(false);
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);
  const { login } = useAuth();
  const navigate  = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      navigate('/app/insights');
    } catch (err) {
      setError(err.response?.data?.error || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Left panel — brand gradient */}
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          flex: 1,
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          gap: 3,
          background: 'linear-gradient(145deg, #2F4AC0 0%, #3B5BDB 40%, #748FFC 100%)',
          color: '#fff',
          p: 6,
        }}
      >
        <Box sx={{ width: 72, height: 72, borderRadius: '20px', bgcolor: 'rgba(255,255,255,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <GroupsRoundedIcon sx={{ fontSize: 40 }} />
        </Box>
        <Typography variant="h3" fontWeight={800} textAlign="center">TeamHub</Typography>
        <Typography variant="h6" sx={{ opacity: 0.85, fontWeight: 400, textAlign: 'center', maxWidth: 320 }}>
          Manage your teams, track achievements, and drive organizational insights.
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mt: 2, flexWrap: 'wrap', justifyContent: 'center' }}>
          {['Teams', 'Members', 'Achievements', 'Insights'].map(f => (
            <Box key={f} sx={{ px: 2, py: 0.75, bgcolor: 'rgba(255,255,255,0.15)', borderRadius: 99, fontSize: '0.85rem', fontWeight: 600 }}>
              {f}
            </Box>
          ))}
        </Box>
      </Box>

      {/* Right panel — form */}
      <Box
        sx={{
          flex: { xs: 1, md: '0 0 440px' },
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          px: { xs: 3, sm: 6 },
          py: 6,
          bgcolor: 'background.paper',
        }}
      >
        <Box sx={{ maxWidth: 360, width: '100%', mx: 'auto' }}>
          <Typography variant="h4" gutterBottom>Welcome back</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            Sign in to your TeamHub account
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth label="Email address" type="email"
              value={email} onChange={e => setEmail(e.target.value)}
              required autoFocus autoComplete="email"
            />
            <TextField
              fullWidth label="Password"
              type={showPw ? 'text' : 'password'}
              value={password} onChange={e => setPassword(e.target.value)}
              required autoComplete="current-password"
              InputProps={{
                endAdornment: (
                  <InputAdornment position="end">
                    <IconButton size="small" onClick={() => setShowPw(v => !v)}>
                      {showPw ? <VisibilityOffRoundedIcon fontSize="small" /> : <VisibilityRoundedIcon fontSize="small" />}
                    </IconButton>
                  </InputAdornment>
                ),
              }}
            />
            <Button
              fullWidth variant="contained" type="submit"
              size="large" disabled={loading}
              sx={{ mt: 1, py: 1.3 }}
              startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
            >
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
            Don&apos;t have an account?{' '}
            <Link to="/register" style={{ color: '#3B5BDB', fontWeight: 600 }}>
              Create one
            </Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
