import { useState, useEffect } from 'react';
import {
  Box, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Paper, IconButton, InputAdornment, Alert, Skeleton,
  Tooltip, Chip, Typography,
} from '@mui/material';
import EditRoundedIcon from '@mui/icons-material/EditRounded';
import DeleteRoundedIcon from '@mui/icons-material/DeleteRounded';
import SearchRoundedIcon from '@mui/icons-material/SearchRounded';
import AddRoundedIcon from '@mui/icons-material/AddRounded';
import GroupsRoundedIcon from '@mui/icons-material/GroupsRounded';
import LocationOnRoundedIcon from '@mui/icons-material/LocationOnRounded';
import { teamsAPI } from '../services/api';
import usePermissions from '../hooks/usePermissions';
import ConfirmDialog from './common/ConfirmDialog';
import EmptyState from './common/EmptyState';
import PageHeader from './common/PageHeader';

const EMPTY_FORM = { name: '', location: '', organization_leader_id: '', description: '' };

export default function TeamsTab() {
  const [teams, setTeams]           = useState([]);
  const [loading, setLoading]       = useState(true);
  const [open, setOpen]             = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  const [search, setSearch]         = useState('');
  const [error, setError]           = useState('');
  const [saving, setSaving]         = useState(false);
  const [confirmId, setConfirmId]   = useState(null);
  const [deleting, setDeleting]     = useState(false);
  const [formData, setFormData]     = useState(EMPTY_FORM);
  const { canWrite, canDelete }     = usePermissions();

  const fetchTeams = async () => {
    setLoading(true);
    try {
      const res = await teamsAPI.getAll({ search });
      setTeams(res.data.teams || []);
    } catch { setError('Failed to fetch teams'); }
    finally { setLoading(false); }
  };

  useEffect(() => { fetchTeams(); }, [search]);

  const openForm = (team = null) => {
    setEditingTeam(team);
    setFormData(team ? { ...team } : EMPTY_FORM);
    setError('');
    setOpen(true);
  };

  const closeForm = () => { setOpen(false); setEditingTeam(null); };

  const set = (k) => (e) => setFormData(f => ({ ...f, [k]: e.target.value }));

  const handleSubmit = async () => {
    setSaving(true);
    setError('');
    try {
      editingTeam ? await teamsAPI.update(editingTeam.id, formData) : await teamsAPI.create(formData);
      closeForm();
      fetchTeams();
    } catch (err) { setError(err.response?.data?.error || 'Operation failed'); }
    finally { setSaving(false); }
  };

  const handleDelete = async () => {
    setDeleting(true);
    try { await teamsAPI.delete(confirmId); fetchTeams(); }
    catch { setError('Failed to delete team'); }
    finally { setDeleting(false); setConfirmId(null); }
  };

  return (
    <Box className="animate-fade-in-up">
      <PageHeader
        title="Teams"
        count={loading ? undefined : teams.length}
        subtitle="Manage your organization's teams"
        action={canWrite && (
          <Button variant="contained" startIcon={<AddRoundedIcon />} onClick={() => openForm()}>
            Add Team
          </Button>
        )}
      />

      {/* Search bar */}
      <Box sx={{ mb: 2 }}>
        <TextField
          placeholder="Search by name or description…"
          value={search} onChange={e => setSearch(e.target.value)}
          sx={{ width: { xs: '100%', sm: 360 } }}
          InputProps={{ startAdornment: <InputAdornment position="start"><SearchRoundedIcon fontSize="small" /></InputAdornment> }}
        />
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Team Name</TableCell>
                <TableCell>Location</TableCell>
                <TableCell>Description</TableCell>
                {(canWrite || canDelete) && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {loading
                ? Array.from({ length: 4 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton width="60%" /></TableCell>
                      <TableCell><Skeleton width="40%" /></TableCell>
                      <TableCell><Skeleton width="80%" /></TableCell>
                      {(canWrite || canDelete) && <TableCell />}
                    </TableRow>
                  ))
                : teams.map(team => (
                    <TableRow key={team.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Box sx={{ width: 32, height: 32, borderRadius: '8px', bgcolor: 'primary.main', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                            <GroupsRoundedIcon sx={{ fontSize: 16, color: '#fff' }} />
                          </Box>
                          <Typography variant="body2" fontWeight={600}>{team.name}</Typography>
                        </Box>
                      </TableCell>
                      <TableCell>
                        {team.location
                          ? <Chip icon={<LocationOnRoundedIcon />} label={team.location} size="small" variant="outlined" sx={{ fontWeight: 500 }} />
                          : <Typography variant="caption" color="text.disabled">—</Typography>}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary" sx={{ maxWidth: 320, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {team.description || '—'}
                        </Typography>
                      </TableCell>
                      {(canWrite || canDelete) && (
                        <TableCell align="right">
                          {canWrite && (
                            <Tooltip title="Edit"><IconButton size="small" onClick={() => openForm(team)}><EditRoundedIcon fontSize="small" /></IconButton></Tooltip>
                          )}
                          {canDelete && (
                            <Tooltip title="Delete"><IconButton size="small" color="error" onClick={() => setConfirmId(team.id)}><DeleteRoundedIcon fontSize="small" /></IconButton></Tooltip>
                          )}
                        </TableCell>
                      )}
                    </TableRow>
                  ))
              }
            </TableBody>
          </Table>
        </TableContainer>
        {!loading && teams.length === 0 && (
          <EmptyState
            icon={GroupsRoundedIcon}
            title="No teams yet"
            message="Create your first team to get started with team management."
            actionLabel={canWrite ? 'Add Team' : undefined}
            onAction={canWrite ? () => openForm() : undefined}
          />
        )}
      </Paper>

      {/* Form dialog */}
      <Dialog open={open} onClose={closeForm} maxWidth="sm" fullWidth>
        <DialogTitle>{editingTeam ? 'Edit Team' : 'New Team'}</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          {error && <Alert severity="error" onClose={() => setError('')}>{error}</Alert>}
          <TextField fullWidth label="Team name *" value={formData.name} onChange={set('name')} autoFocus />
          <TextField fullWidth label="Location" value={formData.location} onChange={set('location')} />
          <TextField fullWidth label="Org Leader ID" value={formData.organization_leader_id} onChange={set('organization_leader_id')} helperText="Optional — member ID of the organisation leader" />
          <TextField fullWidth label="Description" multiline rows={3} value={formData.description} onChange={set('description')} />
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 2, gap: 1 }}>
          <Button onClick={closeForm} disabled={saving}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" disabled={saving || !formData.name.trim()}>
            {saving ? 'Saving…' : editingTeam ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>

      <ConfirmDialog
        open={!!confirmId}
        title="Delete team"
        message="This will permanently delete the team. All member assignments will be cleared."
        loading={deleting}
        onConfirm={handleDelete}
        onCancel={() => setConfirmId(null)}
      />
    </Box>
  );
}
