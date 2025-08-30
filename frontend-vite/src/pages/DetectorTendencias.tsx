type Categoria = 'Eletrônicos' | 'Moda' | 'Casa';
type Produto = { id: number; titulo: string; preco: number; vendas: number; imagem: string };
type DataPonto = { ds: string; y: number };
type MockData = Record<Categoria, DataPonto[]>;
type ProdutosMock = Record<Categoria, Produto[]>;
type MockDataProduto = Record<number, DataPonto[]>;
import React, { useState, useEffect, useMemo } from 'react';
import { Card, CardContent, Typography, Select, MenuItem, FormControl, InputLabel, Button, Grid, Box, TextField, Stack } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';

// Dados mocados por categoria (fallback)
const mockData: MockData = {
  Eletrônicos: [
    { ds: '2025-08-01', y: 120 },
    { ds: '2025-08-02', y: 135 },
    { ds: '2025-08-03', y: 150 },
    { ds: '2025-08-04', y: 170 },
    { ds: '2025-08-05', y: 180 },
    { ds: '2025-08-06', y: 200 },
    { ds: '2025-08-07', y: 220 },
    { ds: '2025-08-08', y: 210 },
    { ds: '2025-08-09', y: 230 },
    { ds: '2025-08-10', y: 250 },
  ],
  Moda: [
    { ds: '2025-08-01', y: 80 },
    { ds: '2025-08-02', y: 85 },
    { ds: '2025-08-03', y: 90 },
    { ds: '2025-08-04', y: 95 },
    { ds: '2025-08-05', y: 100 },
    { ds: '2025-08-06', y: 110 },
    { ds: '2025-08-07', y: 120 },
    { ds: '2025-08-08', y: 115 },
    { ds: '2025-08-09', y: 130 },
    { ds: '2025-08-10', y: 140 },
  ],
  Casa: [
    { ds: '2025-08-01', y: 60 },
    { ds: '2025-08-02', y: 65 },
    { ds: '2025-08-03', y: 70 },
    { ds: '2025-08-04', y: 75 },
    { ds: '2025-08-05', y: 80 },
    { ds: '2025-08-06', y: 85 },
    { ds: '2025-08-07', y: 90 },
    { ds: '2025-08-08', y: 95 },
    { ds: '2025-08-09', y: 100 },
    { ds: '2025-08-10', y: 110 },
  ],
};

const categorias: Categoria[] = Object.keys(mockData) as Categoria[];
const periodos: { label: string; value: number | 'custom' }[] = [
  { label: '7 dias', value: 7 },
  { label: '15 dias', value: 15 },
  { label: '30 dias', value: 30 },
  { label: '60 dias', value: 60 },
  { label: 'Personalizado', value: 'custom' },
];
const coresPie: string[] = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28EFF', '#FF6F91', '#FFD700', '#00BFFF', '#FF6347', '#32CD32'
];

function filtrarPorPeriodo(
  data: DataPonto[],
  dias: number | 'custom',
  customStart?: string,
  customEnd?: string
): DataPonto[] {
  if (!Array.isArray(data) || data.length === 0) return [];
  if (dias === 'custom' && customStart && customEnd) {
    return data.filter(
      (item: DataPonto) => item.ds >= customStart && item.ds <= customEnd
    );
  }
  return data.slice(-Number(dias));
}

function calcularTendencia(data: DataPonto[]): 'Alta' | 'Queda' | 'Estável' {
  if (data.length < 2) return 'Estável';
  const diff = data[data.length - 1].y - data[0].y;
  if (diff > 20) return 'Alta';
  if (diff < -20) return 'Queda';
  return 'Estável';
}

