import { useState, useEffect } from 'react';
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, InputAdornment, Alert, MenuItem,
  Skeleton, Tooltip, Chip, Typography,
} from '@mui/material';
import EditRoundedIcon from '@mui/icons-material/EditRounded';
import DeleteRoundedIcon from '@mui/icons-material/DeleteRounded';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import AddRoundedIcon from '@mui/icons-material/AddRounded';
import EmojiEventsRoundedIcon from '@mui/icons-material/EmojiEventsRounded';
import { achievementsAPI, teamsAPI } from '../services/api';
import usePermissions from '../hooks/usePermissions';
import ConfirmDialog from './common/ConfirmDialog';
import EmptyState from './common/EmptyState';
import PageHeader from './common/PageHeader';

const MONTHS = ['January','February','March','April','May','June','July','August','September','October','November','December'];
const CY = new Date().getFullYear();
const YEARS = Array.from({ length: 6 }, (_, i) => CY - 2 + i);
const EMPTY_FORM = { title: '', description: '', team_id: '', month: '', year: CY };

const MONTH_COLORS = {
  January: '#3B5BDB', February: '#7048E8', March: '#E64980', April: '#F03E3E',
  May: '#E67700', June: '#2F9E44', July: '#0CA678', August: '#1098AD',
  September: '#1971C2', October: '#862E9C', November: '#C2255C', December: '#2C2E33',
};

