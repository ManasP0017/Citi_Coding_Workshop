import { useState, useEffect } from 'react';
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, InputAdornment, Alert, MenuItem,
  FormControlLabel, Checkbox, Skeleton, Tooltip, Chip, Typography, Avatar,
} from '@mui/material';
import EditRoundedIcon from '@mui/icons-material/EditRounded';
import DeleteRoundedIcon from '@mui/icons-material/DeleteRounded';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import AddRoundedIcon from '@mui/icons-material/AddRounded';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
import StarRoundedIcon from '@mui/icons-material/StarRounded';
import { membersAPI, teamsAPI } from '../services/api';
import usePermissions from '../hooks/usePermissions';
import ConfirmDialog from './common/ConfirmDialog';
import EmptyState from './common/EmptyState';
import PageHeader from './common/PageHeader';

const EMPTY_FORM = { name: '', email: '', team_id: '', role: 'member', is_team_leader: false, is_direct_staff: true, location: '' };

export default function MembersTab() {
  const [members, setMembers]         = useState([]);
  const [teams, setTeams]             = useState([]);
  const [loading, setLoading]         = useState(true);
  const [open, setOpen]               = useState(false);
  const [editingMember, setEditing]   = useState(null);
  const [search, setSearch]           = useState('');
  const [filterTeam, setFilterTeam]   = useState('');
  const [error, setError]             = useState('');
  const [saving, setSaving]           = useState(false);
  const [confirmId, setConfirmId]     = useState(null);
  const [deleting, setDeleting]       = useState(false);
  const [formData, setFormData]       = useState(EMPTY_FORM);
  const { canWrite, canDelete }       = usePermissions();

  const teamMap = Object.fromEntries(teams.map(t => [t.id, t.name]));

  const fetchMembers = async () => {
    setLoading(true);
    try {
      const params = {};
      if (search) params.search = search;
      if (filterTeam) params.team_id = filterTeam;
      const res = await membersAPI.getAll(params);
      setMembers(res.data.members || []);
    } catch { setError('Failed to fetch members'); }
    finally { setLoading(false); }
  };

  useEffect(() => { teamsAPI.getAll().then(r => setTeams(r.data.teams || [])); }, []);
  useEffect(() => { fetchMembers(); }, [search, filterTeam]);

  const openForm = (m = null) => {
    setEditing(m);
    setFormData(m ? { ...m } : EMPTY_FORM);
    setError('');
    setOpen(true);
  };
  const closeForm = () => { setOpen(false); setEditing(null); };
  const set = (k) => (e) => setFormData(f => ({ ...f, [k]: e.target.value }));
  const setCheck = (k) => (e) => setFormData(f => ({ ...f, [k]: e.target.checked }));

  const handleSubmit = async () => {
    setSaving(true); setError('');
    try {
      editingMember ? await membersAPI.update(editingMember.id, formData) : await membersAPI.create(formData);
      closeForm(); fetchMembers();
    } catch (err) { setError(err.response?.data?.error || 'Operation failed'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try { await membersAPI.delete(confirmId); fetchMembers(); }
    catch { setError('Failed to delete member'); }
    finally { setDeleting(false); setConfirmId(null); }
  };

  return (
    <Box className="animate-fade-in-up">
      <PageHeader
        title="Members"
        count={loading ? undefined : members.length}
        subtitle="Manage team membership and roles"
        action={canWrite && (
          <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={() => openForm()}>
            Add Member
          </Button>
        )}
      />

      <Box sx={{ display: 'flex', gap: 1.5, mb: 2, flexWrap: 'wrap' }}>
        <TextField
          placeholder="Search members…" value={search} onChange={e => setSearch(e.target.value)}
          sx={{ width: { xs: '100%', sm: 280 } }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchRoundedIcon fontSize="small" /></InputAdornment> }}
        />
        <TextField select label="Filter by team" value={filterTeam} onChange={e => setFilterTeam(e.target.value)} sx={{ minWidth: 180 }}>
          <MenuItem value="">All teams</MenuItem>
          {teams.map(t => <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>)}
        </TextField>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Member</TableCell>
                <TableCell>Team</TableCell>
                <TableCell>Role</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Location</TableCell>
                {(canWrite || canDelete) && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading
                ? Array.from({ length: 5 }).map((_, i) => (
                    <TableRow key={i}>
                      {[70, 50, 40, 80, 40, 0].map((w, j) => (
                        <TableCell key={j}>{w ? <Skeleton width={`${w}%`} /> : null}</TableCell>
                      ))}
                    </TableRow>
                  ))
                : members.map(m => (
                    <TableRow key={m.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                          <Avatar sx={{ width: 32, height: 32, fontSize: '0.8rem', bgcolor: 'secondary.main' }}>
                            {m.name?.charAt(0)?.toUpperCase()}
                          </Avatar>
                          <Box>
                            <Typography variant="body2" fontWeight={600}>{m.name}</Typography>
                            <Typography variant="caption" color="text.secondary">{m.email}</Typography>
                          </Box>
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">{teamMap[m.team_id] || <span style={{ color: '#9E9E9E' }}>No team</span>}</Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>{m.role}</Typography>
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          {m.is_team_leader && <Chip icon={<StarRoundedIcon />} label="Leader" size="small" color="warning" variant="outlined" sx={{ fontWeight: 600 }} />}
                          <Chip label={m.is_direct_staff ? 'Direct' : 'Non-direct'} size="small" color={m.is_direct_staff ? 'success' : 'default'} variant="outlined" sx={{ fontWeight: 600 }} />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">{m.location || '—'}</Typography>
                      </TableCell>
                      {(canWrite || canDelete) && (
                        <TableCell align="right">
                          {canWrite && <Tooltip title="Edit"><IconButton size="small" onClick={() => openForm(m)}><EditRoundedIcon fontSize="small" /></IconButton></Tooltip>}
                          {canDelete && <Tooltip title="Delete"><IconButton size="small" color="error" onClick={() => setConfirmId(m.id)}><DeleteRoundedIcon fontSize="small" /></IconButton></Tooltip>}
                        </TableCell>
                      )}
                    </TableRow>
                  ))
              }
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && members.length === 0 && (
          <EmptyState icon={PersonRoundedIcon} title="No members found" message="Try adjusting your search or add new members to get started." actionLabel={canWrite ? 'Add Member' : undefined} onAction={canWrite ? () => openForm() : undefined} />
        )}
      </Paper>

      <Dialog open={open} onClose={closeForm} maxWidth="sm" fullWidth>
        <DialogTitle>{editingMember ? 'Edit Member' : 'New Member'}</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          {error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth label="Full name *" value={formData.name} onChange={set('name')} autoFocus />
          <TextField fullWidth label="Email address *" type="email" value={formData.email} onChange={set('email')} />
          <TextField fullWidth select label="Team" value={formData.team_id} onChange={set('team_id')}>
            <MenuItem value="">No team</MenuItem>
            {teams.map(t => <MenuItem key={t.id} value={t.id}>{t.name}</MenuItem>)}
          </TextField>
          <TextField fullWidth label="Role / Job title" value={formData.role} onChange={set('role')} helperText='e.g. "engineer", "designer"' />
          <TextField fullWidth label="Location" value={formData.location} onChange={set('location')} />
          <Box sx={{ display: 'flex', gap: 2 }}>
            <FormControlLabel control={<Checkbox checked={formData.is_team_leader} onChange={setCheck('is_team_leader')} />} label="Team Leader" />
            <FormControlLabel control={<Checkbox checked={formData.is_direct_staff} onChange={setCheck('is_direct_staff')} />} label="Direct Staff" />
          </Box>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
          <Button onClick={closeForm} disabled={saving}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={saving || !formData.name.trim() || !formData.email.trim()}>
            {saving ? 'Saving…' : editingMember ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog open={!!confirmId} title="Remove member" message="This will permanently remove the member from the system." loading={deleting} onConfirm={handleDelete} onCancel={() => setConfirmId(null)} />
    </Box>
  );
}