export default function DetectorTendencias() {
  // Declarar todos os estados antes de qualquer uso
  const [categoria, setCategoria] = useState<Categoria>(categorias[0]);
  const [periodo, setPeriodo] = useState<string>('7');
  const [customStart, setCustomStart] = useState<string>('');
  const [customEnd, setCustomEnd] = useState<string>('');
  const [produtoId, setProdutoId] = useState<number | null>(null);
  const [termo, setTermo] = useState<string>('');

  // Carregar dados do mock API ao iniciar e ao mudar filtros
  useEffect(() => {
    async function fetchAPI() {
      try {
        const resProdutos = await fetch(`/api/produtos?categoria=${encodeURIComponent(categoria)}`);
        const produtosData = await resProdutos.json();
        if (produtosData && typeof produtosData === 'object') {
          setProdutosMock(produtosData);
        }
      } catch (e) {}
      try {
        let urlTendencias = `/api/tendencias?categoria=${encodeURIComponent(categoria)}`;
        if (produtoId) urlTendencias += `&produtoId=${produtoId}`;
        if (periodo) urlTendencias += `&periodo=${periodo}`;
        if (customStart) urlTendencias += `&customStart=${customStart}`;
        if (customEnd) urlTendencias += `&customEnd=${customEnd}`;
        if (termo) urlTendencias += `&termo=${encodeURIComponent(termo)}`;
        const resTendencias = await fetch(urlTendencias);
        const tendenciasData = await resTendencias.json();
        if (tendenciasData && typeof tendenciasData === 'object') {
          setMockDataState(tendenciasData);
        }
      } catch (e) {}
    }
    fetchAPI();
  }, [categoria, produtoId, periodo, customStart, customEnd, termo]);

  // Produtos mocados por categoria (simuláveis)
  const [produtosMock, setProdutosMock] = useState<ProdutosMock>({
    Eletrônicos: [
      { id: 1, titulo: 'Smartphone X', preco: 2499.99, vendas: 120, imagem: 'https://placehold.co/80x80?text=Smartphone' },
      { id: 2, titulo: 'Notebook Pro', preco: 4999.99, vendas: 80, imagem: 'https://placehold.co/80x80?text=Notebook' },
      { id: 3, titulo: 'Fone Bluetooth', preco: 399.99, vendas: 200, imagem: 'https://placehold.co/80x80?text=Fone' },
    ],
    Moda: [
      { id: 10, titulo: 'Camiseta', preco: 49.99, vendas: 180, imagem: 'https://placehold.co/80x80?text=Camiseta' },
      { id: 11, titulo: 'Calça Jeans', preco: 99.99, vendas: 140, imagem: 'https://placehold.co/80x80?text=Calca' },
      { id: 12, titulo: 'Bermuda', preco: 59.99, vendas: 90, imagem: 'https://placehold.co/80x80?text=Bermuda' },
      { id: 13, titulo: 'Saia', preco: 69.99, vendas: 70, imagem: 'https://placehold.co/80x80?text=Saia' },
      { id: 14, titulo: 'Vestido Verão', preco: 129.99, vendas: 150, imagem: 'https://placehold.co/80x80?text=Vestido' },
      { id: 15, titulo: 'Tênis Casual', preco: 199.99, vendas: 95, imagem: 'https://placehold.co/80x80?text=Tenis' },
      { id: 16, titulo: 'Camisa Polo', preco: 89.99, vendas: 110, imagem: 'https://placehold.co/80x80?text=Camisa' },
    ],
    Casa: [
      { id: 7, titulo: 'Jogo de Toalhas', preco: 59.99, vendas: 60, imagem: 'https://placehold.co/80x80?text=Toalha' },
      { id: 8, titulo: 'Liquidificador', preco: 149.99, vendas: 40, imagem: 'https://placehold.co/80x80?text=Liquidificador' },
      { id: 9, titulo: 'Cafeteira', preco: 229.99, vendas: 75, imagem: 'https://placehold.co/80x80?text=Cafeteira' },
    ],
  });

  // Dados dos gráficos simuláveis
  const [mockDataState, setMockDataState] = useState<MockData>(mockData);
  const [mockDataProdutoState, setMockDataProdutoState] = useState<MockDataProduto>(() => ({
    10: [
      { ds: '2025-08-01', y: 40 },
      { ds: '2025-08-02', y: 45 },
      { ds: '2025-08-03', y: 50 },
      { ds: '2025-08-04', y: 55 },
      { ds: '2025-08-05', y: 60 },
      { ds: '2025-08-06', y: 65 },
      { ds: '2025-08-07', y: 70 },
      { ds: '2025-08-08', y: 75 },
      { ds: '2025-08-09', y: 80 },
      { ds: '2025-08-10', y: 85 },
    ],
    11: [
      { ds: '2025-08-01', y: 30 },
      { ds: '2025-08-02', y: 32 },
      { ds: '2025-08-03', y: 35 },
      { ds: '2025-08-04', y: 38 },
      { ds: '2025-08-05', y: 40 },
      { ds: '2025-08-06', y: 42 },
      { ds: '2025-08-07', y: 45 },
      { ds: '2025-08-08', y: 47 },
      { ds: '2025-08-09', y: 50 },
      { ds: '2025-08-10', y: 52 },
    ],
  }));

  // Função para simular dados novos
  async function simularNovosDados() {
    // Chama endpoint de simulação, atualiza dados
    try {
      const resSimulacao = await fetch(`/api/tendencias?categoria=${encodeURIComponent(categoria)}&produtoId=${produtoId || ''}&periodo=${periodo}&customStart=${customStart}&customEnd=${customEnd}&termo=${encodeURIComponent(termo)}&simular=1`);
      const tendenciasData = await resSimulacao.json();
      if (tendenciasData && typeof tendenciasData === 'object') {
        setMockDataState(tendenciasData);
      }
    } catch (e) {
      // fallback para simulação local
      setMockDataState((old) => {
        const novo: MockData = { Eletrônicos: [], Moda: [], Casa: [] };
        (Object.keys(old) as Categoria[]).forEach(cat => {
          novo[cat] = old[cat].map((item) => ({
            ...item,
            y: Math.floor(Math.random() * 250 + 30),
          }));
        });
        return novo;
      });
    }
    // Simula dados dos gráficos de produto localmente
    setMockDataProdutoState((old) => {
      const novo: MockDataProduto = {};
      Object.keys(old).forEach((prodId) => {
        novo[Number(prodId)] = old[Number(prodId)].map((item) => ({
          ...item,
          y: Math.floor(Math.random() * 100 + 10),
        }));
      });
      return { ...old, ...novo };
    });
  }

  // Fallback seguro para produtos
  const produtos: Produto[] = Array.isArray(produtosMock[categoria]) ? produtosMock[categoria] : [];
  useEffect(() => {
    if (produtos.length > 0) {
      setProdutoId(produtos[0]?.id ?? null);
    } else {
      setProdutoId(null);
    }
  }, [categoria, produtos]);
  const produtoSelecionado: Produto | undefined = produtos.find((p) => p.id === produtoId) || produtos[0];

  const mockDataProduto: MockDataProduto = mockDataProdutoState;
  const data: DataPonto[] = useMemo(() => {
    if (produtoSelecionado && mockDataProduto[produtoSelecionado.id]) return mockDataProduto[produtoSelecionado.id];
    return mockDataState[categoria];
  }, [categoria, produtoSelecionado, mockDataProduto, mockDataState]);

  const dadosFiltrados: DataPonto[] = useMemo(() => {
    let periodoValor: number | 'custom' = periodo === 'custom' ? 'custom' : Number(periodo);
    return filtrarPorPeriodo(data, periodoValor, customStart, customEnd);
  }, [data, periodo, customStart, customEnd]);
  const tendencia: 'Alta' | 'Queda' | 'Estável' = useMemo(() => calcularTendencia(dadosFiltrados), [dadosFiltrados]);

  const tendenciaCor: Record<'Alta' | 'Queda' | 'Estável', string> = {
    Alta: 'green',
    Queda: 'red',
    Estável: 'gray',
  };

  type InsightIA = { titulo: string; descricao: string; icone: string };
  const insightsIA: InsightIA[] = [
    {
      titulo: 'Explicabilidade da Tendência',
      descricao: tendencia === 'Alta'
        ? 'A tendência de alta foi influenciada por aumento de buscas, promoções recentes e sazonalidade positiva.'
        : tendencia === 'Queda'
        ? 'A tendência de queda pode estar relacionada à concorrência, fim de promoção ou sazonalidade negativa.'
        : 'A tendência está estável, sem grandes variações ou eventos impactantes.',
      icone: '🔍',
    },
    {
      titulo: 'Projeção Futura',
      descricao: tendencia === 'Alta'
        ? 'Projeção de crescimento de até 15% nos próximos 7 dias.'
        : tendencia === 'Queda'
        ? 'Projeção de queda de até 10% nos próximos 7 dias.'
        : 'Projeção de estabilidade para o período analisado.',
      icone: '📈',
    },
    {
      titulo: 'Recomendações',
      descricao: tendencia === 'Alta'
        ? 'Sugestão: aumentar estoque, investir em anúncios e aproveitar o momento.'
        : tendencia === 'Queda'
        ? 'Sugestão: revisar preço, criar promoções e analisar concorrentes.'
        : 'Sugestão: manter estratégia atual e monitorar possíveis mudanças.',
      icone: '💡',
    },
    {
      titulo: 'Confiança da Previsão',
      descricao: tendencia === 'Alta'
        ? 'Intervalo de confiança: 80% a 95%.'
        : tendencia === 'Queda'
        ? 'Intervalo de confiança: 70% a 90%.'
        : 'Intervalo de confiança: 60% a 85%.',
      icone: '🔒',
    },
    {
      titulo: 'Sazonalidade Detectada',
      descricao: 'Semana do consumidor, feriado próximo e alta de buscas por presentes.',
      icone: '🎉',
    },
    {
      titulo: 'Alerta de Outlier',
      descricao: 'Venda atípica detectada no dia 05/08. Recomenda-se revisar o estoque e monitorar concorrentes.',
      icone: '⚠️',
    },
    {
      titulo: 'Ação Automatizada',
      descricao: 'Recomenda-se ativar campanha de desconto para aproveitar o aumento de interesse.',
      icone: '🤖',
    },
  ];

  return (
      <Box sx={{ width: '100%', maxWidth: 1100, mx: 'auto', p: 3, bgcolor: '#fafbfc', borderRadius: 3, boxShadow: 2, minHeight: 700, overflow: 'hidden', fontSize: '12px' }}>
      {/* Mensagem amigável se não houver produtos */}
      {produtos.length === 0 && (
        <Box sx={{ p: 2, bgcolor: '#fff3f3', borderRadius: 2, mb: 2, textAlign: 'center', color: '#c00', fontWeight: 500 }}>
          Nenhum produto encontrado para a categoria selecionada.<br />
          Verifique se a API está rodando corretamente ou tente outra categoria.
        </Box>
      )}
      {/* Ícone de voltar para a dashboard no topo */}
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        <Button
          variant="text"
          color="primary"
          startIcon={
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 18L9 12L15 6" stroke="#1976d2" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          }
          sx={{ fontSize: '13px', minHeight: 32, height: 32, textTransform: 'none', fontWeight: 500, pl: 0.5 }}
          onClick={() => window.location.href = '/dashboard'}
        >
          Voltar para Dashboard
        </Button>
        <Typography variant="h5" gutterBottom sx={{ fontSize: '14px', fontWeight: 'bold', ml: 2 }}>
          Detector de Tendências
        </Typography>
      </Box>
      {/* Filtros e gráficos */}
      <Grid container spacing={2} alignItems="center">
        <Grid>
          <FormControl fullWidth sx={{ fontSize: '12px' }}>
            <InputLabel sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>Categoria</InputLabel>
            <Select
              value={categoria}
              label="Categoria"
              onChange={(e) => setCategoria(e.target.value)}
              sx={{ fontSize: '12px', height: 32, minHeight: 32 }}
              MenuProps={{ PaperProps: { sx: { fontSize: '12px' } } }}
              inputProps={{ sx: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
            >
              {categorias.map((cat) => (
                <MenuItem key={cat} value={cat} sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>{cat}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid>
          <FormControl fullWidth sx={{ fontSize: '12px' }}>
            <InputLabel sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>Subcategoria</InputLabel>
            <Select
              value={
                produtos.length > 0 && produtos.some(p => p.id === produtoId)
                  ? produtoId
                  : produtos[0]?.id || ''
              }
              label="Subcategoria"
              onChange={(e) => setProdutoId(Number(e.target.value))}
              sx={{ fontSize: '12px', height: 32, minHeight: 32 }}
              MenuProps={{ PaperProps: { sx: { fontSize: '12px' } } }}
              inputProps={{ sx: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
            >
              {produtos.map((prod) => (
                <MenuItem key={prod.id} value={prod.id} sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>{prod.titulo}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid>
          <FormControl fullWidth sx={{ fontSize: '12px' }}>
            <InputLabel sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>Período</InputLabel>
            <Select
              value={periodo}
              label="Período"
              onChange={(e) => setPeriodo(e.target.value)}
              sx={{ fontSize: '12px', height: 32, minHeight: 32 }}
              MenuProps={{ PaperProps: { sx: { fontSize: '12px' } } }}
              inputProps={{ sx: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
            >
              {periodos.map((p) => (
                <MenuItem key={p.value} value={String(p.value)} sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>{p.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, height: 32 }}>
            <TextField
              label="Termo para análise de tendência"
              value={termo}
              onChange={e => setTermo(e.target.value)}
              fullWidth
              inputProps={{ maxLength: 70, style: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
              InputLabelProps={{ style: { fontSize: '12px', height: 32, minHeight: 32 } }}
              sx={{ minWidth: 340, fontSize: '12px', height: 32, minHeight: 32, alignItems: 'center', display: 'flex' }}
            />
            <Button variant="contained" color="primary" sx={{ fontSize: '12px', height: 32, minWidth: 120, ml: 1, alignSelf: 'center', p: 0 }} onClick={simularNovosDados}>
              Analisar
            </Button>
          </Box>
        </Grid>
      </Grid>
      {periodo === 'custom' && (
        <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
          <Grid>
            <Box display="flex" gap={1}>
              <TextField
                label="Início"
                type="date"
                InputLabelProps={{ shrink: true, sx: { fontSize: '12px', height: 32, minHeight: 32 } }}
                value={customStart}
                onChange={(e) => setCustomStart(e.target.value)}
                fullWidth
                inputProps={{ sx: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
                sx={{ fontSize: '12px', height: 32, minHeight: 32 }}
              />
              <TextField
                label="Fim"
                type="date"
                InputLabelProps={{ shrink: true, sx: { fontSize: '12px', height: 32, minHeight: 32 } }}
                value={customEnd}
                onChange={(e) => setCustomEnd(e.target.value)}
                fullWidth
                inputProps={{ sx: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
                sx={{ fontSize: '12px', height: 32, minHeight: 32 }}
              />
            </Box>
          </Grid>
        </Grid>
      )}
      <Stack direction="row" spacing={6} alignItems="center" justifyContent="center" sx={{ mt: 2, mb: 2, width: '100%' }}>
        <Box sx={{ minWidth: 540, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center' }}>
          <Typography variant="subtitle2" align="center" mb={1} sx={{ fontSize: '12px' }}>Tendência da Categoria</Typography>
          <LineChart width={600} height={300} data={mockDataState[categoria]} margin={{ top: 30, right: 10, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="ds" tick={{ fontSize: 12 }} />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip />
            <Line type="monotone" dataKey="y" stroke={tendenciaCor[tendencia]} strokeWidth={2} dot={{ r: 4 }} label={{ fontSize: 12 }} />
          </LineChart>
        </Box>
        <Stack direction="row" spacing={3} alignItems="center" justifyContent="center">
          <Box sx={{ minWidth: 260, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
            <Typography variant="subtitle2" align="center" mb={1} sx={{ fontSize: '12px' }}>Evolução da Subcategoria</Typography>
            <PieChart width={260} height={260} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
              <Pie
                data={dadosFiltrados}
                dataKey="y"
                nameKey="ds"
                cx="50%"
                cy="50%"
                outerRadius={100}
                labelLine={false}
                label={(props: { percent?: number; x?: number; y?: number; index?: number }) => {
                  const { percent = 0, x = 0, y = 0, index = 0 } = props;
                  function getContrastColor(hex: string): string {
                    if (!hex) return '#000';
                    hex = hex.replace('#', '');
                    const r = parseInt(hex.substring(0,2), 16);
                    const g = parseInt(hex.substring(2,4), 16);
                    const b = parseInt(hex.substring(4,6), 16);
                    const yiq = (r*299 + g*587 + b*114) / 1000;
                    return yiq >= 128 ? '#222' : '#fff';
                  }
                  const corFatia = coresPie[index % coresPie.length];
                  const corTexto = getContrastColor(corFatia);
                  return (
                    <text x={x} y={y} textAnchor="middle" dominantBaseline="central" fill={corTexto} fontSize={12} fontWeight="bold">
                      {(percent * 100).toFixed(0)}%
                    </text>
                  );
                }}
              >
                {dadosFiltrados.map((entry, idx) => (
                  <Cell key={`cell-${idx}`} fill={coresPie[idx % coresPie.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
            {/* Legenda das cores dos produtos da subcategoria - fora do PieChart para garantir renderização */}
            <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', width: '100%', minHeight: 60, background: 'rgba(255,255,255,0.85)', borderRadius: 1, boxShadow: 0, p: 1 }}>
              <Typography variant="caption" sx={{ fontSize: '10px', fontWeight: 'bold', mb: 1, color: '#333' }}>
                Referência de cores dos produtos:
              </Typography>
              {produtos.slice(0, 5).map((prod, idx) => (
                <Box key={prod.id} sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <Box sx={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: coresPie[idx % coresPie.length], mr: 1, border: '1px solid #ccc' }} />
                  <Typography variant="caption" sx={{ fontSize: '10px', color: '#333' }}>{prod.titulo}</Typography>
                </Box>
              ))}
            </Box>
          </Box>
        </Stack>
      </Stack>
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        {/* Cards de insights IA abaixo dos gráficos, agora distribuídos de forma harmônica e centralizada */}
        <Grid container spacing={1} sx={{ mb: 1, mt: 1 }} justifyContent="center">
          {insightsIA.map((insight, idx) => (
            <Grid key={idx} sx={{ display: 'flex', justifyContent: 'center' }}>
              <Card sx={{ bgcolor: '#f5f7fa', boxShadow: 1, borderRadius: 2, p: 0.5, minHeight: 90, maxWidth: 210, width: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                <CardContent sx={{ p: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 'bold', fontSize: '12px', mb: 0.5, lineHeight: 1.2, whiteSpace: 'normal', wordBreak: 'break-word', textAlign: 'center', width: '100%' }}>
                    {insight.icone} {insight.titulo}
                  </Typography>
                  <Typography variant="body2" sx={{ fontSize: '11px', color: '#444', lineHeight: 1.2, textAlign: 'center', width: '100%' }}>{insight.descricao}</Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
          {/* Card de tendência detectada */}
          <Grid sx={{ display: 'flex', justifyContent: 'center' }}>
            <Card sx={{ bgcolor: '#f5f7fa', boxShadow: 1, borderRadius: 2, p: 0.5, minHeight: 90, maxWidth: 210, width: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <CardContent sx={{ p: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', width: '100%' }}>
                <Box sx={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: tendenciaCor[tendencia], mb: 1 }} />
                <Typography variant="subtitle2" sx={{ fontWeight: 'bold', fontSize: '12px', mb: 0.5, textAlign: 'center', width: '100%' }}>
                  Tendência detectada
                </Typography>
                <Typography variant="body2" sx={{ fontSize: '12px', color: tendenciaCor[tendencia], fontWeight: 500, textAlign: 'center', width: '100%' }}>
                  <b>{tendencia}</b>
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>
      <Typography variant="body2" color="text.secondary" mb={2} sx={{ fontSize: '12px' }}>
        Esta funcionalidade armazena diariamente as operações de venda e intenções de compra, permitindo projetar tendências de mercado com base em dados reais. A análise atual é baseada em dados mocados e lógica simplificada. Para explicabilidade real, integre com o modelo Prophet e exiba componentes como sazonalidade, feriados e outliers.
      </Typography>
      <Typography variant="h6" gutterBottom sx={{ fontSize: '14px', fontWeight: 'bold' }}>
        Produtos em destaque
      </Typography>
      <Box sx={{ width: '100%', overflowX: 'auto', pb: 2, minHeight: 80 }}>
        <Box sx={{ width: '100%', overflowX: 'auto', pb: 2 }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
            <thead>
              <tr style={{ background: '#f5f5f5', fontSize: '12px' }}>
                <th style={{ padding: '10px', textAlign: 'left', fontSize: '12px' }}>Imagem</th>
                <th style={{ padding: '10px', textAlign: 'left', fontSize: '12px' }}>Título</th>
                <th style={{ padding: '10px', textAlign: 'left', fontSize: '12px' }}>Vendas</th>
                <th style={{ padding: '10px', textAlign: 'left', fontSize: '12px' }}>Preço</th>
              </tr>
            </thead>
            <tbody>
              {produtos.map((prod) => (
                <tr key={prod.id} style={{ borderBottom: '1px solid #eee', fontSize: '12px' }}>
                  <td style={{ padding: '10px', textAlign: 'center', fontSize: '12px' }}>
                    <img
                      src={prod.imagem || 'https://placehold.co/80x80?text=Produto'}
                      alt={prod.titulo}
                      style={{ width: 48, height: 48, borderRadius: 4, objectFit: 'cover', background: '#eee' }}
                    />
                  </td>
                  <td style={{ padding: '10px', fontSize: '12px' }}>{prod.titulo}</td>
                  <td style={{ padding: '10px', color: '#555', fontWeight: 500, fontSize: '12px' }}>{prod.vendas}</td>
                  <td style={{ padding: '10px', color: '#1976d2', fontWeight: 500, fontSize: '12px' }}>
                    R$ {prod.preco.toLocaleString('pt-br', { minimumFractionDigits: 2 })}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Box>
      </Box>
    </Box>
  );
}
