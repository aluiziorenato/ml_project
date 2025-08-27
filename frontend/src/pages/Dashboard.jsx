import React from "react";
import {
  Paper,
  Typography,
  Box,
  Fade,
  Container,
  Divider,
} from "@mui/material";
import Grid from "@mui/material/Grid";
import BarChartIcon from '@mui/icons-material/BarChart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import InventoryIcon from '@mui/icons-material/Inventory';
import PeopleAltIcon from '@mui/icons-material/PeopleAlt';

function AnimatedCard({ icon, title, value, color }) {
  return (
    <Fade in timeout={500}>
      <Paper elevation={4} sx={{
        p: 3,
        borderRadius: 4,
        background: '#fff',
        boxShadow: '0 4px 24px #e5e7eb',
        minHeight: 120,
        display: 'flex',
        alignItems: 'center',
        gap: 2,
        transition: 'transform 0.2s',
        '&:hover': { transform: 'scale(1.03)', boxShadow: '0 8px 32px #e5e7eb' }
      }}>
        <Box sx={{ mr: 2, color, fontSize: 36 }}>
          {icon}
        </Box>
        <Box>
          <Typography variant="subtitle2" sx={{ color: '#5D5D59', fontWeight: 500 }}>{title}</Typography>
          <Typography variant="h5" sx={{ fontWeight: 700, color }}>{value}</Typography>
        </Box>
      </Paper>
    </Fade>
  );
}

export default function Dashboard() {
  const kpis = [
    { title: 'Vendas', value: '1.240', sub: '5,2x' },
    { title: 'ROI', value: '5,2x' },
    { title: 'ACOS', value: '24,5 %' },
    { title: 'ROAS', value: '6,1' },
    { title: 'Reputação', value: '⭐⭐⭐⭐☆' },
    { title: 'Conexões ML', value: 'Ativo' },
  ];

  return (
    <Container maxWidth="xl" sx={{ fontFamily: 'Inter, Segoe UI, Roboto, Arial, sans-serif', background: '#F6F7F9', minHeight: '100vh', py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700, color: '#11110D', letterSpacing: 0.5, textAlign: 'center' }}>Dashboard</Typography>
      {/* KPIs em linha, igual à imagem */}
      <Grid container columns={12} spacing={2} sx={{ mb: 2 }}>
        {kpis.map((kpi, idx) => (
          <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 2' }} key={idx} sx={{ display: 'flex', justifyContent: 'center' }}>
            <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minWidth: 140, minHeight: 90, boxShadow: '0 2px 8px #e5e7eb', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
              <Typography variant="subtitle2" sx={{ color: '#11110D', fontWeight: 500 }}>{kpi.title}</Typography>
              <Typography variant="h5" sx={{ fontWeight: 700 }}>{kpi.value}</Typography>
              {kpi.sub && <Typography variant="body2" sx={{ color: '#5D5D59' }}>{kpi.sub}</Typography>}
            </Paper>
          </Grid>
        ))}
      </Grid>
      {/* Grid 3x3 de cards abaixo dos KPIs */}
      <Grid container columns={12} spacing={2} sx={{ mb: 2 }}>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Atividade Recente</Typography>
            <Typography variant="body2">Desconto aplicado no Produto C <span style={{ fontSize: 11, background: '#eee', borderRadius: 4, padding: '2px 6px', marginLeft: 4 }}>Tend</span></Typography>
            <Typography variant="body2">Otimatica <span style={{ float: 'right', color: '#888' }}>Automatica</span></Typography>
            <Typography variant="body2">Ajustar lance na Campanha X <span style={{ fontSize: 11, background: '#eee', borderRadius: 4, padding: '2px 6px', marginLeft: 4 }}>Medo</span></Typography>
            <Typography variant="body2">Menilao <span style={{ float: 'right', color: '#888' }}>Manual</span></Typography>
            <Typography variant="body2">Agendar desconto para Produto Mala <span style={{ float: 'right', color: '#888' }}>Alto</span></Typography>
          </Paper>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Campanhas</Typography>
            <table style={{ width: '100%', fontSize: 13 }}>
              <thead>
                <tr style={{ color: '#888' }}>
                  <th>Tutam</th><th>Biudxe</th><th>BID</th><th>Audência</th><th>CTR</th>
                </tr>
              </thead>
              <tbody>
                <tr><td>Campanha X</td><td>500,000</td><td>2,00</td><td>Interesses</td><td>○</td></tr>
                <tr><td>Campanha Y</td><td>300,000</td><td>1,50</td><td>CTR</td><td>○</td></tr>
                <tr><td>Campanha Z</td><td>200,000</td><td>1,00</td><td>CTR</td><td>○</td></tr>
              </tbody>
            </table>
          </Paper>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Agendador Visual de Descontos</Typography>
            <table style={{ width: '100%', fontSize: 13, textAlign: 'center' }}>
              <thead>
                <tr><th>Mi</th><th>Ti</th><th>W</th><th>Th</th><th>Fr</th><th>Sa</th></tr>
              </thead>
              <tbody>
                <tr><td></td><td></td><td></td><td></td><td></td><td>Produto Mala</td></tr>
                <tr><td></td><td></td><td>Produto Mochila</td><td></td><td></td><td></td></tr>
              </tbody>
            </table>
          </Paper>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Modo Estratégico</Typography>
            <table style={{ width: '100%', fontSize: 13 }}>
              <thead>
                <tr><th>Raícho</th><th>Descrição</th><th>Status</th></tr>
              </thead>
              <tbody>
                <tr><td>Bola</td><td>Produto C</td><td>Ativo</td></tr>
                <tr><td>Luva</td><td>Adostar Climizár SEO</td><td>Ativo</td></tr>
                <tr><td>Corda</td><td><button style={{ fontSize: 11, padding: '2px 8px', borderRadius: 4, background: '#1976D2', color: '#fff', border: 'none' }}>Otimizar SEO</button></td><td></td></tr>
                <tr><td>Mala</td><td>Produto C</td><td>Ativo</td></tr>
              </tbody>
            </table>
          </Paper>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Campanhas</Typography>
            <table style={{ width: '100%', fontSize: 13 }}>
              <thead>
                <tr><th>Título</th><th>Búdgete</th><th>Stuzo</th><th>ROI</th><th>ROI</th></tr>
              </thead>
              <tbody>
                <tr><td>Campanha X</td><td>500.0</td><td>22.g</td><td>5g</td><td>●</td></tr>
                <tr><td>Campanha Y</td><td>300.0</td><td>1,50</td><td>84</td><td>●</td></tr>
                <tr><td>Campanha Z</td><td>200.0</td><td>1,00</td><td>5</td><td>●</td></tr>
              </tbody>
            </table>
          </Paper>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Paper elevation={2} sx={{ p: 2, borderRadius: 3, minHeight: 180, boxShadow: '0 2px 8px #e5e7eb' }}>
            <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>Analytics e Simulações</Typography>
            <Box sx={{ height: 120, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#B2B2B2', mb: 1 }}>
              <svg width="100%" height="60" viewBox="0 0 180 60"><path d="M0,40 Q45,10 90,30 Q135,50 180,20" stroke="#1976D2" strokeWidth="2" fill="none"/><path d="M0,50 Q45,30 90,50 Q135,60 180,40" stroke="#888" strokeWidth="2" fill="none"/></svg>
            </Box>
            <Typography variant="body2" sx={{ color: '#888' }}>Cenário Otimizado</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}
