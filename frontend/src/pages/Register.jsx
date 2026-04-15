import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Box, TextField, Button, Typography, Alert,
  MenuItem, CircularProgress, Chip,
} from '@mui/material';
import GroupsRoundedIcon from '@mui/icons-material/GroupsRounded';
import { useAuth } from '../contexts/AuthContext';

const ROLES = [
  { value: 'admin',       label: 'Admin',       desc: 'Full access'            },
  { value: 'manager',     label: 'Manager',     desc: 'Create, edit, delete'   },
  { value: 'contributor', label: 'Contributor', desc: 'Create & edit'          },
  { value: 'viewer',      label: 'Viewer',      desc: 'Read-only access'       },
];

export default function Register() {
  const [form, setForm]       = useState({ name: '', email: '', password: '', role: 'contributor' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate     = useNavigate();

  const set = (k) => (e) => setForm(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await register(form.email, form.password, form.name, form.role);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      {/* Left brand panel */}
      <Box
        sx={{
          display: { xs: 'none', md: 'flex' },
          flex: 1, flexDirection: 'column', justifyContent: 'center', alignItems: 'center',
          gap: 3, p: 6, color: '#fff',
          background: 'linear-gradient(145deg, #099268 0%, #0CA678 50%, #38D9A9 100%)',
        }}
      >
        <Box sx={{ width: 72, height: 72, borderRadius: '20px', bgcolor: 'rgba(255,255,255,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <GroupsRoundedIcon sx={{ fontSize: 40 }} />
        </Box>
        <Typography variant="h3" fontWeight={800}>Join TeamHub</Typography>
        <Typography variant="h6" sx={{ opacity: 0.85, fontWeight: 400, textAlign: 'center', maxWidth: 320 }}>
          Create your account and start collaborating with your team today.
        </Typography>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5, mt: 2, width: '100%', maxWidth: 300 }}>
          {ROLES.map(r => (
            <Box key={r.value} sx={{ display: 'flex', alignItems: 'center', gap: 2, bgcolor: 'rgba(255,255,255,0.12)', borderRadius: 2, px: 2, py: 1.25 }}>
              <Chip label={r.label} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.25)', color: '#fff', fontWeight: 700, fontSize: '0.72rem' }} />
              <Typography variant="caption" sx={{ opacity: 0.9 }}>{r.desc}</Typography>
            </Box>
          ))}
        </Box>
      </Box>

      {/* Right form panel */}
      <Box
        sx={{
          flex: { xs: 1, md: '0 0 440px' },
          display: 'flex', flexDirection: 'column', justifyContent: 'center',
          px: { xs: 3, sm: 6 }, py: 6, bgcolor: 'background.paper',
        }}
      >
        <Box sx={{ maxWidth: 360, width: '100%', mx: 'auto' }} className="animate-scale-in">
          <Typography variant="h4" gutterBottom>Create account</Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
            Fill in the details below to get started
          </Typography>

          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

          <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField fullWidth label="Full name" value={form.name} onChange={set('name')} required autoFocus />
            <TextField fullWidth label="Email address" type="email" value={form.email} onChange={set('email')} required />
            <TextField fullWidth label="Password" type="password" value={form.password} onChange={set('password')} required helperText="At least 8 characters" />
            <TextField fullWidth select label="Role" value={form.role} onChange={set('role')} required>
              {ROLES.map(r => (
                <MenuItem key={r.value} value={r.value}>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>{r.label}</Typography>
                    <Typography variant="caption" color="text.secondary">{r.desc}</Typography>
                  </Box>
                </MenuItem>
              ))}
            </TextField>
            <Button
              fullWidth variant="contained" type="submit" size="large"
              disabled={loading} className="btn-press" sx={{ mt: 1, py: 1.3 }}
              startIcon={loading ? <CircularProgress size={16} color="inherit" /> : null}
            >
              {loading ? 'Creating account…' : 'Create account'}
            </Button>
          </Box>

          <Typography variant="body2" color="text.secondary" sx={{ mt: 3, textAlign: 'center' }}>
            Already have an account?{' '}
            <Link to="/login" style={{ color: '#3B5BDB', fontWeight: 600 }}>Sign in</Link>
          </Typography>
        </Box>
      </Box>
    </Box>
  );
}
