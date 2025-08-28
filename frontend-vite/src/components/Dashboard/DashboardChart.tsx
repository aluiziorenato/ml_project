import React, { useEffect, useState } from 'react';
import { Typography, Card, CircularProgress, Alert, Box } from "@mui/material";
import { ResponsiveContainer, LineChart, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts';
import { fetchDashboardMetrics } from '../../services/dashboardService.js';

const DashboardChart = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardMetrics()
      .then((metrics) => {
        setData(metrics);
        setLoading(false);
      })
      .catch(() => {
        setError('Erro ao carregar métricas');
        setLoading(false);
      });
  }, []);

  if (loading) return (
    <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 120 }}>
      <CircularProgress />
    </Box>
  );
  if (error) return <Alert severity="error">{error}</Alert>;

  return (
    <Card sx={{ p: 4, minHeight: 300, background: '#fff', boxShadow: 2 }}>
      <Typography variant="h6" color="textSecondary" sx={{ mb: 2 }}>Métricas do Dashboard</Typography>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="uv" stroke="#8884d8" />
          <Line type="monotone" dataKey="pv" stroke="#82ca9d" />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  );
};

export default DashboardChart;
