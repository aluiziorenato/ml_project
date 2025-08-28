import React, { useEffect, useState } from 'react';
import { Box, TextField, Button, Typography, TableContainer, Paper, Table, TableHead, TableRow, TableCell, TableBody, CircularProgress, Alert } from "@mui/material";
import { fetchDashboardTableData } from '../../services/dashboardService.js';

const DashboardTable = () => {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState('');
  const [minValue, setMinValue] = useState('');
  const [maxValue, setMaxValue] = useState('');

  useEffect(() => {
    fetchDashboardTableData({ search: filter, minValue, maxValue })
      .then((data) => {
        setRows(data);
        setLoading(false);
      })
      .catch(() => {
        setError('Erro ao carregar dados da tabela');
        setLoading(false);
      });
  }, [filter, minValue, maxValue]);

  const handleExport = () => {
    if (!rows.length) {
      alert('Nenhum dado para exportar');
      return;
    }
    const header = 'ID,Nome,Valor\n';
    const csvRows = rows.map(row => `${row.id},${row.name},${row.value}`).join('\n');
    const csv = header + csvRows;
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'dashboard-dados.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <Box>
      <Box sx={{ mb: 3, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <TextField
          label="Filtrar por nome"
          variant="outlined"
          value={filter}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setFilter(e.target.value)}
          size="small"
          sx={{ width: 180 }}
        />
        <TextField
          label="Valor mínimo"
          variant="outlined"
          value={minValue}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMinValue(e.target.value)}
          size="small"
          sx={{ width: 120 }}
          type="number"
        />
        <TextField
          label="Valor máximo"
          variant="outlined"
          value={maxValue}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setMaxValue(e.target.value)}
          size="small"
          sx={{ width: 120 }}
          type="number"
        />
        <Button variant="contained" color="primary">Filtrar</Button>
        <Button variant="outlined" onClick={handleExport}>Exportar</Button>
      </Box>
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 120 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : (
        <TableContainer component={Paper} sx={{ background: '#fff', boxShadow: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Nome</TableCell>
                <TableCell>Valor</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {rows.map((row: any) => (
                <TableRow key={row.id}>
                  <TableCell>{row.id}</TableCell>
                  <TableCell>{row.name}</TableCell>
                  <TableCell>{row.value}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default DashboardTable;
