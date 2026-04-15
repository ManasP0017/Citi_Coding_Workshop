import { useState, useEffect, useCallback } from 'react';
import {
  Box, Grid, Card, CardContent, Typography, Skeleton,
  Alert, Button, Chip, Divider,
} from '@mui/material';
import GroupsRoundedIcon from '@mui/icons-material/GroupsRounded';
import PersonRoundedIcon from '@mui/icons-material/PersonRounded';
import LocationOffRoundedIcon from '@mui/icons-material/LocationOffRounded';
import WorkOffRoundedIcon from '@mui/icons-material/WorkOffRounded';
import TrendingDownRoundedIcon from '@mui/icons-material/TrendingDownRounded';
import AccountTreeRoundedIcon from '@mui/icons-material/AccountTreeRounded';
import RefreshRoundedIcon from '@mui/icons-material/RefreshRounded';
import FiberManualRecordIcon from '@mui/icons-material/FiberManualRecord';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RTooltip,
  ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from 'recharts';
import { insightsAPI } from '../services/api';
import useSSE from '../hooks/useSSE';

const METRICS = [
  { key: 'total_teams',                     label: 'Total Teams',                icon: GroupsRoundedIcon,          color: '#3B5BDB', bg: '#EEF2FF' },
  { key: 'total_members',                   label: 'Total Members',              icon: PersonRoundedIcon,          color: '#0CA678', bg: '#ECFDF5' },
  { key: 'teams_with_leader_not_colocated', label: 'Leader Not Co-located',      icon: LocationOffRoundedIcon,     color: '#E67700', bg: '#FFF7ED' },
  { key: 'teams_with_nondir_leader',        label: 'Non-direct Leader',          icon: WorkOffRoundedIcon,         color: '#7048E8', bg: '#F3F0FF' },
  { key: 'teams_nondir_ratio_above_20',     label: 'Non-direct Ratio >20%',      icon: TrendingDownRoundedIcon,    color: '#F03E3E', bg: '#FFF5F5' },
  { key: 'teams_reporting_to_org_leader',   label: 'Report to Org Leader',       icon: AccountTreeRoundedIcon,     color: '#1098AD', bg: '#E3FAFC' },
];

const PIE_COLORS = ['#3B5BDB', '#F03E3E'];

function MetricCard({ metric, value, loading }) {
  const { label, icon: Icon, color, bg } = metric;
  return (
    <Card sx={{ height: '100%' }} className="hover-lift">
      <CardContent sx={{ p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="caption" color="text.secondary" fontWeight={600} sx={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {label}
            </Typography>
            {loading
              ? <Skeleton width={60} height={48} sx={{ mt: 0.5 }} />
              : <Typography variant="h3" fontWeight={800} sx={{ color, mt: 0.5, lineHeight: 1.1 }}>
                  {value ?? '—'}
                </Typography>
            }
          </Box>
          <Box sx={{ width: 44, height: 44, borderRadius: '12px', bgcolor: bg, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
            <Icon sx={{ fontSize: 22, color }} />
          </Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export default function InsightsTab() {
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState('');
  const [live, setLive]       = useState(false);

  const fetchInsights = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const res = await insightsAPI.get();
      setData(res.data);
    } catch { setError('Failed to load insights'); }
    finally { setLoading(false); }
  }, []);

  useEffect(() => { fetchInsights(); }, [fetchInsights]);

  const handleSSE = useCallback((msg) => {
    if (msg.event === 'connected') { setLive(true); return; }
    const refresh = ['member.created','member.updated','member.deleted','team.created','team.updated','team.deleted','achievement.created','achievement.deleted'];
    if (refresh.includes(msg.event)) fetchInsights();
  }, [fetchInsights]);

  useSSE(handleSSE);

  const barData = METRICS.map(m => ({
    name: m.label.split(' ').slice(0, 2).join(' '),
    value: data?.[m.key] ?? 0,
    color: m.color,
  }));

  const directCount = (data?.total_members ?? 0) - (data?.teams_with_nondir_leader ?? 0);
  const pieData = [
    { name: 'Direct Staff', value: Math.max(0, directCount) },
    { name: 'Non-direct',   value: data?.teams_with_nondir_leader ?? 0 },
  ];

  return (
    <Box className="animate-fade-in-up">
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            <Typography variant="h5">Business Insights</Typography>
            <Chip
              size="small"
              icon={<FiberManualRecordIcon sx={{ fontSize: '10px !important', color: live ? '#36B37E !important' : '#637381 !important' }} />}
              label={live ? 'Live' : 'Connecting…'}
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 22, borderColor: live ? '#36B37E' : '#637381', color: live ? '#36B37E' : '#637381' }}
            />
          </Box>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Real-time organisational metrics — auto-refreshes on data changes
          </Typography>
        </Box>
        <Button startIcon={<RefreshRoundedIcon />} onClick={fetchInsights} variant="outlined" size="small" disabled={loading}>
          Refresh
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError('')}>{error}</Alert>}

      {/* Metric cards */}
      <Grid container spacing={2} sx={{ mb: 4 }} className="stagger-children">
        {METRICS.map(m => (
          <Grid item xs={12} sm={6} md={4} key={m.key} className="hover-lift">
            <MetricCard metric={m} value={data?.[m.key]} loading={loading} />
          </Grid>
        ))}
      </Grid>

      {/* Charts row */}
      <Grid container spacing={3}>
        {/* Bar chart — all metrics at a glance */}
        <Grid item xs={12} md={7}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>Metric Overview</Typography>
              <Divider sx={{ mb: 2 }} />
              {loading
                ? <Skeleton variant="rectangular" height={220} sx={{ borderRadius: 2 }} />
                : (
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={barData} margin={{ top: 4, right: 8, left: -16, bottom: 4 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(145,158,171,0.2)" />
                      <XAxis dataKey="name" tick={{ fontSize: 11, fill: '#637381' }} />
                      <YAxis tick={{ fontSize: 11, fill: '#637381' }} allowDecimals={false} />
                      <RTooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 16px rgba(0,0,0,0.12)' }} />
                      <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                        {barData.map((entry, index) => (
                          <Cell key={index} fill={entry.color} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                )
              }
            </CardContent>
          </Card>
        </Grid>

        {/* Pie chart — direct vs non-direct */}
        <Grid item xs={12} md={5}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>Staff Composition</Typography>
              <Divider sx={{ mb: 2 }} />
              {loading
                ? <Skeleton variant="circular" width={160} height={160} sx={{ mx: 'auto', mt: 2 }} />
                : (data?.total_members > 0
                  ? (
                    <ResponsiveContainer width="100%" height={220}>
                      <PieChart>
                        <Pie data={pieData} cx="50%" cy="45%" innerRadius={55} outerRadius={85} paddingAngle={3} dataKey="value">
                          {pieData.map((_, i) => <Cell key={i} fill={PIE_COLORS[i]} />)}
                        </Pie>
                        <Legend iconType="circle" iconSize={10} formatter={(v) => <span style={{ fontSize: 12, color: '#637381' }}>{v}</span>} />
                        <RTooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 16px rgba(0,0,0,0.12)' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  )
                  : (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 200 }}>
                      <Typography variant="body2" color="text.secondary">No member data yet</Typography>
                    </Box>
                  )
                )
              }
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
