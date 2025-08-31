


import React, { useState, useEffect } from "react";
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import Box from '@mui/material/Box';
import { motion } from 'framer-motion';
import Typography from '@mui/material/Typography';
// Certifique-se de que está usando apenas o Grid do @mui/material
import Grid from '@mui/material/Grid';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Divider from '@mui/material/Divider';
import Chip from '@mui/material/Chip';
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import MenuItem from '@mui/material/MenuItem';
import Tooltip from '@mui/material/Tooltip';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SearchIcon from '@mui/icons-material/Search';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth';
import PieChartIcon from '@mui/icons-material/PieChart';
import BarChartIcon from '@mui/icons-material/BarChart';
import LineChartIcon from '@mui/icons-material/ShowChart';

// Mock de categorias
const categorias = [
  "Eletrônicos", "Casa", "Moda", "Informática", "Esportes", "Veículos", "Beleza", "Brinquedos", "Livros", "Ferramentas"
];
const statusList = ["Alta", "Estável", "Queda"];

// Mock de produtos
const produtosMock = [
  { nome: "Smartphone Samsung Galaxy S23", categoria: "Eletrônicos", keywords: ["smartphone", "galaxy", "s23", "android"] },
  { nome: "Notebook Dell Inspiron 15", categoria: "Informática", keywords: ["notebook", "dell", "inspiron", "windows"] },
  { nome: "Geladeira Brastemp Frost Free", categoria: "Casa", keywords: ["geladeira", "brastemp", "frost free"] },
  { nome: "Tênis Nike Air Max", categoria: "Moda", keywords: ["tênis", "nike", "air max"] },
  { nome: "Bicicleta Caloi Aro 29", categoria: "Esportes", keywords: ["bicicleta", "caloi", "aro 29"] },
  { nome: "Livro Harry Potter", categoria: "Livros", keywords: ["livro", "harry potter", "fantasia"] },
  { nome: "Furadeira Bosch", categoria: "Ferramentas", keywords: ["furadeira", "bosch", "ferramenta"] },
];

// Mock de palavras-chave populares
const keywordsMock = [
  "smartphone", "notebook", "geladeira", "tênis", "bicicleta", "livro", "furadeira", "android", "windows", "fantasia", "ferramenta"
];

