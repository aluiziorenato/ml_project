import React, { useState } from "react";
import { Grid, Typography, Card, CardContent, ButtonGroup, Button, Box, Divider, IconButton, Tooltip as MuiTooltip } from "@mui/material";
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useNavigate } from 'react-router-dom';
import BarChartIcon from '@mui/icons-material/BarChart';
import { ResponsiveContainer, LineChart, CartesianGrid, XAxis, YAxis, Tooltip, Legend, Line } from 'recharts';
import { BarChart, Bar, Cell } from 'recharts';

export default function MetricasPage() {
  const navigate = useNavigate();
  // Mock de dados para diferentes intervalos
  const mockMetricas = {
    7: [
      { date: '22/08', visitas: 120, vendas: 10, vendas_pub: 6, vendas_org: 4, acos: 0.22, roi: 2.1 },
      { date: '23/08', visitas: 140, vendas: 12, vendas_pub: 7, vendas_org: 5, acos: 0.18, roi: 2.3 },
      { date: '24/08', visitas: 110, vendas: 8, vendas_pub: 5, vendas_org: 3, acos: 0.25, roi: 1.9 },
      { date: '25/08', visitas: 160, vendas: 15, vendas_pub: 9, vendas_org: 6, acos: 0.20, roi: 2.5 },
      { date: '26/08', visitas: 130, vendas: 11, vendas_pub: 6, vendas_org: 5, acos: 0.21, roi: 2.2 },
      { date: '27/08', visitas: 150, vendas: 13, vendas_pub: 8, vendas_org: 5, acos: 0.19, roi: 2.4 },
      { date: '28/08', visitas: 170, vendas: 16, vendas_pub: 10, vendas_org: 6, acos: 0.17, roi: 2.6 },
    ],
    15: [
      { date: '14/08', visitas: 90, vendas: 7, vendas_pub: 4, vendas_org: 3, acos: 0.28, roi: 1.7 },
      { date: '15/08', visitas: 100, vendas: 8, vendas_pub: 5, vendas_org: 3, acos: 0.26, roi: 1.8 },
      { date: '16/08', visitas: 110, vendas: 9, vendas_pub: 5, vendas_org: 4, acos: 0.24, roi: 2.0 },
      { date: '17/08', visitas: 120, vendas: 10, vendas_pub: 6, vendas_org: 4, acos: 0.22, roi: 2.1 },
      { date: '18/08', visitas: 130, vendas: 11, vendas_pub: 7, vendas_org: 4, acos: 0.20, roi: 2.3 },
      { date: '19/08', visitas: 140, vendas: 12, vendas_pub: 8, vendas_org: 4, acos: 0.19, roi: 2.4 },
      { date: '20/08', visitas: 150, vendas: 13, vendas_pub: 9, vendas_org: 4, acos: 0.18, roi: 2.5 },
      { date: '21/08', visitas: 160, vendas: 14, vendas_pub: 10, vendas_org: 4, acos: 0.17, roi: 2.6 },
      { date: '22/08', visitas: 170, vendas: 15, vendas_pub: 11, vendas_org: 4, acos: 0.16, roi: 2.7 },
      { date: '23/08', visitas: 180, vendas: 16, vendas_pub: 12, vendas_org: 4, acos: 0.15, roi: 2.8 },
      { date: '24/08', visitas: 190, vendas: 17, vendas_pub: 13, vendas_org: 4, acos: 0.14, roi: 2.9 },
      { date: '25/08', visitas: 200, vendas: 18, vendas_pub: 14, vendas_org: 4, acos: 0.13, roi: 3.0 },
      { date: '26/08', visitas: 210, vendas: 19, vendas_pub: 15, vendas_org: 4, acos: 0.12, roi: 3.1 },
      { date: '27/08', visitas: 220, vendas: 20, vendas_pub: 16, vendas_org: 4, acos: 0.11, roi: 3.2 },
      { date: '28/08', visitas: 230, vendas: 21, vendas_pub: 17, vendas_org: 4, acos: 0.10, roi: 3.3 },
    ],
    30: [
      { date: '30/07', visitas: 60, vendas: 4, vendas_pub: 2, vendas_org: 2, acos: 0.32, roi: 1.3 },
      { date: '31/07', visitas: 70, vendas: 5, vendas_pub: 3, vendas_org: 2, acos: 0.30, roi: 1.4 },
      { date: '01/08', visitas: 80, vendas: 6, vendas_pub: 3, vendas_org: 3, acos: 0.28, roi: 1.5 },
      { date: '02/08', visitas: 90, vendas: 7, vendas_pub: 4, vendas_org: 3, acos: 0.26, roi: 1.6 },
      { date: '03/08', visitas: 100, vendas: 8, vendas_pub: 4, vendas_org: 4, acos: 0.24, roi: 1.7 },
      { date: '04/08', visitas: 110, vendas: 9, vendas_pub: 5, vendas_org: 4, acos: 0.22, roi: 1.8 },
      { date: '05/08', visitas: 120, vendas: 10, vendas_pub: 5, vendas_org: 5, acos: 0.20, roi: 1.9 },
      { date: '06/08', visitas: 130, vendas: 11, vendas_pub: 6, vendas_org: 5, acos: 0.18, roi: 2.0 },
      { date: '07/08', visitas: 140, vendas: 12, vendas_pub: 6, vendas_org: 6, acos: 0.16, roi: 2.1 },
      { date: '08/08', visitas: 150, vendas: 13, vendas_pub: 7, vendas_org: 6, acos: 0.14, roi: 2.2 },
      { date: '09/08', visitas: 160, vendas: 14, vendas_pub: 7, vendas_org: 7, acos: 0.12, roi: 2.3 },
      { date: '10/08', visitas: 170, vendas: 15, vendas_pub: 8, vendas_org: 7, acos: 0.10, roi: 2.4 },
      { date: '11/08', visitas: 180, vendas: 16, vendas_pub: 8, vendas_org: 8, acos: 0.09, roi: 2.5 },
      { date: '12/08', visitas: 190, vendas: 17, vendas_pub: 9, vendas_org: 8, acos: 0.08, roi: 2.6 },
      { date: '13/08', visitas: 200, vendas: 18, vendas_pub: 9, vendas_org: 9, acos: 0.07, roi: 2.7 },
      { date: '14/08', visitas: 210, vendas: 19, vendas_pub: 10, vendas_org: 9, acos: 0.06, roi: 2.8 },
      { date: '15/08', visitas: 220, vendas: 20, vendas_pub: 10, vendas_org: 10, acos: 0.05, roi: 2.9 },
      { date: '16/08', visitas: 230, vendas: 21, vendas_pub: 11, vendas_org: 10, acos: 0.04, roi: 3.0 },
      { date: '17/08', visitas: 240, vendas: 22, vendas_pub: 11, vendas_org: 11, acos: 0.03, roi: 3.1 },
      { date: '18/08', visitas: 250, vendas: 23, vendas_pub: 12, vendas_org: 11, acos: 0.02, roi: 3.2 },
      { date: '19/08', visitas: 260, vendas: 24, vendas_pub: 12, vendas_org: 12, acos: 0.01, roi: 3.3 },
      { date: '20/08', visitas: 270, vendas: 25, vendas_pub: 13, vendas_org: 12, acos: 0.01, roi: 3.4 },
      { date: '21/08', visitas: 280, vendas: 26, vendas_pub: 13, vendas_org: 13, acos: 0.01, roi: 3.5 },
      { date: '22/08', visitas: 290, vendas: 27, vendas_pub: 14, vendas_org: 13, acos: 0.01, roi: 3.6 },
      { date: '23/08', visitas: 300, vendas: 28, vendas_pub: 14, vendas_org: 14, acos: 0.01, roi: 3.7 },
      { date: '24/08', visitas: 310, vendas: 29, vendas_pub: 15, vendas_org: 14, acos: 0.01, roi: 3.8 },
      { date: '25/08', visitas: 320, vendas: 30, vendas_pub: 15, vendas_org: 15, acos: 0.01, roi: 3.9 },
      { date: '26/08', visitas: 330, vendas: 31, vendas_pub: 16, vendas_org: 15, acos: 0.01, roi: 4.0 },
      { date: '27/08', visitas: 340, vendas: 32, vendas_pub: 16, vendas_org: 16, acos: 0.01, roi: 4.1 },
      { date: '28/08', visitas: 350, vendas: 33, vendas_pub: 17, vendas_org: 16, acos: 0.01, roi: 4.2 },
    ],
    60: [
      { date: '30/06', visitas: 40, vendas: 2, vendas_pub: 1, vendas_org: 1, acos: 0.35, roi: 1.1 },
      { date: '01/07', visitas: 45, vendas: 2, vendas_pub: 1, vendas_org: 1, acos: 0.34, roi: 1.2 },
      { date: '02/07', visitas: 50, vendas: 3, vendas_pub: 2, vendas_org: 1, acos: 0.33, roi: 1.3 },
      { date: '03/07', visitas: 55, vendas: 3, vendas_pub: 2, vendas_org: 1, acos: 0.32, roi: 1.4 },
      { date: '04/07', visitas: 60, vendas: 4, vendas_pub: 2, vendas_org: 2, acos: 0.31, roi: 1.5 },
      { date: '05/07', visitas: 65, vendas: 4, vendas_pub: 2, vendas_org: 2, acos: 0.30, roi: 1.6 },
      { date: '06/07', visitas: 70, vendas: 5, vendas_pub: 3, vendas_org: 2, acos: 0.29, roi: 1.7 },
      { date: '07/07', visitas: 75, vendas: 5, vendas_pub: 3, vendas_org: 2, acos: 0.28, roi: 1.8 },
      { date: '08/07', visitas: 80, vendas: 6, vendas_pub: 3, vendas_org: 3, acos: 0.27, roi: 1.9 },
      { date: '09/07', visitas: 85, vendas: 6, vendas_pub: 3, vendas_org: 3, acos: 0.26, roi: 2.0 },
      { date: '10/07', visitas: 90, vendas: 7, vendas_pub: 4, vendas_org: 3, acos: 0.25, roi: 2.1 },
      { date: '11/07', visitas: 95, vendas: 7, vendas_pub: 4, vendas_org: 3, acos: 0.24, roi: 2.2 },
      { date: '12/07', visitas: 100, vendas: 8, vendas_pub: 4, vendas_org: 4, acos: 0.23, roi: 2.3 },
      { date: '13/07', visitas: 105, vendas: 8, vendas_pub: 4, vendas_org: 4, acos: 0.22, roi: 2.4 },
      { date: '14/07', visitas: 110, vendas: 9, vendas_pub: 5, vendas_org: 4, acos: 0.21, roi: 2.5 },
      { date: '15/07', visitas: 115, vendas: 9, vendas_pub: 5, vendas_org: 4, acos: 0.20, roi: 2.6 },
      { date: '16/07', visitas: 120, vendas: 10, vendas_pub: 5, vendas_org: 5, acos: 0.19, roi: 2.7 },
      { date: '17/07', visitas: 125, vendas: 10, vendas_pub: 5, vendas_org: 5, acos: 0.18, roi: 2.8 },
      { date: '18/07', visitas: 130, vendas: 11, vendas_pub: 6, vendas_org: 5, acos: 0.17, roi: 2.9 },
      { date: '19/07', visitas: 135, vendas: 11, vendas_pub: 6, vendas_org: 5, acos: 0.16, roi: 3.0 },
      { date: '20/07', visitas: 140, vendas: 12, vendas_pub: 6, vendas_org: 6, acos: 0.15, roi: 3.1 },
      { date: '21/07', visitas: 145, vendas: 12, vendas_pub: 6, vendas_org: 6, acos: 0.14, roi: 3.2 },
      { date: '22/07', visitas: 150, vendas: 13, vendas_pub: 7, vendas_org: 6, acos: 0.13, roi: 3.3 },
      { date: '23/07', visitas: 155, vendas: 13, vendas_pub: 7, vendas_org: 6, acos: 0.12, roi: 3.4 },
      { date: '24/07', visitas: 160, vendas: 14, vendas_pub: 7, vendas_org: 7, acos: 0.11, roi: 3.5 },
      { date: '25/07', visitas: 165, vendas: 14, vendas_pub: 7, vendas_org: 7, acos: 0.10, roi: 3.6 },
      { date: '26/07', visitas: 170, vendas: 15, vendas_pub: 8, vendas_org: 7, acos: 0.09, roi: 3.7 },
      { date: '27/07', visitas: 175, vendas: 15, vendas_pub: 8, vendas_org: 7, acos: 0.08, roi: 3.8 },
      { date: '28/07', visitas: 180, vendas: 16, vendas_pub: 8, vendas_org: 8, acos: 0.07, roi: 3.9 },
    ],
  };
  const filtros = [7, 15, 30, 60];
  const [intervalo, setIntervalo] = useState(7);
  const metricas = mockMetricas[intervalo] || [];

  // Mock de produtos para os boxes
  const produtos = [
    { id: 'MLB1001', nome: 'Produto A', vendas: 120, visitas: 800, roi: 2.5, preco: 199.90, imagem: 'https://picsum.photos/seed/MLB1001/40/40' },
    { id: 'MLB1002', nome: 'Produto B', vendas: 110, visitas: 700, roi: 2.8, preco: 149.90, imagem: 'https://picsum.photos/seed/MLB1002/40/40' },
    { id: 'MLB1003', nome: 'Produto C', vendas: 90, visitas: 600, roi: 3.1, preco: 89.90, imagem: 'https://picsum.photos/seed/MLB1003/40/40' },
    { id: 'MLB1004', nome: 'Produto D', vendas: 80, visitas: 500, roi: 2.2, preco: 249.90, imagem: 'https://picsum.photos/seed/MLB1004/40/40' },
    { id: 'MLB1005', nome: 'Produto E', vendas: 70, visitas: 400, roi: 3.5, preco: 299.90, imagem: 'https://picsum.photos/seed/MLB1005/40/40' },
    { id: 'MLB1006', nome: 'Produto F', vendas: 60, visitas: 300, roi: 2.0, preco: 59.90, imagem: 'https://picsum.photos/seed/MLB1006/40/40' },
    { id: 'MLB1007', nome: 'Produto G', vendas: 50, visitas: 200, roi: 2.9, preco: 99.90, imagem: 'https://picsum.photos/seed/MLB1007/40/40' },
    { id: 'MLB1008', nome: 'Produto H', vendas: 40, visitas: 100, roi: 3.8, preco: 399.90, imagem: 'https://picsum.photos/seed/MLB1008/40/40' },
    { id: 'MLB1009', nome: 'Produto I', vendas: 30, visitas: 90, roi: 1.9, preco: 79.90, imagem: 'https://picsum.photos/seed/MLB1009/40/40' },
    { id: 'MLB1010', nome: 'Produto J', vendas: 20, visitas: 80, roi: 2.7, preco: 129.90, imagem: 'https://picsum.photos/seed/MLB1010/40/40' },
    { id: 'MLB1011', nome: 'Produto K', vendas: 95, visitas: 650, roi: 2.6, preco: 159.90, imagem: 'https://picsum.photos/seed/MLB1011/40/40' },
    { id: 'MLB1012', nome: 'Produto L', vendas: 85, visitas: 550, roi: 2.3, preco: 189.90, imagem: 'https://picsum.photos/seed/MLB1012/40/40' },
    { id: 'MLB1013', nome: 'Produto M', vendas: 75, visitas: 450, roi: 3.0, preco: 219.90, imagem: 'https://picsum.photos/seed/MLB1013/40/40' },
    { id: 'MLB1014', nome: 'Produto N', vendas: 65, visitas: 350, roi: 2.1, preco: 269.90, imagem: 'https://picsum.photos/seed/MLB1014/40/40' },
    { id: 'MLB1015', nome: 'Produto O', vendas: 55, visitas: 250, roi: 2.4, preco: 89.90, imagem: 'https://picsum.photos/seed/MLB1015/40/40' },
    { id: 'MLB1016', nome: 'Produto P', vendas: 45, visitas: 150, roi: 3.2, preco: 349.90, imagem: 'https://picsum.photos/seed/MLB1016/40/40' },
    { id: 'MLB1017', nome: 'Produto Q', vendas: 35, visitas: 120, roi: 2.9, preco: 119.90, imagem: 'https://picsum.photos/seed/MLB1017/40/40' },
    { id: 'MLB1018', nome: 'Produto R', vendas: 25, visitas: 110, roi: 2.8, preco: 139.90, imagem: 'https://picsum.photos/seed/MLB1018/40/40' },
    { id: 'MLB1019', nome: 'Produto S', vendas: 15, visitas: 100, roi: 2.5, preco: 179.90, imagem: 'https://picsum.photos/seed/MLB1019/40/40' },
    { id: 'MLB1020', nome: 'Produto T', vendas: 10, visitas: 90, roi: 2.2, preco: 209.90, imagem: 'https://picsum.photos/seed/MLB1020/40/40' },
  ];
  // Calcula 20% do total
  const topPercent = Math.ceil(produtos.length * 0.2);
  const maisVendidos = [...produtos].sort((a, b) => b.vendas - a.vendas).slice(0, topPercent);
  const maisVisitados = [...produtos].sort((a, b) => b.visitas - a.visitas).slice(0, topPercent);
  const maiorROI = [...produtos].sort((a, b) => b.roi - a.roi).slice(0, topPercent);

  return (
    <Grid container direction="column" alignItems="center" sx={{ maxWidth: 1100, mx: "auto", mt: 4, p: 2, width: '100%' }}>
      <Grid item sx={{ width: '100%', mb: 2 }}>
        <MuiTooltip title="Voltar para o Dashboard">
          <IconButton onClick={() => navigate('/dashboard')} sx={{ bgcolor: '#f5f5f5', mr: 1 }}>
            <ArrowBackIcon sx={{ color: '#1976d2', fontSize: 28 }} />
          </IconButton>
        </MuiTooltip>
      </Grid>
      <Grid item sx={{ width: '100%' }}>
        <Grid container alignItems="center" sx={{ mb: 3 }}>
          <BarChartIcon sx={{ color: '#1976d2', fontSize: 32, mr: 2 }} />
          <Typography variant="h5" sx={{ fontWeight: 700 }}>Métricas Mercado Livre</Typography>
        </Grid>
        <ButtonGroup sx={{ mb: 3 }}>
          {filtros.map(f => (
            <Button key={f} variant={intervalo === f ? 'contained' : 'outlined'} onClick={() => setIntervalo(f)}>{f} dias</Button>
          ))}
        </ButtonGroup>
      </Grid>
      <Grid item sx={{ width: '100%' }}>
        <Card sx={{ mb: 4, width: '100%' }}>
          <CardContent>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Todas as Métricas</Typography>
            <Box sx={{ width: '100%' }}>
              <ResponsiveContainer width="100%" height={400}>
                <LineChart data={metricas} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="visitas" stroke="#1976d2" strokeWidth={2} dot={{ r: 3 }} name="Visitas" />
                  <Line type="monotone" dataKey="vendas" stroke="#388e3c" strokeWidth={2} dot={{ r: 3 }} name="Vendas Totais" />
                  <Line type="monotone" dataKey="vendas_pub" stroke="#ff9800" strokeWidth={2} dot={{ r: 3 }} name="Vendas Publicidade" />
                  <Line type="monotone" dataKey="vendas_org" stroke="#1976d2" strokeDasharray="5 2" strokeWidth={2} dot={{ r: 3 }} name="Vendas Orgânico" />
                  <Line type="monotone" dataKey="acos" stroke="#d32f2f" strokeWidth={2} dot={{ r: 3 }} name="ACOS" />
                  <Line type="monotone" dataKey="roi" stroke="#00a650" strokeWidth={2} dot={{ r: 3 }} name="ROI" />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      {/* Boxes 20% mais vendidos, visitados, maior ROI */}
      <Grid container spacing={2} sx={{ mt: 2, width: '100%' }} alignItems="stretch">
        <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
          <Card sx={{ p: 2, bgcolor: '#f5f5f5', flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BarChartIcon sx={{ color: '#1976d2', fontSize: 28, mr: 1 }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700, fontSize: 18 }}>20% Mais Vendidos</Typography>
            </Box>
            <Grid container spacing={1} sx={{ width: '100%' }}>
              <Grid item xs={7} sx={{ pr: 24 }}>
                {maisVendidos.map((p, i) => (
                  <>
                    <Grid item xs={12} key={i} sx={{ width: '100%' }}>
                      <Grid container spacing={2} alignItems="center" sx={{ width: '100%' }}>
                        <Grid item xs={2} sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 700 }}>ID: {p.id}</Typography>
                          <img src={p.imagem} alt={p.nome} style={{ marginLeft: 8, borderRadius: 4, width: 40, height: 40, objectFit: 'cover', background: '#eee' }} />
                        </Grid>
                        <Grid item xs={4}><Typography variant="body2">{p.nome}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">Vendas: {p.vendas}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">Preço: R$ {p.preco.toFixed(2)}</Typography></Grid>
                      </Grid>
                    </Grid>
                    {i < maisVendidos.length - 1 && <Grid item xs={12}><Divider sx={{ bgcolor: '#e0e0e0' }} /></Grid>}
                  </>
                ))}
              </Grid>
              <Grid item xs={5} sx={{ display: 'flex', alignItems: 'stretch', justifyContent: 'center', height: '100%', pl: 24 }}>
                <BarChart width={180} height={maisVendidos.length * 40} data={maisVendidos} layout="vertical" style={{ flex: 1 }}>
                  <XAxis type="number" hide domain={[0, Math.max(...maisVendidos.map(p => p.vendas))]} />
                  <YAxis type="category" dataKey="nome" width={80} />
                  <Tooltip />
                  <Bar dataKey="vendas" fill="#1976d2">
                    {maisVendidos.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#388e3c' : '#1976d2'} />
                    ))}
                  </Bar>
                </BarChart>
              </Grid>
            </Grid>
          </Card>
        </Grid>
        <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
          <Card sx={{ p: 2, bgcolor: '#f5f5f5', flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BarChartIcon sx={{ color: '#1976d2', fontSize: 28, mr: 1 }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700, fontSize: 18 }}>20% Mais Visitados</Typography>
            </Box>
            <Grid container spacing={1} sx={{ width: '100%' }}>
              <Grid item xs={7} sx={{ pr: 24 }}>
                {maisVisitados.map((p, i) => (
                  <>
                    <Grid item xs={12} key={i} sx={{ width: '100%' }}>
                      <Grid container spacing={2} alignItems="center" sx={{ width: '100%' }}>
                        <Grid item xs={2} sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 700 }}>ID: {p.id}</Typography>
                          <img src={p.imagem} alt={p.nome} style={{ marginLeft: 8, borderRadius: 4, width: 40, height: 40, objectFit: 'cover', background: '#eee' }} />
                        </Grid>
                        <Grid item xs={4}><Typography variant="body2">{p.nome}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">Visitas: {p.visitas}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">Preço: R$ {p.preco.toFixed(2)}</Typography></Grid>
                      </Grid>
                    </Grid>
                    {i < maisVisitados.length - 1 && <Grid item xs={12}><Divider sx={{ bgcolor: '#e0e0e0' }} /></Grid>}
                  </>
                ))}
              </Grid>
              <Grid item xs={5} sx={{ display: 'flex', alignItems: 'stretch', justifyContent: 'center', height: '100%', pl: 24 }}>
                <BarChart width={180} height={maisVisitados.length * 40} data={maisVisitados} layout="vertical" style={{ flex: 1 }}>
                  <XAxis type="number" hide domain={[0, Math.max(...maisVisitados.map(p => p.visitas))]} />
                  <YAxis type="category" dataKey="nome" width={80} />
                  <Tooltip />
                  <Bar dataKey="visitas" fill="#1976d2">
                    {maisVisitados.map((entry, index) => (
                      <Cell key={`cell-visitados-${index}`} fill={index === 0 ? '#388e3c' : '#1976d2'} />
                    ))}
                  </Bar>
                </BarChart>
              </Grid>
            </Grid>
          </Card>
        </Grid>
        <Grid item xs={12} md={4} sx={{ display: 'flex' }}>
          <Card sx={{ p: 2, bgcolor: '#f5f5f5', flex: 1, display: 'flex', flexDirection: 'column', width: '100%' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <BarChartIcon sx={{ color: '#1976d2', fontSize: 28, mr: 1 }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700, fontSize: 18 }}>20% Maior ROI</Typography>
            </Box>
            <Grid container spacing={1} sx={{ width: '100%' }}>
              <Grid item xs={7} sx={{ pr: 24 }}>
                {maiorROI.map((p, i) => (
                  <>
                    <Grid item xs={12} key={i} sx={{ width: '100%' }}>
                      <Grid container spacing={2} alignItems="center" sx={{ width: '100%' }}>
                        <Grid item xs={2} sx={{ display: 'flex', alignItems: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 700 }}>ID: {p.id}</Typography>
                          <img src={p.imagem} alt={p.nome} style={{ marginLeft: 8, borderRadius: 4, width: 40, height: 40, objectFit: 'cover', background: '#eee' }} />
                        </Grid>
                        <Grid item xs={4}><Typography variant="body2">{p.nome}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">ROI: {p.roi}</Typography></Grid>
                        <Grid item xs={3}><Typography variant="body2">Preço: R$ {p.preco.toFixed(2)}</Typography></Grid>
                      </Grid>
                    </Grid>
                    {i < maiorROI.length - 1 && <Grid item xs={12}><Divider sx={{ bgcolor: '#e0e0e0' }} /></Grid>}
                  </>
                ))}
              </Grid>
              <Grid item xs={5} sx={{ display: 'flex', alignItems: 'stretch', justifyContent: 'center', height: '100%', pl: 24 }}>
                <BarChart width={180} height={maiorROI.length * 40} data={maiorROI} layout="vertical" style={{ flex: 1, marginLeft: 32 }}>
                  <XAxis type="number" hide domain={[0, Math.max(...maiorROI.map(p => p.roi))]} />
                  <YAxis type="category" dataKey="nome" width={80} />
                  <Tooltip />
                  <Bar dataKey="roi" fill="#1976d2">
                    {maiorROI.map((entry, index) => (
                      <Cell key={`cell-roi-${index}`} fill={index === 0 ? '#388e3c' : '#1976d2'} />
                    ))}
                  </Bar>
                </BarChart>
              </Grid>
            </Grid>
          </Card>
        </Grid>
      </Grid>
    </Grid>
  );
}
