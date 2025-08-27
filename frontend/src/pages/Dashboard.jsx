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
  const metrics = [
    { icon: <BarChartIcon />, title: 'Vendas Mensais', value: 'R$ 12.500', color: '#1976D2' },
    { icon: <TrendingUpIcon />, title: 'Tendência Estoque', value: '+8%', color: '#10B981' },
    { icon: <InventoryIcon />, title: 'Produtos Ativos', value: '124', color: '#F59E42' },
    { icon: <PeopleAltIcon />, title: 'Clientes', value: '1.320', color: '#7C3AED' },
  ];
  const produtosCards = [
    {
      title: "Produtos Mais Visitados",
      items: ["Smartphone XYZ", "Fone de Ouvido ABC", "Smartwatch DEF"],
    },
    {
      title: "Produtos Mais Vendidos",
      items: ["Notebook Ultra", "Teclado Gamer", "Monitor 4K"],
    },
  ];

  return (
    <Container maxWidth="xl" sx={{ fontFamily: 'Inter, Segoe UI, Roboto, Arial, sans-serif', background: '#F6F7F9', minHeight: '100vh', py: 4 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700, color: '#11110D', letterSpacing: 0.5, textAlign: 'center' }}>Dashboard</Typography>
      <Grid container spacing={3} justifyContent="center">
        {metrics.map((m, idx) => (
          <Grid gridColumn="span 12" md={6} lg={3} key={idx}>
            <AnimatedCard {...m} />
          </Grid>
        ))}
      </Grid>
      <Divider sx={{ my: 4 }} />
      <Grid container spacing={4}>
        {produtosCards.map(({ title, items }) => (
          <Grid gridColumn="span 12" md={6} key={title}>
            <Fade in timeout={500}>
              <Paper elevation={4} sx={{
                bgcolor: '#fff',
                color: '#11110D',
                p: 3,
                borderRadius: 4,
                boxShadow: '0 4px 24px #e5e7eb',
                transition: 'transform 0.2s',
                '&:hover': { transform: 'scale(1.03)', boxShadow: '0 8px 32px #e5e7eb' }
              }}>
                <Typography variant="h6" sx={{ fontWeight: 600, color: '#1976D2', mb: 2 }}>{title}</Typography>
                {items.map((item, idx) => (
                  <Typography key={idx} variant="body2" sx={{ color: '#5D5D59', mb: 1 }}>{idx + 1}. {item}</Typography>
                ))}
              </Paper>
            </Fade>
          </Grid>
        ))}
      </Grid>
      <Divider sx={{ my: 4 }} />
      {/* Espaço para gráficos e widgets avançados */}
      <Box sx={{ mt: 2 }}>
        <Paper elevation={3} sx={{ p: 3, borderRadius: 4, background: '#fff', boxShadow: '0 2px 8px #e5e7eb', minHeight: 320 }}>
          <Typography variant="h6" sx={{ mb: 2, fontWeight: 600, color: '#1976D2' }}>Gráfico de Vendas (em breve)</Typography>
          <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#B2B2B2' }}>
            <BarChartIcon sx={{ fontSize: 64 }} />
            <Typography sx={{ ml: 2 }}>Gráfico interativo será exibido aqui</Typography>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
