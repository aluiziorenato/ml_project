import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, Select, MenuItem, FormControl, InputLabel, Button, Grid, Box, TextField, Stack } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';

// Dados mocados por categoria
const mockData = {
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

const categorias = Object.keys(mockData);
const periodos = [
  { label: '7 dias', value: 7 },
  { label: '15 dias', value: 15 },
  { label: '30 dias', value: 30 },
  { label: '60 dias', value: 60 },
  { label: 'Personalizado', value: 'custom' },
];

const coresPie = [
  '#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#A28EFF', '#FF6F91', '#FFD700', '#00BFFF', '#FF6347', '#32CD32'
];

function filtrarPorPeriodo(data, dias, customStart, customEnd) {
  if (dias === 'custom' && customStart && customEnd) {
    return data.filter(
      (item) => item.ds >= customStart && item.ds <= customEnd
    );
  }
  return data.slice(-Number(dias));
}

function calcularTendencia(data) {
  if (data.length < 2) return 'Estável';
  const diff = data[data.length - 1].y - data[0].y;
  if (diff > 20) return 'Alta';
  if (diff < -20) return 'Queda';
  return 'Estável';
}

export default function DetectorTendencias() {
  const [categoria, setCategoria] = useState(categorias[0]);
  const [periodo, setPeriodo] = useState('7'); // tipo string
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');
  const [produtoId, setProdutoId] = useState(null);
  const [termo, setTermo] = useState('');

  // Produtos mocados por categoria (fora do componente para evitar recriação)
  const produtosMock = React.useMemo(() => ({
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
  }), []);

  const produtos = produtosMock[categoria];
  useEffect(() => {
    setProdutoId(produtos[0]?.id || null);
  }, [categoria]);
  const produtoSelecionado = produtos.find(p => p.id === produtoId) || produtos[0];

  // Mock de dados por produto
  const mockDataProduto = React.useMemo(() => ({
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
    // ...outros produtos podem ser adicionados aqui
  }), []);

  // Dados do gráfico: prioriza dados do produto, senão da categoria
  const data = React.useMemo(() => {
    if (mockDataProduto[produtoSelecionado.id]) return mockDataProduto[produtoSelecionado.id];
    return mockData[categoria];
  }, [categoria, produtoSelecionado.id, mockDataProduto]);

  const dadosFiltrados = React.useMemo(() => filtrarPorPeriodo(data, periodo, customStart, customEnd), [data, periodo, customStart, customEnd]);
  const tendencia = React.useMemo(() => calcularTendencia(dadosFiltrados), [dadosFiltrados]);

  const tendenciaCor = {
    Alta: 'green',
    Queda: 'red',
    Estável: 'gray',
  };

  return (
    <Box sx={{ width: '100%', maxWidth: 1100, mx: 'auto', p: 3, bgcolor: '#fafbfc', borderRadius: 3, boxShadow: 2, minHeight: 700, overflow: 'hidden', fontSize: '12px' }}>
      <Card sx={{ width: '100%', boxShadow: 0, bgcolor: 'transparent', fontSize: '12px' }}>
        <CardContent sx={{ fontSize: '12px' }}>
          <Typography variant="h5" gutterBottom sx={{ fontSize: '14px', fontWeight: 'bold' }}>
            Detector de Tendências
          </Typography>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={3}>
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
            <Grid item xs={12} sm={3}>
              <FormControl fullWidth sx={{ fontSize: '12px' }}>
                <InputLabel sx={{ fontSize: '12px', height: 32, minHeight: 32 }}>Subcategoria</InputLabel>
                <Select
                  value={produtoId || produtos[0]?.id || ''}
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
            <Grid item xs={12} sm={3}>
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
            <Grid item xs={12} sm={3}>
              <TextField
                label="Termo para análise de tendência"
                value={termo}
                onChange={e => setTermo(e.target.value)}
                fullWidth
                inputProps={{ maxLength: 70, style: { fontSize: '12px', height: 32, minHeight: 32, padding: '6px 10px' } }}
                InputLabelProps={{ style: { fontSize: '12px', height: 32, minHeight: 32 } }}
                sx={{ minWidth: 180, fontSize: '12px', height: 32, minHeight: 32 }}
              />
            </Grid>
          </Grid>
          {periodo === 'custom' && (
            <Grid container spacing={2} alignItems="center" sx={{ mt: 2 }}>
              <Grid item xs={12} sm={4}>
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
            <Box sx={{ minWidth: 400, display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'center' }}>
              <Typography variant="subtitle2" align="center" mb={1} sx={{ fontSize: '12px' }}>Tendência da Categoria</Typography>
              <ResponsiveContainer width={400} height={300}>
                <LineChart data={mockData[categoria]} margin={{ top: 30, right: 40, left: 20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ds" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="y" stroke="#1976d2" strokeWidth={3} dot={{ r: 4 }} label={{ fontSize: 12 }} />
                </LineChart>
              </ResponsiveContainer>
            </Box>
            <Stack direction="row" spacing={3} alignItems="center" justifyContent="center">
              <Box sx={{ minWidth: 260, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <Typography variant="subtitle2" align="center" mb={1} sx={{ fontSize: '12px' }}>Evolução da Subcategoria</Typography>
                <ResponsiveContainer width={260} height={260} style={{ margin: 0, padding: 0 }}>
                  <PieChart margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                    <Pie
                      data={dadosFiltrados}
                      dataKey="y"
                      nameKey="ds"
                      cx="50%"
                      cy="50%"
                      outerRadius={100}
                      labelLine={false}
                      label={({ percent, x, y, index }) => {
                        // Função para calcular cor contrastante
                        function getContrastColor(hex: string) {
                          if (!hex) return '#000';
                          hex = hex.replace('#', '');
                          const r = parseInt(hex.substring(0,2), 16);
                          const g = parseInt(hex.substring(2,4), 16);
                          const b = parseInt(hex.substring(4,6), 16);
                          // Fórmula de contraste YIQ
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
                        <Cell key={`cell-${idx}`} fill={["#1976d2", "#26a69a", "#ffa726", "#ef5350", "#ab47bc", "#8d6e63"][idx % 6]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </Box>
              <Box sx={{ minWidth: 180 }}>
                <Typography variant="subtitle2" align="center" mb={1} sx={{ fontSize: '12px' }}>Top 5 Subcategorias</Typography>
                <ul style={{ listStyle: 'none', padding: 0, margin: 0, fontSize: '12px' }}>
                  {produtos
                    .sort((a, b) => b.vendas - a.vendas)
                    .slice(0, 5)
                    .map((prod, idx) => (
                      <li key={prod.id} style={{ marginBottom: 6 }}>
                        <span style={{ fontWeight: 500, color: ["#1976d2", "#26a69a", "#ffa726", "#ef5350", "#ab47bc", "#8d6e63"][idx % 6], fontSize: '12px' }}>
                          {prod.titulo}
                        </span>
                        : {prod.vendas} vendas
                      </li>
                    ))}
                </ul>
              </Box>
            </Stack>
          </Stack>

          <Box display="flex" alignItems="center" gap={2} mb={2}>
            <Box
              sx={{
                width: 16,
                height: 16,
                borderRadius: '50%',
                backgroundColor: tendenciaCor[tendencia],
                display: 'inline-block',
              }}
            />
            <Typography variant="subtitle1" sx={{ fontSize: '12px' }}>
              Tendência detectada: <b style={{ color: tendenciaCor[tendencia], fontSize: '12px' }}>{tendencia}</b>
            </Typography>
          </Box>
          <Typography variant="body2" color="text.secondary" mb={2} sx={{ fontSize: '12px' }}>
            Análise baseada em dados mocados e lógica simplificada. Para explicabilidade real, integre com o modelo Prophet e exiba componentes como sazonalidade, feriados e outliers.
          </Typography>
          <Button variant="contained" color="primary" sx={{ mt: 2, mb: 4, fontSize: '12px' }}>
            Simular Novos Dados
          </Button>
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
        </CardContent>
      </Card>
    </Box>
  );
}
