import React from "react";
import { Grid, Box, Typography, Table, TableHead, TableRow, TableCell, TableBody, Paper } from "@mui/material";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

// Mock de intenções de busca
const mockIntencoes = Array.from({ length: 50 }, (_, i) => ({
  palavra: `Palavra-chave ${i + 1}`,
  relevancia: Math.floor(Math.random() * 100),
  volume: Math.floor(Math.random() * 5000 + 100),
  ctr: parseFloat((Math.random() * 0.2 + 0.05).toFixed(2)),
  conversao: parseFloat((Math.random() * 0.15 + 0.01).toFixed(2)),
  posicao: i + 1,
})).sort((a, b) => b.relevancia - a.relevancia);

export default function IntencoesBuscaDashboard() {
  return (
    <Paper sx={{ p: 2, width: '100%', height: 600 }}>
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 700 }}>
        Intenções de Busca - Top 50
      </Typography>
      <Grid container spacing={2} sx={{ height: '100%' }}>
        {/* Gráfico à esquerda */}
        <Grid sx={{ height: '100%' }}>
          <Box sx={{ height: 520 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockIntencoes.slice(0, 20)} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" dataKey="relevancia" hide={false} />
                <YAxis type="category" dataKey="palavra" width={120} />
                <Tooltip />
                <Bar dataKey="relevancia" fill="#1976d2">
                  {mockIntencoes.slice(0, 20).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={index === 0 ? '#388e3c' : '#1976d2'} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </Box>
        </Grid>
        {/* Tabela à direita */}
        <Grid sx={{ height: '100%', overflowY: 'auto' }}>
          <Table size="small" stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell>Posição</TableCell>
                <TableCell>Palavra-chave</TableCell>
                <TableCell>Relevância</TableCell>
                <TableCell>Volume</TableCell>
                <TableCell>CTR</TableCell>
                <TableCell>Conversão</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {mockIntencoes.map((row, i) => (
                <TableRow key={i}>
                  <TableCell>{row.posicao}</TableCell>
                  <TableCell>{row.palavra}</TableCell>
                  <TableCell>{row.relevancia}</TableCell>
                  <TableCell>{row.volume}</TableCell>
                  <TableCell>{(row.ctr * 100).toFixed(1)}%</TableCell>
                  <TableCell>{(row.conversao * 100).toFixed(1)}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Grid>
      </Grid>
    </Paper>
  );
}
