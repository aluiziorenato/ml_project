import React, { useState, useEffect } from "react";
import {
  fetchMLUserItems,
  fetchMLItemDetails,
  fetchMLItemPriceHistory,
  fetchMLSearch,
  fetchMLCategory,
  fetchPriceForecastARIMA
} from '../api/competitorIntelligenceApi';
import {
  Box, Typography, Grid, TextField, Button, Divider, Chip, Tooltip, Dialog, DialogTitle, DialogContent, DialogActions,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, IconButton, Snackbar, Alert, MenuItem, Switch, Skeleton
} from "@mui/material";
import { motion } from "framer-motion";
import SearchIcon from "@mui/icons-material/Search";
import TrendingUpIcon from "@mui/icons-material/TrendingUp";
import InfoIcon from "@mui/icons-material/Info";
import DownloadIcon from "@mui/icons-material/Download";
import TimelineIcon from "@mui/icons-material/Timeline";
import SettingsIcon from "@mui/icons-material/Settings";
import BarChartIcon from "@mui/icons-material/BarChart";
import ShowChartIcon from "@mui/icons-material/ShowChart";
import CalendarMonthIcon from "@mui/icons-material/CalendarMonth";
import PieChartIcon from "@mui/icons-material/PieChart";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import DarkModeIcon from "@mui/icons-material/DarkMode";

// Mock de dados e funções (substitua por integração real)
const concorrentesMock = [
  { id: "user1", nome: "Loja Alpha", preco: 1999, variacao: 2.5, ranking: 1, link: "https://ml.com/anuncio1", categoria: "Eletrônicos", status: "Ativo" },
  { id: "user2", nome: "TechStore", preco: 2050, variacao: -1.2, ranking: 2, link: "https://ml.com/anuncio2", categoria: "Eletrônicos", status: "Ativo" },
  { id: "user3", nome: "MegaShop", preco: 1980, variacao: 0.8, ranking: 3, link: "https://ml.com/anuncio3", categoria: "Eletrônicos", status: "Ativo" },
];
const historicoMock = [
  { data: "2025-08-01", preco: 2000 },
  { data: "2025-08-08", preco: 1995 },
  { data: "2025-08-15", preco: 1980 },
  { data: "2025-08-22", preco: 1999 },
  { data: "2025-08-29", preco: 2005 },
];
const previsaoMock = {
  modelo: "ARIMA(1,1,1)",
  hiperparametros: { p: 1, d: 1, q: 1, sazonalidade: "Mensal" },
  aic: 123.4,
  bic: 130.2,
  timestamp: "2025-08-30T10:00:00",
  previsoes: [2005, 2010, 2020],
  intervaloConfianca: [[1990, 2020], [1995, 2025], [2000, 2040]],
};
const timelineMock = [
  { tipo: "previsao", texto: "Previsão ARIMA realizada", data: "2025-08-30" },
  { tipo: "acao", texto: "Ajuste de preço executado", data: "2025-08-29" },
  { tipo: "resultado", texto: "Variação positiva detectada", data: "2025-08-28" },
];
const categoriasMock = ["Eletrônicos", "Casa", "Moda", "Informática", "Esportes"];