export default function AchievementsTab() {
  const [achievements, setAchievements] = useState([]);
  const [teams, setTeams]               = useState([]);
  const [loading, setLoading]           = useState(true);
  const [open, setOpen]                 = useState(false);
  const [editing, setEditing]           = useState(null);
  const [search, setSearch]             = useState('');
  const [filterMonth, setFilterMonth]   = useState('');
  const [filterYear, setFilterYear]     = useState('');
  const [error, setError]               = useState('');
  const [saving, setSaving]             = useState(false);
  const [confirmId, setConfirmId]       = useState(null);
  const [deleting, setDeleting]         = useState(false);
  const [formData, setFormData]         = useState(EMPTY_FORM);
  const { canWrite, canDelete }         = usePermissions();

  const teamMap = Object.fromEntries(teams.map(t => [t.id, t.name]));

  const fetchAchievements = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (filterMonth) params.month = filterMonth;
      if (filterYear) params.year = filterYear;
      const res = await achievementsAPI.getAll(params);
      setAchievements(res.data.achievements || []);
    } catch { setError('Failed to fetch achievements'); }
    finally { setLoading(false); }
  };

  useEffect(() => { teamsAPI.getAll().then(r => setTeams(r.data.teams || [])); }, []);
  useEffect(() => { fetchAchievements(); }, [search, filterMonth, filterYear]);

  const openForm = (a = null) => {
    setEditing(a);
    setFormData(a ? { ...a } : EMPTY_FORM);
    setError('');
    setOpen(true);
  };
  const closeForm = () => { setOpen(false); setEditing(null); };
  const set = (k) => (e) => setFormData(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async () => {
    setSaving(true); setError('');
    try {
      editing ? await achievementsAPI.update(editing.id, formData) : await achievementsAPI.create(formData);
      closeForm(); fetchAchievements();
    } catch (err) { setError(err.response?.data?.error || 'Operation failed'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try { await achievementsAPI.delete(confirmId); fetchAchievements(); }
    catch { setError('Failed to delete achievement'); }
    finally { setDeleting(false); setConfirmId(null); }
  };

  return (
    <Box>
      <PageHeader
        title="Achievements"
        count={loading ? undefined : achievements.length}
        subtitle="Track team accomplishments by month"
        action={canWrite && (
          <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={() => openForm()}>
            Add Achievement
          </Button>
        )}
      />

      <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search achievements…" value={search} onChange={e => setSearch(e.target.value)}
          sx={{ width: { xs: '100%', sm: 260 } }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchRoundedIcon fontSize="small" /></InputAdornment> }}
        />
        <TextField select label="Month" value={filterMonth} onChange={e => setFilterMonth(e.target.value)} sx={{ minWidth: 140 }}>
          <MenuItem value="">All months</MenuItem>
          {MONTHS.map(m => <MenuItem key={m} value={m}>{m}</MenuItem>)}
        </TextField>
        <TextField select label="Year" value={filterYear} onChange={e => setFilterYear(e.target.value)} sx={{ minWidth: 110 }}>
          <MenuItem value="">All years</MenuItem>
          {YEARS.map(y => <MenuItem key={y} value={y}>{y}</MenuItem>)}
        </TextField>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Achievement</TableCell>
                <TableCell>Team</TableCell>
                <TableCell>Period</TableCell>
                <TableCell>Description</TableCell>
                {(canWrite || canDelete) && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading
                ? Array.from({ length: 4 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton width="55%" /></TableCell>
                      <TableCell><Skeleton width="45%" /></TableCell>
                      <TableCell><Skeleton width="35%" /></TableCell>
                      <TableCell><Skeleton width="75%" /></TableCell>
                      {(canWrite || canDelete) && <TableCell />}
                    </TableRow>
                  ))
                : achievements.map(a => (
                    <TableRow key={a.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ width: 32, height: 32, borderRadius: '8px', background: 'linear-gradient(135deg, #F59E0B, #FCD34D)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                            <EmojiEventsRoundedIcon sx={{ fontSize: 16, color: '#fff' }} />
                          </Box>
                          <Typography variant="body2" fontWeight={600}>{a.title}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{teamMap[a.team_id] || <span style={{ color: '#9E9E9E' }}>No team</span>}</Typography>
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`${a.month} ${a.year}`}
                          size="small"
                          sx={{ fontWeight: 600, bgcolor: `${MONTH_COLORS[a.month] ?? '#637381'}18`, color: MONTH_COLORS[a.month] ?? '#637381' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 280, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {a.description || '—'}
                        </Typography>
                      </TableCell>
                      {(canWrite || canDelete) && (
                        <TableCell align="right">
                          {canWrite && <Tooltip title="Edit"><IconButton size="small" onClick={() => openForm(a)}><EditRoundedIcon fontSize="small" /></IconButton></Tooltip>}
                          {canDelete && <Tooltip title="Delete"><IconButton size="small" color="error" onClick={() => setConfirmId(a.id)}><DeleteRoundedIcon fontSize="small" /></IconButton></Tooltip>}
                        </TableCell>
                      )}
                    </TableRow>
                  ))
              }
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && achievements.length === 0 && (
          <EmptyState icon={EmojiEventsRoundedIcon} title="No achievements yet" message="Record your team's first achievement to start tracking progress." actionLabel={canWrite ? 'Add Achievement' : undefined} onAction={canWrite ? () => openForm() : undefined} />
        )}
      </Paper>

      <Dialog open={open} onClose={closeForm} maxWidth="sm" fullWidth>
        <DialogTitle>{editing ? 'Edit Achievement' : 'New Achievement'}</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          {error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth label="Title *" value={formData.title} onChange={set('title')} autoFocus />
          <TextField fullWidth label="Description" multiline rows={3} value={formData.description} onChange={set('description')} />
          <TextField fullWidth select label="Team *" value={formData.team_id} onChange={set('team_id')}>
            {teams.map(t => <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>)}
          </TextField>
          <Box sx={{ display: 'flex', gap: 1.5 }}>
            <TextField fullWidth select label="Month *" value={formData.month} onChange={set('month')}>
              {MONTHS.map(m => <MenuItem key={m} value={m}>{m}</MenuItem>)}
            </TextField>
            <TextField fullWidth select label="Year *" value={formData.year} onChange={e => setFormData(f => ({ ...f, year: parseInt(e.target.value) }))}>
              {YEARS.map(y => <MenuItem key={y} value={y}>{y}</MenuItem>)}
            </TextField>
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
          <Button onClick={closeForm} disabled={saving}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={saving || !formData.title.trim() || !formData.team_id || !formData.month}>
            {saving ? 'Saving…' : editing ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog open={!!confirmId} title="Delete achievement" message="This will permanently remove the achievement record." loading={deleting} onConfirm={handleDelete} onCancel={() => setConfirmId(null)} />
    </Box>
  );
}
