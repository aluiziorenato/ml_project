
import React from "react";
import { Grid, Card, Typography, Box, Button, Divider } from "@mui/material";
import { Link } from "react-router-dom";

const kpis = [
  { label: "Vendas", value: 1200 },
  { label: "ROI", value: "2.5" },
  { label: "Produtos Ativos", value: 35 },
  { label: "Alertas", value: 3 },
];

const funcionalidades = [
  { nome: "Produtos", rota: "/produtos", descricao: "Gestão e análise de produtos" },
  { nome: "Campanhas", rota: "/campanhas", descricao: "Monitoramento de campanhas" },
  { nome: "Concorrentes", rota: "/concorrentes", descricao: "Inteligência de concorrentes" },
  { nome: "Chatbot", rota: "/chatbot", descricao: "Assistente virtual" },
  { nome: "Otimização", rota: "/otimizacao", descricao: "Otimização dinâmica" },
  { nome: "Tendências", rota: "/tendencias", descricao: "Tendências de mercado" },
  { nome: "ROI", rota: "/roi", descricao: "Simulador de ROI" },
  { nome: "Intenção Semântica", rota: "/intencao-semantica", descricao: "Análise semântica" },
  { nome: "Detector de Tendências", rota: "/detector-tendencias", descricao: "Alertas de tendências" },
  { nome: "SEO Visual", rota: "/seo-visual", descricao: "Checklist de SEO" },
];

// Mock de gráfico e lista para simular o modelo visual
function GraficoMock() {
  return (
    <Card sx={{ p: 2, height: "100%" }}>
      <Typography variant="h6">Gráfico de Vendas</Typography>
      <Box sx={{ height: 180, bgcolor: "grey.100", borderRadius: 2, mt: 2, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Typography variant="body2" color="text.secondary">[Gráfico mockado]</Typography>
      </Box>
    </Card>
  );
}

function ListaMock() {
  return (
    <Card sx={{ p: 2, height: "100%" }}>
      <Typography variant="h6">Alertas Recentes</Typography>
      <Box sx={{ mt: 2 }}>
        <Typography>- Produto X com estoque baixo</Typography>
        <Typography>- Campanha Y finalizando hoje</Typography>
        <Typography>- Nova tendência detectada</Typography>
      </Box>
    </Card>
  );
}

export default function DashboardLayout() {
  return (
    <Box sx={{ p: 2 }}>
      {/* KPIs principais em linha, harmônicos */}
      <Grid container columns={12} spacing={2} sx={{ mb: 2 }}>
        <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, textAlign: 'center', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.04)', boxShadow: 6 } }}>
            <Typography variant="subtitle2" color="text.secondary">Vendas</Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>1200</Typography>
          </Card>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, textAlign: 'center', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.04)', boxShadow: 6 } }}>
            <Typography variant="subtitle2" color="text.secondary">ROI</Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>2.5</Typography>
          </Card>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, textAlign: 'center', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.04)', boxShadow: 6 } }}>
            <Typography variant="subtitle2" color="text.secondary">Produtos Ativos</Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>35</Typography>
          </Card>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 3' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, textAlign: 'center', transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.04)', boxShadow: 6 } }}>
            <Typography variant="subtitle2" color="text.secondary">Alertas</Typography>
            <Typography variant="h4" sx={{ fontWeight: 700 }}>3</Typography>
          </Card>
        </Grid>
      </Grid>
      <Grid container columns={12} spacing={2} sx={{ mb: 2 }}>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 8' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, minHeight: 260, transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.01)', boxShadow: 5 } }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>Gráfico de Vendas</Typography>
            <Box sx={{ height: 220, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: '#f5f7fa', borderRadius: 2 }}>
              <Typography variant="body2" color="text.secondary">[Gráfico mockado]</Typography>
            </Box>
          </Card>
        </Grid>
        <Grid gridColumn={{ xs: 'span 12', md: 'span 4' }}>
          <Card sx={{ p: 2, boxShadow: 3, border: 'none', borderRadius: 3, minHeight: 260, transition: 'transform 0.2s, box-shadow 0.2s', '&:hover': { transform: 'scale(1.01)', boxShadow: 5 } }}>
            <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>Alertas Recentes</Typography>
            <Box>
              <Typography variant="body2" sx={{ mb: 1 }}>• Produto X com estoque baixo</Typography>
              <Typography variant="body2" sx={{ mb: 1 }}>• Campanha Y finalizando hoje</Typography>
              <Typography variant="body2">• Nova tendência detectada</Typography>
            </Box>
          </Card>
        </Grid>
      </Grid>
      <Divider sx={{ my: 2 }} />
      {/* Cards de funcionalidades abaixo */}
      <Grid container columns={12} spacing={2}>
        {funcionalidades.map((func) => (
          <Grid key={func.nome} gridColumn={{ xs: 'span 12', sm: 'span 6', md: 'span 4' }}>
            <Card
              sx={{
                p: 2,
                height: "100%",
                cursor: "pointer",
                boxShadow: 3,
                border: "none",
                transition: "transform 0.2s, box-shadow 0.2s",
                '&:hover': {
                  transform: 'translateY(-4px) scale(1.03)',
                  boxShadow: 6,
                  background: 'linear-gradient(90deg, #f5f7fa 0%, #c3cfe2 100%)',
                },
                background: 'white',
                borderRadius: 3,
              }}
              onClick={() => window.location.href = func.rota}
            >
              <Typography variant="h6" sx={{ fontWeight: 600 }}>{func.nome}</Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>{func.descricao}</Typography>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