export default function CompetitorIntelligence() {
  // Estados principais
  const [searchTerm, setSearchTerm] = useState("");
  const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedCompetitor, setSelectedCompetitor] = useState<any>(null);
  const [period, setPeriod] = useState(30);
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [openSimModal, setOpenSimModal] = useState(false);
  const [simResult, setSimResult] = useState<any>(null);
  const [openSnackbar, setOpenSnackbar] = useState(false);
  const [concorrentes, setConcorrentes] = useState<any[]>([]);
  const [historico, setHistorico] = useState<any[]>([]);
  const [previsao, setPrevisao] = useState<any>(null);
  const [timeline, setTimeline] = useState<any[]>([]);
  const [categorias, setCategorias] = useState<string[]>([]);

  // Buscar concorrentes e autocomplete
  useEffect(() => {
    async function fetchCompetitors() {
      setLoading(true);
      try {
        const res = await fetchMLSearch(searchTerm || "smartphone");
        setConcorrentes(res.results || []);
        setAutocompleteOptions(res.results ? res.results.map((r: any) => r.title) : []);
      } catch (e) {}
      setLoading(false);
    }
    fetchCompetitors();
  }, [searchTerm]);

  // Buscar histórico de preço do concorrente selecionado
  useEffect(() => {
    async function fetchHistory() {
      if (selectedCompetitor && selectedCompetitor.id) {
        setLoading(true);
        try {
          const details = await fetchMLItemDetails(selectedCompetitor.id);
          const priceHistory = await fetchMLItemPriceHistory(selectedCompetitor.id);
          setHistorico(priceHistory || []);
        } catch (e) {}
        setLoading(false);
      }
    }
    fetchHistory();
  }, [selectedCompetitor]);

  // Função de previsão de preço IA
  async function handleForecast() {
    setLoading(true);
    try {
      const payload = {
        competitor_name: selectedCompetitor?.title || "",
        price_history: historico.map((h: any) => h.price),
        forecast_days: period,
        frequency: "daily"
      };
      const res = await fetchPriceForecastARIMA(payload);
      setPrevisao(res);
      setTimeline((prev: any[]) => [...prev, { tipo: "previsao", texto: "Previsão ARIMA realizada", data: new Date().toISOString().slice(0, 10) }]);
    } catch (e) {}
    setLoading(false);
  }

  // Função de simulação
  function handleSimulate() {
    setSimResult({ antes: historico[historico.length - 1]?.price || 0, depois: (historico[historico.length - 1]?.price || 0) - 30, recomendacao: "Reduza o preço para aumentar competitividade." });
    setOpenSimModal(true);
    setTimeline((prev: any[]) => [...prev, { tipo: "acao", texto: "Ajuste de preço simulado", data: new Date().toISOString().slice(0, 10) }]);
  }

  // Função de exportação
  function handleExport() {
    setOpenSnackbar(true);
    setTimeline((prev: any[]) => [...prev, { tipo: "resultado", texto: "Relatório exportado", data: new Date().toISOString().slice(0, 10) }]);
  }

  // Layout principal
  return (
    <Box sx={{ bgcolor: darkMode ? "#181a20" : "#f5f7fa", minHeight: "100vh", color: darkMode ? "#fff" : "#222" }}>
      {/* Topo: Busca, filtros, exportação, dark mode */}
      <Box sx={{ display: "flex", alignItems: "center", px: 4, py: 2, bgcolor: darkMode ? "#23272f" : "#fff", boxShadow: 2 }}>
        <TrendingUpIcon sx={{ fontSize: 36, color: "#1976d2", mr: 2 }} />
        <Typography variant="h5" sx={{ fontWeight: 700, flex: 1 }}>Competidor Inteligente</Typography>
        <TextField
          label="Buscar concorrente/produto"
          value={searchTerm}
          onChange={e => setSearchTerm(e.target.value)}
          sx={{ minWidth: 220, bgcolor: darkMode ? "#23272f" : "#f0f7ff", borderRadius: 2, mr: 2 }}
          select
        >
          {autocompleteOptions.map(opt => (
            <MenuItem key={opt} value={opt}>{opt}</MenuItem>
          ))}
        </TextField>
        <TextField select label="Categoria" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} sx={{ minWidth: 140, mr: 2 }}>
          {categoriasMock.map(cat => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
        </TextField>
        <Button variant="outlined" color="primary" startIcon={<DownloadIcon />} sx={{ mr: 2 }} onClick={handleExport}>Exportar Relatório</Button>
        <Tooltip title="Alternar modo escuro">
          <IconButton onClick={() => setDarkMode(!darkMode)}><DarkModeIcon /></IconButton>
        </Tooltip>
      </Box>
      <Divider sx={{ my: 2 }} />

      {/* Painel Principal: Gráfico histórico/previsão, cards concorrentes, gap */}
      <Grid container spacing={3} sx={{ px: 4 }}>
        <Grid item xs={12} md={8}>
          {/* Gráfico histórico de preços + previsão IA */}
          <Box sx={{ bgcolor: darkMode ? "#23272f" : "#fff", borderRadius: 3, p: 3, boxShadow: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <ShowChartIcon sx={{ color: "#1976d2", mr: 1 }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>Histórico de Preços</Typography>
              <Tooltip title="Gráfico mostra evolução dos preços do concorrente selecionado."><InfoIcon sx={{ ml: 1, color: "#888" }} /></Tooltip>
              <Box sx={{ flex: 1 }} />
              <TextField select label="Período" value={period} onChange={e => setPeriod(Number(e.target.value))} sx={{ minWidth: 100 }}>
                {[7, 30, 90].map(p => <MenuItem key={p} value={p}>{p} dias</MenuItem>)}
              </TextField>
              <Button variant="contained" color="success" sx={{ ml: 2 }} onClick={() => {}}>
                Prever Preço IA
              </Button>
            </Box>
            {/* Gráfico de linha (mock) */}
            <Box sx={{ height: 220, position: "relative" }}>
              {/* Substitua por gráfico real (ex: recharts) */}
              <svg width="100%" height="220">
                <polyline
                  fill="none"
                  stroke="#1976d2"
                  strokeWidth="3"
                  points={historicoMock.map((h, i) => `${i * 60},${220 - (h.preco - 1950)}`).join(" ")}
                />
                {/* Previsão IA sobreposta */}
                <polyline
                  fill="none"
                  stroke="#43a047"
                  strokeWidth="2"
                  strokeDasharray="6 4"
                  points={previsaoMock.previsoes.map((p, i) => `${(historicoMock.length + i) * 60},${220 - (p - 1950)}`).join(" ")}
                />
                {/* Faixa de confiança */}
                {previsaoMock.intervaloConfianca.map((ic, i) => (
                  <rect key={i} x={(historicoMock.length + i) * 60 - 10} y={220 - (ic[1] - 1950)} width={20} height={ic[1] - ic[0]} fill="#43a047" opacity={0.18} />
                ))}
              </svg>
              <Tooltip title="Linha azul: histórico real. Linha verde: previsão IA. Faixa: intervalo de confiança.">
                <InfoIcon sx={{ position: "absolute", top: 8, right: 8, color: "#888" }} />
              </Tooltip>
            </Box>
            {/* Tabela de dados brutos */}
            <TableContainer component={Paper} sx={{ mt: 2 }}>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Data</TableCell>
                    <TableCell>Preço</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {historicoMock.map(h => (
                    <TableRow key={h.data}>
                      <TableCell>{h.data}</TableCell>
                      <TableCell>R$ {h.preco}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {/* Hiperparâmetros IA */}
            <Box sx={{ mt: 2, display: "flex", alignItems: "center", gap: 2 }}>
              <SettingsIcon sx={{ color: "#1976d2" }} />
              <Typography variant="body2">Modelo: {previsaoMock.modelo}</Typography>
              <Typography variant="body2">AIC: {previsaoMock.aic}</Typography>
              <Typography variant="body2">BIC: {previsaoMock.bic}</Typography>
              <Typography variant="body2">Sazonalidade: {previsaoMock.hiperparametros.sazonalidade}</Typography>
              <Typography variant="body2">Previsão: {new Date(previsaoMock.timestamp).toLocaleString()}</Typography>
              <Tooltip title="Hiperparâmetros e métricas do modelo preditivo IA."><InfoIcon sx={{ color: "#888" }} /></Tooltip>
            </Box>
          </Box>
        </Grid>
        <Grid item xs={12} md={4}>
          {/* Cards dinâmicos de concorrentes */}
          <Box sx={{ bgcolor: darkMode ? "#23272f" : "#fff", borderRadius: 3, p: 2, boxShadow: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Concorrentes</Typography>
            <Grid container spacing={2}>
            {concorrentesMock.map((c, idx) => (
                <Grid item xs={12} key={c.id}>
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    whileHover={{ scale: 1.06, boxShadow: "0 8px 32px rgba(25,118,210,0.18)" }}
                    transition={{ duration: 0.3, type: "spring", stiffness: 120 }}
                  >
                    <Box sx={{ bgcolor: darkMode ? "#181a20" : "#f5f7fa", borderRadius: 2, p: 1.5, mb: 1, boxShadow: 1 }}>
                      <Box sx={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{c.nome}</Typography>
                        <Chip label={c.status} color={c.status === "Ativo" ? "success" : "warning"} size="small" />
                      </Box>
                      <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 1 }}>
                        <Typography variant="body2">Preço: R$ {c.preco}</Typography>
                        <Typography variant="body2">Variação: {c.variacao}%</Typography>
                        <Typography variant="body2">Ranking: {c.ranking}</Typography>
                        <Tooltip title="Ver anúncio no Mercado Livre"><Button size="small" href={c.link} target="_blank">Ver</Button></Tooltip>
                      </Box>
                    </Box>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
            {/* Gap competitivo */}
            <Box sx={{ mt: 2, bgcolor: darkMode ? "#181a20" : "#f5f7fa", borderRadius: 2, p: 2 }}>
              <Typography variant="body2" sx={{ fontWeight: 600 }}>Gap de Preço</Typography>
              <Typography variant="body2">Seu preço: R$ 1970</Typography>
              <Typography variant="body2">Concorrente mais próximo: R$ 1980</Typography>
              <Alert severity="info" sx={{ mt: 1 }}>Oportunidade: Reduza o preço para superar o concorrente!</Alert>
              <Tooltip title="Gap de preço entre você e os concorrentes. Recomendações automáticas exibidas aqui."><InfoIcon sx={{ color: "#888", mt: 1 }} /></Tooltip>
            </Box>
            {/* Botão de simulação */}
            <Button variant="contained" color="secondary" sx={{ mt: 2, width: "100%" }} onClick={handleSimulate}>Simular Impacto Competitivo</Button>
          </Box>
        </Grid>
      </Grid>
      <Divider sx={{ my: 4 }} />

      {/* Sidebar: Alertas, recomendações, exportação */}
      <Grid container spacing={3} sx={{ px: 4 }}>
        <Grid item xs={12} md={4}>
          <Box sx={{ bgcolor: darkMode ? "#23272f" : "#fff", borderRadius: 3, p: 2, boxShadow: 2 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Alertas & Recomendações</Typography>
            <Alert severity="warning" sx={{ mb: 2 }}>Concorrente "TechStore" baixou o preço em 2%!</Alert>
            <Alert severity="info" sx={{ mb: 2 }}>Sugestão: Ajuste seu preço para manter competitividade.</Alert>
            <Alert severity="success" sx={{ mb: 2 }}>Promoção recente aumentou seu ranking!</Alert>
            <Tooltip title="Alertas e recomendações automáticas baseadas em análise preditiva e simulação IA."><InfoIcon sx={{ color: "#888" }} /></Tooltip>
          </Box>
        </Grid>
        <Grid item xs={12} md={8}>
          {/* Timeline visual de previsões e ações */}
          <Box sx={{ bgcolor: darkMode ? "#23272f" : "#fff", borderRadius: 3, p: 2, boxShadow: 2 }}>
            <Box sx={{ display: "flex", alignItems: "center", mb: 2 }}>
              <TimelineIcon sx={{ color: "#1976d2", mr: 1 }} />
              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>Histórico de Previsões & Ações</Typography>
              <Tooltip title="Timeline mostra previsões feitas, ações tomadas e resultados obtidos."><InfoIcon sx={{ ml: 1, color: "#888" }} /></Tooltip>
            </Box>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              {timelineMock.map((t, idx) => (
                <Box key={idx} sx={{ display: "flex", alignItems: "center", gap: 2 }}>
                  <Chip label={t.tipo} color={t.tipo === "previsao" ? "primary" : t.tipo === "acao" ? "secondary" : "success"} />
                  <Typography variant="body2">{t.texto}</Typography>
                  <Typography variant="caption">{t.data}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        </Grid>
      </Grid>
      <Divider sx={{ my: 4 }} />

      {/* Rodapé: Tabela detalhada de concorrentes, filtros */}
      <Box sx={{ px: 4, py: 4, bgcolor: darkMode ? "#23272f" : "#fff", borderRadius: 4, boxShadow: 2 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Tabela Detalhada de Concorrentes</Typography>
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell>Nome</TableCell>
                <TableCell>Preço</TableCell>
                <TableCell>Variação</TableCell>
                <TableCell>Ranking</TableCell>
                <TableCell>Categoria</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Link</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {concorrentesMock.map(c => (
                <TableRow key={c.id}>
                  <TableCell>{c.nome}</TableCell>
                  <TableCell>R$ {c.preco}</TableCell>
                  <TableCell>{c.variacao}%</TableCell>
                  <TableCell>{c.ranking}</TableCell>
                  <TableCell>{c.categoria}</TableCell>
                  <TableCell>{c.status}</TableCell>
                  <TableCell><Button size="small" href={c.link} target="_blank">Ver</Button></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
        <Box sx={{ display: "flex", gap: 2, mt: 2 }}>
          <TextField select label="Filtrar por categoria" value={selectedCategory} onChange={e => setSelectedCategory(e.target.value)} sx={{ minWidth: 140 }}>
            {categoriasMock.map(cat => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
          </TextField>
          <TextField select label="Filtrar por movimentação" value={""} onChange={() => {}} sx={{ minWidth: 140 }}>
            <MenuItem value="alta">Alta</MenuItem>
            <MenuItem value="baixa">Baixa</MenuItem>
          </TextField>
        </Box>
      </Box>

      {/* Modal de Simulação de Impacto */}
      <Dialog open={openSimModal} onClose={() => setOpenSimModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Simulação de Impacto Competitivo</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ mb: 2 }}>Veja o efeito de um ajuste de preço sobre o gap competitivo e ranking.</Typography>
          <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
            <Typography variant="body2">Antes: R$ {simResult?.antes}</Typography>
            <Typography variant="body2">Depois: R$ {simResult?.depois}</Typography>
            <Alert severity="info">{simResult?.recomendacao}</Alert>
            {/* Gráfico comparativo (mock) */}
            <Box sx={{ height: 120, bgcolor: "#f5f5f5", borderRadius: 2, mt: 2 }}>
              <Typography variant="caption" sx={{ p: 2 }}>Gráfico comparativo antes/depois (substitua por gráfico real)</Typography>
            </Box>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenSimModal(false)} color="secondary">Fechar</Button>
        </DialogActions>
      </Dialog>

      {/* Ajuda contextual */}
      <Box sx={{ position: "fixed", bottom: 24, right: 24 }}>
        <Tooltip title="Ajuda contextual: Clique nos ícones de info para explicações detalhadas. Tutorial disponível no menu principal.">
          <IconButton color="primary"><InfoIcon sx={{ fontSize: 32 }} /></IconButton>
        </Tooltip>
      </Box>

      {/* Snackbar de exportação */}
      <Snackbar open={openSnackbar} autoHideDuration={3000} onClose={() => setOpenSnackbar(false)}>
        <Alert severity="success" sx={{ width: "100%" }}>Relatório exportado com sucesso! (mock)</Alert>
      </Snackbar>
    </Box>
  );
}

// ----------------------
// EXPLICAÇÃO DOS RECURSOS VISUAIS:
// - Cards dinâmicos: mostram status, preço, variação, ranking e link dos concorrentes. Interativos, com animação e tooltips.
// - Gráfico histórico/previsão: linha azul (real), linha verde (previsão IA), faixa sombreada (intervalo de confiança). Tooltips explicam cada métrica.
// - Gap competitivo: painel mostra diferença de preço e recomendações automáticas.
// - Simulação: modal permite testar impacto de ações, com gráfico comparativo e recomendações.
// - Alertas/recomendações: sidebar exibe insights automáticos e sugestões de ação.
// - Timeline: histórico visual de previsões, ações e resultados.
// - Tabela detalhada: lista concorrentes, preços, variações, ranking, categoria, status e link.
// - Filtros: por categoria, movimentação, período.
// - Exportação: botão exporta relatório visual (mock).
// - Dark mode: alternância visual para conforto.
// - Skeletons: podem ser adicionados durante loading.
// - Tooltips: explicações em todos os ícones de info.
// - Ajuda contextual: ícone fixo para tutorial e explicações.
// - Atualização: manual e automática (adicionar timer se necessário).
// - Integração: todos os dados mockados devem ser substituídos por chamadas reais às APIs Mercado Livre e serviço ARIMA/SARIMA.
// - Segurança: adicionar autenticação e logs na integração real.
// ----------------------