export default function MarketPulse() {
  // Estado de busca/autocomplete
  const [searchTerm, setSearchTerm] = useState("");
  const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>(keywordsMock);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [selectedStatus, setSelectedStatus] = useState("");
  const [volumeFilter, setVolumeFilter] = useState("");
  const [competitionFilter, setCompetitionFilter] = useState("");
  // Estado do modal de categoria
  const [openCategoryModal, setOpenCategoryModal] = useState(false);
  const [mlCategories, setMlCategories] = useState<any[]>([]);
  const [mlSubcategories, setMlSubcategories] = useState<any[]>([]);
  const [selectedMainCategory, setSelectedMainCategory] = useState("");
  // Estado de cards e cache
  const [keywordCards, setKeywordCards] = useState<any[]>([]); // [{ keyword, status, confidence, volume, competition, history, seasonality }]
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  // Estado de alertas/recomendações
  const [alerts, setAlerts] = useState<any[]>([]);
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [openAlerts, setOpenAlerts] = useState<boolean[]>([]);
  const [openRecommendations, setOpenRecommendations] = useState<boolean[]>([]);
  // Estado de gráficos agregados
  const [heatmapData, setHeatmapData] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [pieData, setPieData] = useState<any[]>([]);
  // Estado de concorrentes
  const [competitors, setCompetitors] = useState<any[]>([]);
  // Estado de modal
  const [openModal, setOpenModal] = useState(false);
  const [modalData, setModalData] = useState<any>(null);
  // Estado do tooltip do gráfico de barras
  const [barTooltip, setBarTooltip] = useState<{ x: number, y: number, value: number, keyword: string } | null>(null);

  // Atualização automática/manual
  const [loading, setLoading] = useState(false);
  const [autoUpdate, setAutoUpdate] = useState(true);
  const updateInterval = 300000; // 5 minutos

  // Mock: Funções de busca de dados (substitua por chamadas reais)
  function getRandomStatus() {
    const arr = ['Alta', 'Estável', 'Queda'];
    return arr[Math.floor(Math.random() * arr.length)];
  }
  function getRandomConfidence() {
    return Math.round((0.6 + Math.random() * 0.4) * 100) / 100;
  }
  function getRandomVolume() {
    return Math.floor(1000 + Math.random() * 20000);
  }
  function getRandomCompetition() {
    return Math.floor(10 + Math.random() * 100);
  }
function getRandomHistory(base: number): number[] {
  // Gera uma série histórica com valores entre 100 e 600, com variação suave
  const history = [Math.floor(200 + Math.random() * 200)];
  for (let i = 1; i < 6; i++) {
    // Variação de até ±40 do valor anterior
    const variation = (Math.random() - 0.5) * 80;
    history.push(Math.max(100, Math.min(600, Math.round(history[i - 1] + variation))));
  }
  return history;
}
  function getRandomSeasonality() {
    const arr = ['Alta', 'Média', 'Baixa'];
    return arr[Math.floor(Math.random() * arr.length)];
  }

  async function fetchMarketPulseData() {
    // Gerar cards para cada produto e keyword
    const allKeywords = Array.from(new Set([
      ...produtosMock.flatMap(p => p.keywords),
      ...keywordsMock
    ]));
    const keywordCards = allKeywords.map((kw, idx) => {
      const volume = getRandomVolume();
      return {
        keyword: kw,
        status: getRandomStatus(),
        confidence: getRandomConfidence(),
        volume,
        competition: getRandomCompetition(),
        history: getRandomHistory(volume),
        seasonality: getRandomSeasonality(),
      };
    });

    // Mock de alertas/recomendações
    const alerts = keywordCards.length > 0 ? [
      { text: `Concorrência alta para ${keywordCards[0].keyword}!` },
      { text: `Volume em queda para ${keywordCards[1].keyword}!` },
    ] : [];
    const recommendations = keywordCards.length > 1 ? [
      { action: 'Ajustar preço', text: `Reduza o preço do produto relacionado à ${keywordCards[1].keyword} para aumentar competitividade.` },
      { action: 'Melhorar anúncio', text: `Otimize o anúncio de ${keywordCards[2].keyword} para aumentar buscas.` },
    ] : [];

    // Mock de heatmap, trend, pie, competitors
    const heatmapData = keywordCards.slice(0, 10).map(card => ({ keyword: card.keyword, status: card.status }));
    const trendData = keywordCards.slice(0, 10).map(card => ({ keyword: card.keyword, history: card.history }));
    const pieData = [
      { status: 'Alta', value: keywordCards.filter(c => c.status === 'Alta').length },
      { status: 'Estável', value: keywordCards.filter(c => c.status === 'Estável').length },
      { status: 'Queda', value: keywordCards.filter(c => c.status === 'Queda').length },
    ];
    const competitors = keywordCards.slice(0, 10).map((card, idx) => ({
      user: `user${idx + 1}`,
      ads: getRandomCompetition(),
      keyword: card.keyword,
      link: `https://mercadolivre.com/anuncio${idx + 1}`,
    }));

    return {
      keywordCards,
      alerts,
      recommendations,
      heatmapData,
      trendData,
      pieData,
      competitors,
    };
  }

  // Atualização dos dados
  async function updateData() {
    setLoading(true);
    const data = await fetchMarketPulseData();
    setKeywordCards(data.keywordCards);
    setAlerts(data.alerts);
    setRecommendations(data.recommendations);
    setOpenAlerts(data.alerts.map(() => true));
    setOpenRecommendations(data.recommendations.map(() => true));
    setHeatmapData(data.heatmapData);
    setTrendData(data.trendData);
    setPieData(data.pieData);
    setCompetitors(data.competitors);
    setLastUpdate(new Date());
    setLoading(false);
  }

  // Atualização automática
  useEffect(() => {
    updateData();
    let timer: NodeJS.Timeout;
    if (autoUpdate) {
      timer = setInterval(updateData, updateInterval);
    }
    return () => { if (timer) clearInterval(timer); };
  }, [autoUpdate]);

  return (
    <Box sx={{ width: '100vw', minHeight: '100vh', bgcolor: '#f5f7fa', p: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      {/* Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', bgcolor: '#fff', px: 4, py: 2, boxShadow: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 4, width: '100%' }}>
          <TrendingUpIcon sx={{ fontSize: 40, color: '#1976d2', mr: 2 }} />
          <Typography variant="h4" sx={{ fontWeight: 700, color: '#1976d2', flex: 1, textAlign: 'center' }}>MARKET PULSE</Typography>
          <Box sx={{ flex: 2, display: 'flex', alignItems: 'center', gap: 2, minWidth: 340 }}>
            <TextField
              label="Buscar produto/keyword"
              value={searchTerm}
              onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                setSearchTerm(e.target.value);
                const termo = e.target.value.toLowerCase();
                if (termo.length > 0) {
                  setAutocompleteOptions(keywordsMock.filter(k => k.includes(termo)));
                } else {
                  setAutocompleteOptions(keywordsMock);
                }
              }}
              fullWidth
              InputProps={{ endAdornment: <SearchIcon /> }}
              sx={{ minWidth: 320, bgcolor: '#f0f7ff', borderRadius: 2 }}
              select
            >
              {autocompleteOptions.map((option: string) => (
                <MenuItem key={option} value={option}>{option}</MenuItem>
              ))}
            </TextField>
            <Button variant="contained" color="primary" sx={{ fontWeight: 600, px: 3, borderRadius: 2 }}>Buscar</Button>
          </Box>
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2, justifyContent: 'flex-end', minWidth: 260 }}>
            <Button variant="outlined" color="primary" sx={{ minWidth: 120 }} onClick={() => setOpenCategoryModal(true)}>
              {selectedCategory ? `Categoria: ${selectedCategory}` : 'Selecionar Categoria'}
            </Button>
            <TextField select label="Status" value={selectedStatus} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedStatus(e.target.value)} sx={{ minWidth: 120 }}>
              {statusList.map(s => <MenuItem key={s} value={s}>{s}</MenuItem>)}
            </TextField>
          </Box>
        </Box>
      </Box>
      <Divider sx={{ my: 2 }} />
      {/* Painel Principal: Cards dinâmicos */}
      <Box sx={{ px: 4, py: 2 }}>
        {loading ? (
          <Typography variant="body1">Carregando dados...</Typography>
        ) : keywordCards.length === 0 ? (
          <Typography variant="body1">Nenhuma keyword encontrada.</Typography>
        ) : (
          <React.Fragment>
            <Grid container spacing={4} justifyContent="center" sx={{ maxWidth: 1400, margin: '0 auto' }}>
              {keywordCards.map((card: any, idx: number) => (
                <Grid item xs={12} sm={6} md={4} key={card.keyword + '-' + idx}>
                  <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    whileHover={{ scale: 1.12, boxShadow: "0 12px 40px rgba(25, 118, 210, 0.22)" }}
                    transition={{ duration: 0.35, type: "spring", stiffness: 140 }}
                    style={{ minWidth: 260, maxWidth: 400, width: '100%' }}
                  >
                    <Box sx={{ bgcolor: '#fff', borderRadius: 3, boxShadow: 2, p: 2, minHeight: 200, display: 'flex', flexDirection: 'column', gap: 1, justifyContent: 'space-between', mb: '20px' }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="subtitle1" sx={{ fontWeight: 700, fontSize: 15 }}>{card.keyword}</Typography>
                        <Chip label={card.status} color={card.status === 'Alta' ? 'success' : card.status === 'Queda' ? 'error' : 'warning'} sx={{ fontWeight: 600, height: 20, fontSize: 12 }} />
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <BarChartIcon sx={{ color: '#1976d2', fontSize: 15 }} />
                        <Typography variant="body2" sx={{ fontSize: 12 }}>Volume: {card.volume}</Typography>
                        <Tooltip title="Volume de buscas nos últimos 30 dias"><WarningAmberIcon sx={{ color: '#888', fontSize: 13 }} /></Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <PieChartIcon sx={{ color: '#1976d2', fontSize: 15 }} />
                        <Typography variant="body2" sx={{ fontSize: 12 }}>Concorrência: {card.competition}</Typography>
                        <Tooltip title="Concorrência entre anúncios"><WarningAmberIcon sx={{ color: '#888', fontSize: 13 }} /></Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <LineChartIcon sx={{ color: '#1976d2', fontSize: 15 }} />
                        <Typography variant="caption" sx={{ fontSize: 11 }}>Histórico de Preços</Typography>
                        <Box sx={{ height: 32, width: 160, display: 'flex', alignItems: 'center', justifyContent: 'center', mx: 'auto' }}>
                          <svg width="160" height="32">
                            <polyline
                              fill="none"
                              stroke="#1976d2"
                              strokeWidth="2"
                              points={(() => {
                                const max = Math.max(...card.history);
                                if (!isFinite(max) || max === 0) return '';
                                return card.history.map((v: number, i: number) => `${i * 32},${32 - (v / max * 32)}`).join(' ');
                              })()}
                            />
                          </svg>
                        </Box>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                        <CalendarMonthIcon sx={{ color: '#1976d2', fontSize: 15 }} />
                        <Typography variant="caption" sx={{ fontSize: 11 }}>Sazonalidade: {card.seasonality}</Typography>
                        <Tooltip title="Sazonalidade prevista pela IA"><CalendarMonthIcon sx={{ color: '#888', fontSize: 13 }} /></Tooltip>
                      </Box>
                      <Box sx={{ display: 'flex', gap: 0.5, mt: 1, justifyContent: 'flex-end' }}>
                        <Button variant="outlined" color="primary" size="small" sx={{ minWidth: 0, px: 0.5, fontSize: 11, height: 24 }}>Atualizar ML</Button>
                        <Button variant="outlined" color="secondary" size="small" sx={{ minWidth: 0, px: 0.5, fontSize: 11, height: 24 }}>Explorar</Button>
                        <Button variant="contained" color="success" size="small" sx={{ minWidth: 0, px: 0.5, fontSize: 11, height: 24 }}>Simular</Button>
                      </Box>
                    </Box>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
            {/* Gráfico de barras animado - evolução das palavras-chave */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', mt: 6, mb: 4 }}>
              <Typography variant="h6" sx={{ fontWeight: 700, mb: 2 }}>Evolução das Palavras-chave</Typography>
              {trendData.length > 0 && (
                <Box sx={{ bgcolor: '#f5f5f5', borderRadius: 3, p: 3, boxShadow: 2, minWidth: 420, maxWidth: 820, width: '100%', display: 'flex', justifyContent: 'center' }}>
                  <svg width={Math.max(420, trendData.length * 70)} height={260} style={{ display: 'block' }}>
                    {/* Eixo Y */}
                    <line x1={40} y1={20} x2={40} y2={220} stroke="#1976d2" strokeWidth="2" />
                    {/* Eixo X */}
                    <line x1={40} y1={220} x2={Math.max(420, trendData.length * 70) - 20} y2={220} stroke="#1976d2" strokeWidth="2" />
                    {/* Barras animadas */}
                    {trendData.map((trend, idx) => {
                      const value = trend.history[trend.history.length - 1];
                      const maxY = Math.max(...trendData.map(t => t.history[t.history.length - 1]));
                      const barHeight = ((value / (maxY || 1)) * 180);
                      const x = 60 + idx * 60;
                      // Corrige para que a barra fique encostada no eixo X
                      // Paleta de cores para barras
                      const barColors = [
                        '#1976d2', '#388e3c', '#fbc02d', '#d32f2f', '#7b1fa2', '#0288d1', '#c2185b', '#ffa000', '#009688', '#5d4037'
                      ];
                      const barColor = barColors[idx % barColors.length];
                      return (
                        <motion.rect
                          key={trend.keyword}
                          x={x}
                          y={220 - barHeight}
                          width={40}
                          height={barHeight}
                          initial={{ height: 0 }}
                          animate={{ height: barHeight }}
                          transition={{ duration: 0.7, delay: idx * 0.1, type: 'spring', stiffness: 120 }}
                          fill={barColor}
                          rx={6}
                        />
                      );
                    })}
                    {/* Labels das palavras-chave */}
                    {trendData.map((trend, idx) => {
                      const x = 60 + idx * 60 + 20;
                      return (
                        <text key={trend.keyword + '-label'} x={x} y={240} fontSize="14" textAnchor="middle" fill="#333">{trend.keyword}</text>
                      );
                    })}
                    {/* Valores no topo das barras */}
                    {trendData.map((trend, idx) => {
                      const value = trend.history[trend.history.length - 1];
                      const maxY = Math.max(...trendData.map(t => t.history[t.history.length - 1]));
                      const barHeight = ((value / (maxY || 1)) * 180);
                      const x = 60 + idx * 60 + 20;
                      return (
                        <text key={trend.keyword + '-value'} x={x} y={220 - barHeight - 8} fontSize="13" textAnchor="middle" fill="#1976d2">{value}</text>
                      );
                    })}
                  </svg>
                </Box>
              )}
            </Box>
          </React.Fragment>
        )}
      </Box>
      {/* Rodapé: Gráficos agregados e concorrentes */}
      <Box sx={{ px: 4, py: 4, mt: 4, bgcolor: '#fff', borderRadius: 4, boxShadow: 2 }}>
        <Grid container spacing={3} justifyContent="center">
          <Grid item md={8} sm={12} xs={12} sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            {/* ...gráfico removido... */}
          </Grid>
        </Grid>
        <Divider sx={{ my: 4 }} />
        <Typography variant="subtitle1" sx={{ fontWeight: 700, mb: 2 }}>Concorrentes</Typography>
        <Box sx={{ bgcolor: '#f5f5f5', borderRadius: 2, p: 2 }}>
          <Grid container spacing={2}>
            <Grid item md={3} sm={6} xs={12} sx={{ fontWeight: 600 }}>Usuário</Grid>
            <Grid item md={3} sm={6} xs={12} sx={{ fontWeight: 600 }}>Qtd. Anúncios</Grid>
            <Grid item md={3} sm={6} xs={12} sx={{ fontWeight: 600 }}>Keyword</Grid>
            <Grid item md={3} sm={6} xs={12} sx={{ fontWeight: 600 }}>Link</Grid>
            {/* Dados concorrentes */}
            {competitors.map((comp: any, idx: number) => (
              <React.Fragment key={comp.user + '-' + comp.keyword + '-' + idx}>
                <Grid item md={3} sm={6} xs={12}>{comp.user}</Grid>
                <Grid item md={3} sm={6} xs={12}>{comp.ads}</Grid>
                <Grid item md={3} sm={6} xs={12}>{comp.keyword}</Grid>
                <Grid item md={3} sm={6} xs={12}><Button variant="outlined" color="primary" size="small" href={comp.link} target="_blank">Ver</Button></Grid>
              </React.Fragment>
            ))}
          </Grid>
        </Box>
        {/* Controle de atualização e tempo */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mt: 2 }}>
          <Button variant="contained" color="primary" onClick={updateData} disabled={loading}>Atualizar dados</Button>
          <Typography variant="caption">Última atualização: {lastUpdate ? lastUpdate.toLocaleTimeString() : '---'}</Typography>
          <Button variant="outlined" color={autoUpdate ? 'success' : 'secondary'} onClick={() => setAutoUpdate(!autoUpdate)}>{autoUpdate ? 'Auto atualização ON' : 'Auto atualização OFF'}</Button>
        </Box>
      </Box>
      {/* Modal/Popup para ações */}
      {/* Modal de seleção de categoria Mercado Livre */}
      <Dialog open={openCategoryModal} onClose={() => setOpenCategoryModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Selecione uma Categoria</DialogTitle>
        <DialogContent>
          {/* Lista de categorias principais (mock inicial, depois API) */}
          <Typography variant="subtitle2" sx={{ mb: 1 }}>Categorias principais:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
            {mlCategories.length === 0 ? (
              <Typography variant="body2">Carregando categorias...</Typography>
            ) : (
              mlCategories.map((cat: any) => (
                <Chip
                  key={cat.id}
                  label={cat.name}
                  color={selectedMainCategory === cat.id ? 'primary' : 'default'}
                  onClick={() => setSelectedMainCategory(cat.id)}
                  sx={{ cursor: 'pointer' }}
                />
              ))
            )}
          </Box>
          {/* Lista de subcategorias se houver */}
          {mlSubcategories.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mb: 1 }}>Subcategorias:</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {mlSubcategories.map((sub: any) => (
                  <Chip
                    key={sub.id}
                    label={sub.name}
                    color={selectedCategory === sub.name ? 'primary' : 'default'}
                    onClick={() => setSelectedCategory(sub.name)}
                    sx={{ cursor: 'pointer' }}
                  />
                ))}
              </Box>
            </>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCategoryModal(false)} color="secondary">Fechar</Button>
          <Button onClick={() => setOpenCategoryModal(false)} color="primary" disabled={!selectedCategory}>Selecionar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
