// Importa React e hooks para estado
import React, { useState } from "react";
// ...existing code...

// Importa componentes do Material UI para layout, formulários, tabelas e modais
import Box from "@mui/material/Box";
import Card from "@mui/material/Card";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TextField from "@mui/material/TextField";
import Snackbar from "@mui/material/Snackbar";
import Alert from "@mui/material/Alert";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Grid from "@mui/material/Grid";

// Mock de campanhas para exibição na tabela
// Em produção, viria de API/backend
// Possível melhoria: tipar corretamente os objetos
// Lista mockada de campanhas para exibição na tabela principal
// Cada campanha possui id, nome, status, performance, orçamento e ACOS
// Em produção, substituir por dados vindos de API/backend
const mockCampaigns = [
  {
    id: "CMP001",
    name: "Campanha de Primavera",
    status: "Ativa",
    performance: "Ótima",
    budget: 5000,
    acos: 18.5
  },
  {
    id: "CMP002",
    name: "Descontos Relâmpago",
    status: "Pausada",
    performance: "Média",
    budget: 3000,
    acos: 22.1
  }
];

// Mock de promoções para exibição na tabela
// Em produção, viria de API/backend
// Possível melhoria: tipar corretamente os objetos
// Lista mockada de promoções para exibição na tabela secundária
// Cada promoção possui id, item, desconto e status
// Em produção, substituir por dados vindos de API/backend
const mockPromotions = [
  {
    id: "PROMO01",
    item: "Smartphone XYZ",
    discount: "15%",
    status: "Ativa",
    produtos: ["MLB123456", "MLB987654"]
  },
  {
    id: "PROMO02",
    item: "Tênis ABC",
    discount: "20%",
    status: "Expirada",
    produtos: ["MLB654321"]
  }
];

// Componente principal da página de otimização de campanhas
// Possui múltiplos estados para modais, campanhas e produtos
// Possível melhoria: dividir em componentes menores
/**
 * Componente principal da página de Otimização de Campanhas.
 * Exibe tabelas, formulários e modais para gerenciar campanhas e promoções.
 * Utiliza Material UI para layout e componentes visuais.
 *
 * Possíveis melhorias:
 * - Dividir em componentes menores
 * - Tipar corretamente os estados
 * - Integrar com backend/API
 */
const Otimizacao: React.FC = () => {
  // Estado para modal de edição de promoção
  const [openEditPromotionModal, setOpenEditPromotionModal] = useState(false);
  // Estado para modal de nova promoção
  const [openNovaPromocao, setOpenNovaPromocao] = useState(false);
  const [novaPromocao, setNovaPromocao] = useState({
    deal_id: '',
    price: '',
    discount_percentage: '',
    start_time: '',
    end_time: '',
    produtos: []
    // status: '',
    // title: '',
    // available_quantity: ''
  });
  // Estado para modal de detalhes de promoção
  const [openPromoModal, setOpenPromoModal] = useState(false);
  const [selectedPromotion, setSelectedPromotion] = useState<any | null>(null);
  // Estados para controle dos modais de edição/criação de campanha e seleção de produtos
  const [openEditProductModal, setOpenEditProductModal] = useState(false);
  const [editCampaign, setEditCampaign] = useState<any | null>(null); // Campanha em edição
  const [openEditModal, setOpenEditModal] = useState(false); // Modal de edição
  const [openProductModal, setOpenProductModal] = useState(false); // Modal de seleção de produtos
  // Lista de produtos mockada
  // Possível melhoria: tipar corretamente e buscar de API
  // Lista mockada de produtos disponíveis para campanhas
  // Cada produto possui id, título, preço, imagem, tipo, categoria e status
  // Em produção, substituir por dados vindos de API/backend
  const [productList] = useState([
    {
      id: "MLB123456",
      title: "Smartphone XYZ",
      price: 1999.99,
      image: "https://http2.mlstatic.com/D_870627-MLA111111_022024-I.jpg",
      type: "premium",
      category: "Celulares",
      status: "active"
    },
    {
      id: "MLB654321",
      title: "Tênis ABC",
      price: 299.90,
      image: "https://http2.mlstatic.com/D_870627-MLA222222_022024-I.jpg",
      type: "classico",
      category: "Calçados",
      status: "paused"
    },
    {
      id: "MLB987654",
      title: "Fone de Ouvido QWE",
      price: 149.50,
      image: "https://http2.mlstatic.com/D_870627-MLA333333_022024-I.jpg",
      type: "premium",
      category: "Eletrônicos",
      status: "active"
    }
  ]);
  // Estado para modal de criação de campanha
  // Estado para controlar abertura do modal de criação de campanha
  const [openDialog, setOpenDialog] = useState(false);
  // Estado para Snackbar de feedback
  // Estado para controlar exibição de feedback ao usuário
  // message: texto exibido
  // severity: tipo de alerta (success ou error)
  const [snackbar, setSnackbar] = useState<{open: boolean, message: string, severity: "success"|"error"}>({open: false, message: "", severity: "success"});
  // Estado para nova campanha (formulário de criação)
  // Possível melhoria: tipar corretamente
  // Estado para armazenar dados do formulário de nova campanha
  // name: nome da campanha
  // budget: orçamento
  // acos_target: objetivo de ACOS
  // strategy: estratégia de campanha
  // channel: canal de venda
  // status: status da campanha
  // currency_id: moeda
  // items: produtos selecionados
  const [newCampaign, setNewCampaign] = useState({
    name: "",
    budget: "",
    acos_target: "",
    strategy: "profitability",
    channel: "marketplace",
    status: "active",
    currency_id: "BRL",
    items: ""
  });

  // Função para criar campanha (mock)
  // Possível melhoria: enviar dados para backend/API
  /**
   * Função para criar uma nova campanha.
   * Exibe feedback via Snackbar e reseta o formulário.
   * Atualmente apenas mocka a criação, não envia para backend.
   */
  /**
   * Cria uma nova campanha a partir dos dados do formulário.
   * Exibe feedback de sucesso e reseta o formulário.
   * Em produção, deve enviar os dados para o backend/API.
   */
  const handleCreateCampaign = () => {
    setSnackbar({open: true, message: "Campanha criada com sucesso!", severity: "success"});
    setOpenDialog(false);
    setNewCampaign({
      name: "",
      budget: "",
      acos_target: "",
      strategy: "profitability",
      channel: "marketplace",
      status: "active",
      currency_id: "BRL",
      items: ""
    });
  };

  // Renderização principal da página
  // Possui grid com tabela de campanhas, promoções e formulários
  // Possível melhoria: dividir em componentes menores
  return (
    <Box sx={{ p: 4 }}>
      {/* Título principal da página: nome do módulo */}
      <Typography variant="h3" fontWeight={700} sx={{ mb: 3, textAlign: 'center' }}>
        Otimização de Campanhas
      </Typography>

      {/* PROBLEMA: Título duplicado, pode remover o próximo bloco */}
      <Typography variant="h4" gutterBottom>
        Otimização de Campanhas
      </Typography>
            {/* Tabela de campanhas ativas */}
      {/* Modal de edição de campanha */}
      {/* PROBLEMA: Modal de edição de campanha contém lógica repetida de campos e produtos */}
        {/* PROBLEMA: Campos de campanha repetidos, podem ser extraídos para componente reutilizável */}
              {/* PROBLEMA: Lógica de manipulação de produtos duplicada nos modais de edição e criação */}
              {/* PROBLEMA: Não há lógica de salvar edição, apenas fecha o modal */}
      {/* Modal de seleção de produtos para edição de campanha */}
      {/* PROBLEMA: Modal de seleção de produtos duplicado, lógica igual ao modal de criação */}
            {/* Card de criação de nova campanha */}
            {/* PROBLEMA: Campos de campanha repetidos, podem ser extraídos para componente reutilizável */}
      {/* Modal de criação de campanha */}
      {/* Modal de seleção de produtos para criação de campanha */}
      {/* PROBLEMA: Modal de seleção de produtos duplicado, lógica igual ao modal de edição */}

      {/* Grid principal: layout da página, divide em colunas para campanhas (esquerda) e criação (direita) */}
      <Grid container spacing={3}>
        {/* Grid coluna esquerda: exibe tabela de campanhas ativas e promoções recentes */}
            {/* Card de campanhas ativas: exibe lista de campanhas mockadas */}
      {/* Modal de edição de campanha: permite editar dados e produtos de uma campanha existente */}
        {/* Grid de campos do formulário de edição de campanha */}
              {/* Lista de produtos da campanha em edição, permite excluir produtos individualmente */}
              {/* Botões de ação do modal de edição: fechar e salvar (atualmente só fecha) */}
      {/* Modal de seleção de produtos para edição de campanha: permite marcar/desmarcar produtos */}
            {/* Card de criação de nova campanha: formulário para cadastrar nova campanha */}
      {/* Modal de criação de campanha: formulário detalhado para cadastrar nova campanha */}
      {/* Modal de seleção de produtos para criação de campanha: permite marcar/desmarcar produtos */}
        <Grid size={{ xs: 12, md: 12 }}>
          {/* O uso de <Grid item xs={12} md={7}> está correto para MUI v5. Certifique-se que o import está assim: */}
          {/* import Grid from "@mui/material/Grid"; */}
          {/* Se o erro persistir, pode ser conflito de versão ou import duplicado. */}
          <Card sx={{ mb: 3, p: 4, minHeight: 360, boxShadow: 6, borderRadius: 4, background: '#f5f5fc' }}>
            <Typography variant="h6" gutterBottom>
              Campanhas Ativas
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Nome</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Performance</TableCell>
                    <TableCell>Orçamento</TableCell>
                    <TableCell>ACOS (%)</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockCampaigns.map((c) => (
                    <TableRow key={c.id}>
                      <TableCell>{c.id}</TableCell>
                      <TableCell>{c.name}</TableCell>
                      <TableCell>{c.status}</TableCell>
                      <TableCell>{c.performance}</TableCell>
                      <TableCell>R$ {c.budget}</TableCell>
                      <TableCell>{c.acos}</TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" onClick={() => {
                          setEditCampaign(c);
                          setOpenEditModal(true);
                        }}>Editar</Button>
                      </TableCell>
                    </TableRow>
                  ))}
      {/* Modal de edição de campanha */}
      <Dialog open={openEditModal} onClose={() => setOpenEditModal(false)} maxWidth="md" fullWidth>
        <DialogTitle>Editar Campanha</DialogTitle>
        {/* Campos de edição da campanha */}
        {editCampaign && (
          <Box sx={{
            width: { xs: '100%', sm: '600px', md: '900px' },
            maxHeight: { xs: '90vh', md: '95vh' },
            overflowY: 'auto',
            p: { xs: 1, sm: 2 }
          }}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  label="Nome da Campanha"
                  fullWidth
                  value={editCampaign.name}
                  onChange={e => setEditCampaign({ ...editCampaign, name: e.target.value })}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 2 }}>
                <TextField
                  label="Orçamento (R$)"
                  fullWidth
                  type="number"
                  value={editCampaign.budget}
                  onChange={e => setEditCampaign({ ...editCampaign, budget: e.target.value })}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 2 }}>
                <TextField
                  label="ACOS (%)"
                  fullWidth
                  type="number"
                  value={editCampaign.acos}
                  onChange={e => setEditCampaign({ ...editCampaign, acos: e.target.value })}
                />
              </Grid>
              <Grid size={{ xs: 12, sm: 2 }}>
                <TextField
                  label="Status"
                  fullWidth
                  select
                  SelectProps={{ native: true }}
                  value={editCampaign.status}
                  onChange={e => setEditCampaign({ ...editCampaign, status: e.target.value })}
                >
                  <option value="Ativa">Ativa</option>
                  <option value="Pausada">Pausada</option>
                </TextField>
              </Grid>
              <Grid size={{ xs: 12, sm: 3 }}>
                <TextField
                  label="Estratégia"
                  fullWidth
                  select
                  SelectProps={{ native: true }}
                  value={editCampaign.strategy || "profitability"}
                  onChange={e => setEditCampaign({ ...editCampaign, strategy: e.target.value })}
                >
                  <option value="profitability">Rentabilidade</option>
                  <option value="increase">Crescimento</option>
                  <option value="visibility">Visibilidade</option>
                </TextField>
              </Grid>
            </Grid>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle1" gutterBottom>Produtos da campanha:</Typography>
              {editCampaign.items && editCampaign.items.split(',').map((id: string) => {
                const prod = productList.find(p => p.id === id);
                if (!prod) return null;
                return (
                  <Box key={id} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <img src={prod.image} alt={prod.title} style={{ width: 32, height: 32, objectFit: 'cover', borderRadius: 4, marginRight: 8 }} />
                    <Typography variant="body2">{prod.title}</Typography>
                    <Typography variant="caption" color="textSecondary" sx={{ ml: 2 }}>ID: {prod.id}</Typography>
                    <Button size="small" color="error" sx={{ ml: 2 }} onClick={() => {
                      const ids = editCampaign.items.split(',').filter((pid: string) => pid !== id);
                      setEditCampaign({ ...editCampaign, items: ids.join(',') });
                    }}>Excluir</Button>
                  </Box>
                );
              })}
              <Button variant="outlined" size="small" sx={{ mt: 1 }} onClick={() => setOpenEditProductModal(true)}>
                Incluir Produtos
              </Button>
            </Box>
            <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2, mt: 2, pr: 4 }}>
              <Button onClick={() => setOpenEditModal(false)} color="secondary" variant="outlined">Fechar</Button>
              <Button onClick={() => setOpenEditModal(false)} variant="contained" color="primary">Salvar</Button>
            </Box>
          </Box>
        )}
      {/* Modal de seleção de produtos para edição de campanha */}
      <Dialog open={openEditProductModal} onClose={() => setOpenEditProductModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Selecionar Produtos para Campanha</DialogTitle>
        <DialogContent>
          <Box>
            {productList.map((prod) => {
              const ids = editCampaign?.items ? editCampaign.items.split(',') : [];
              const checked = ids.includes(prod.id);
              return (
                <Box key={prod.id} sx={{ display: 'flex', alignItems: 'center', mb: 2, p: 1, borderBottom: '1px solid #eee' }}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => {
                      if (!editCampaign) return;
                      const newIds = checked
                        ? ids.filter((id: number) => id !== prod.id)
                        : [...ids, prod.id];
                      setEditCampaign({ ...editCampaign, items: newIds.filter(Boolean).join(',') });
                    }}
                  />
                  <img src={prod.image} alt={prod.title} style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 6, marginLeft: 12 }} />
                  <Box sx={{ ml: 2, flex: 1 }}>
                    <Typography variant="body1">{prod.title}</Typography>
                    <Typography variant="caption" color="textSecondary">ID: {prod.id}</Typography>
                    <Typography variant="caption" color="textSecondary">Categoria: {prod.category}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 90, textAlign: 'right', mr: 2 }}>
                    <Typography variant="body2" color="primary">R$ {prod.price.toFixed(2)}</Typography>
                    <Typography variant="caption" color="textSecondary">{prod.type === "premium" ? "Premium" : "Clássico"}</Typography>
                    <Typography variant="caption" color={prod.status === "active" ? "success.main" : "warning.main"} sx={{ display: 'block' }}>
                      {prod.status === "active" ? "Ativo" : "Pausado"}
                    </Typography>
                  </Box>
                </Box>
              );
            })}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenEditProductModal(false)} color="secondary">Fechar</Button>
          <Button
            onClick={() => {
              if (!editCampaign) return;
              setEditCampaign({ ...editCampaign, items: "" });
            }}
            color="error"
            variant="outlined"
          >
            Excluir Selecionados
          </Button>
          <Button onClick={() => setOpenEditProductModal(false)} variant="contained" color="primary">Aplicar</Button>
        </DialogActions>
      </Dialog>
      </Dialog>
                </TableBody>
              </Table>
            </TableContainer>
            <Box sx={{ mt: 2, textAlign: "right" }}>
              <Button variant="contained" onClick={() => setOpenDialog(true)}>
                Nova Campanha
              </Button>
            </Box>
          </Card>

          <Card sx={{ p: 2, boxShadow: 3 }}>
            <Typography variant="h6" gutterBottom>
              Promoções Recentes
            </Typography>
            <Box sx={{ mt: 2, textAlign: "right" }}>
              <Button variant="outlined" color="primary" onClick={() => setOpenNovaPromocao(true)}>
                Nova Promoção
              </Button>
            </Box>
      {/* Modal Nova Promoção */}
      <Dialog open={openNovaPromocao} onClose={() => setOpenNovaPromocao(false)} sx={{ '& .MuiPaper-root': { maxWidth: '100vw', width: '100%', maxWidth: 900 } }}>
        <DialogTitle>Criar Nova Promoção</DialogTitle>
        <DialogContent sx={{ p: 2 }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, p: 2 }}>
            <TextField label="ID da Promoção (deal_id)" value={novaPromocao.deal_id} onChange={e => setNovaPromocao({ ...novaPromocao, deal_id: e.target.value })} fullWidth />
            <TextField label="Preço Promocional" value={novaPromocao.price} onChange={e => setNovaPromocao({ ...novaPromocao, price: e.target.value })} fullWidth />
            <TextField label="% de Desconto" value={novaPromocao.discount_percentage} onChange={e => setNovaPromocao({ ...novaPromocao, discount_percentage: e.target.value })} fullWidth />
            <TextField label="Início" type="datetime-local" value={novaPromocao.start_time} onChange={e => setNovaPromocao({ ...novaPromocao, start_time: e.target.value })} fullWidth />
            <TextField label="Fim" type="datetime-local" value={novaPromocao.end_time} onChange={e => setNovaPromocao({ ...novaPromocao, end_time: e.target.value })} fullWidth />
            <Typography variant="subtitle1" sx={{ mt: 2 }}>Produtos Ativos</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
              {productList.filter(p => p.status === 'active').map((p) => (
                <Box key={p.id} sx={{ width: '100%', border: '1px solid #eee', borderRadius: 2, p: 1, display: 'flex', alignItems: 'center', mb: 1 }}>
                  <input
                    type="checkbox"
                    checked={novaPromocao.produtos.includes(p.id)}
                    onChange={e => {
                      const checked = e.target.checked;
                      setNovaPromocao({
                        ...novaPromocao,
                        produtos: checked
                          ? [...novaPromocao.produtos, p.id]
                          : novaPromocao.produtos.filter(id => id !== p.id)
                      });
                    }}
                    style={{ marginRight: 12 }}
                  />
                  <Typography variant="body2" sx={{ width: 120 }}>{p.id}</Typography>
                  <Box sx={{ width: 48, height: 48, mr: 2 }}>
                    <img src={p.image} alt={p.title} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 4 }} />
                  </Box>
                  <Typography variant="body2" sx={{ flex: 1 }}>{p.title}</Typography>
                  <Typography variant="body2" sx={{ width: 120 }}>{p.category}</Typography>
                  <Typography variant="body2" sx={{ width: 100, textAlign: 'right' }}>R$ {p.price.toFixed(2)}</Typography>
                </Box>
              ))}
            </Box>
            {/* <TextField label="Status" value={novaPromocao.status} onChange={e => setNovaPromocao({ ...novaPromocao, status: e.target.value })} fullWidth /> */}
            {/* <TextField label="Título do Item" value={novaPromocao.title} onChange={e => setNovaPromocao({ ...novaPromocao, title: e.target.value })} fullWidth /> */}
            {/* <TextField label="Quantidade Disponível" value={novaPromocao.available_quantity} onChange={e => setNovaPromocao({ ...novaPromocao, available_quantity: e.target.value })} fullWidth /> */}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNovaPromocao(false)} color="secondary">Cancelar</Button>
          <Button onClick={() => { setOpenNovaPromocao(false); }} variant="contained" color="primary">Salvar</Button>
        </DialogActions>
      </Dialog>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>ID</TableCell>
                    <TableCell>Item</TableCell>
                    <TableCell>Desconto</TableCell>
                    <TableCell>Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {mockPromotions.map((p) => (
                    <TableRow key={p.id} hover>
                      <TableCell>{p.id}</TableCell>
                      <TableCell>{p.item}</TableCell>
                      <TableCell>{p.discount}</TableCell>
                      <TableCell>{p.status}</TableCell>
                      <TableCell>
                        <Button size="small" variant="outlined" onClick={() => { setSelectedPromotion(p); setOpenEditPromotionModal(true); }}>Editar</Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
            {/* Modal de edição da promoção */}
            <Dialog open={openEditPromotionModal} onClose={() => setOpenEditPromotionModal(false)} maxWidth="md" fullWidth sx={{ '& .MuiPaper-root': { maxWidth: '100vw', width: '100%', maxWidth: 900 } }}>
              <DialogTitle>Editar Promoção</DialogTitle>
              <DialogContent>
                {selectedPromotion && (
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <TextField
                      label="ID"
                      value={selectedPromotion.id}
                      fullWidth
                      disabled
                    />
                    <TextField
                      label="Desconto"
                      value={selectedPromotion.discount}
                      onChange={e => setSelectedPromotion({ ...selectedPromotion, discount: e.target.value })}
                      fullWidth
                    />
                    <TextField
                      label="Status"
                      value={selectedPromotion.status}
                      onChange={e => setSelectedPromotion({ ...selectedPromotion, status: e.target.value })}
                      fullWidth
                    />
                    <Typography variant="subtitle2" sx={{ mt: 2 }}>Produtos</Typography>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                      {productList.map((prod) => {
                        const checked = selectedPromotion.produtos?.includes(prod.id);
                        return (
                          <Box key={prod.id} sx={{ display: 'flex', alignItems: 'center', border: '1px solid #eee', borderRadius: 2, p: 1, mb: 1 }}>
                            <input
                              type="checkbox"
                              checked={checked}
                              onChange={e => {
                                const isChecked = e.target.checked;
                                let newProdutos = selectedPromotion.produtos ? [...selectedPromotion.produtos] : [];
                                if (isChecked) {
                                  if (!newProdutos.includes(prod.id)) newProdutos.push(prod.id);
                                } else {
                                  newProdutos = newProdutos.filter(id => id !== prod.id);
                                }
                                setSelectedPromotion({ ...selectedPromotion, produtos: newProdutos });
                              }}
                              style={{ marginRight: 12 }}
                            />
                            <Typography variant="body2" sx={{ width: 120 }}>{prod.id}</Typography>
                            <Box sx={{ width: 48, height: 48, mr: 2 }}>
                              <img src={prod.image} alt={prod.title} style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: 4 }} />
                            </Box>
                            <Typography variant="body2" sx={{ flex: 1 }}>{prod.title}</Typography>
                            <Typography variant="body2" sx={{ width: 100, textAlign: 'right' }}>R$ {prod.price.toFixed(2)}</Typography>
                          </Box>
                        );
                      })}
                    </Box>
                  </Box>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setOpenEditPromotionModal(false)} color="secondary">Cancelar</Button>
                <Button
                  onClick={() => {
                    // Atualiza mockPromotions (apenas local, sem backend)
                    if (selectedPromotion) {
                      const idx = mockPromotions.findIndex(p => p.id === selectedPromotion.id);
                      if (idx !== -1) {
                        mockPromotions[idx] = { ...selectedPromotion };
                      }
                    }
                    setOpenEditPromotionModal(false);
                  }}
                  variant="contained"
                  color="primary"
                >Salvar</Button>
              </DialogActions>
            </Dialog>
            {/* Modal de detalhes da promoção */}
            <Dialog open={openPromoModal} onClose={() => setOpenPromoModal(false)} maxWidth="xs" fullWidth>
              <DialogTitle>Detalhes da Promoção</DialogTitle>
              <DialogContent>
                {selectedPromotion && (
                  <Box>
                    <Typography variant="subtitle1"><b>ID:</b> {selectedPromotion.id}</Typography>
                    <Typography variant="subtitle1"><b>Item:</b> {selectedPromotion.item}</Typography>
                    <Typography variant="subtitle1"><b>Desconto:</b> {selectedPromotion.discount}</Typography>
                    <Typography variant="subtitle1"><b>Status:</b> {selectedPromotion.status}</Typography>
                  </Box>
                )}
              </DialogContent>
              <DialogActions>
                <Button onClick={() => setOpenPromoModal(false)} color="primary">Fechar</Button>
              </DialogActions>
            </Dialog>
          </Card>
        </Grid>

        {/* Card 'Criar Nova Campanha' removido conforme solicitado */}
      {/* Fim do Grid principal: fecha layout da página */}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)}>
        <DialogTitle>Nova Campanha</DialogTitle>
        <DialogContent>
          <Grid container spacing={2}>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Nome da Campanha"
                fullWidth
                value={newCampaign.name}
                onChange={e => setNewCampaign({ ...newCampaign, name: e.target.value })}
              />
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Orçamento (R$)"
                fullWidth
                type="number"
                value={newCampaign.budget}
                onChange={e => setNewCampaign({ ...newCampaign, budget: e.target.value })}
              />
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="ACOS Objetivo (%)"
                fullWidth
                type="number"
                value={newCampaign.acos_target}
                onChange={e => setNewCampaign({ ...newCampaign, acos_target: e.target.value })}
              />
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Estratégia"
                fullWidth
                select
                SelectProps={{ native: true }}
                value={newCampaign.strategy}
                onChange={e => setNewCampaign({ ...newCampaign, strategy: e.target.value })}
              >
                <option value="profitability">Rentabilidade</option>
                <option value="increase">Crescimento</option>
                <option value="visibility">Visibilidade</option>
              </TextField>
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Canal"
                fullWidth
                select
                SelectProps={{ native: true }}
                value={newCampaign.channel}
                onChange={e => setNewCampaign({ ...newCampaign, channel: e.target.value })}
              >
                <option value="marketplace">Mercado Livre</option>
                <option value="mshops">Mercado Shops</option>
              </TextField>
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Status"
                fullWidth
                select
                SelectProps={{ native: true }}
                value={newCampaign.status}
                onChange={e => setNewCampaign({ ...newCampaign, status: e.target.value })}
              >
                <option value="active">Ativa</option>
                <option value="paused">Pausada</option>
              </TextField>
            </Grid>
          <Grid size={{ xs: 12, sm: 6 }}>
              <TextField
                label="Moeda"
                fullWidth
                value={newCampaign.currency_id}
                onChange={e => setNewCampaign({ ...newCampaign, currency_id: e.target.value })}
              />
            </Grid>
            <Grid size={12}>
              <Button variant="outlined" fullWidth onClick={() => setOpenProductModal(true)}>
                Selecionar Produtos
              </Button>
              {newCampaign.items && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2" color="textSecondary">
                    Produtos selecionados:
                  </Typography>
                  <Typography variant="body2">
                    {newCampaign.items}
                  </Typography>
                </Box>
              )}
            </Grid>
      {/* Modal de seleção de produtos */}
      <Dialog open={openProductModal} onClose={() => setOpenProductModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Selecione os produtos para a campanha</DialogTitle>
        <DialogContent>
          <Box>
            {productList.map((prod) => {
              const ids = newCampaign.items ? newCampaign.items.split(',') : [];
              const checked = ids.includes(prod.id);
              return (
                <Box key={prod.id} sx={{ display: 'flex', alignItems: 'center', mb: 2, p: 1, borderBottom: '1px solid #eee' }}>
                  <input
                    type="checkbox"
                    checked={checked}
                    onChange={() => {
                      const newIds = checked
                        ? ids.filter(id => id !== prod.id)
                        : [...ids, prod.id];
                      setNewCampaign({ ...newCampaign, items: newIds.filter(Boolean).join(',') });
                    }}
                  />
                  <img src={prod.image} alt={prod.title} style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 6, marginLeft: 12 }} />
                  <Box sx={{ ml: 2, flex: 1 }}>
                    <Typography variant="body1">{prod.title}</Typography>
                    <Typography variant="caption" color="textSecondary">ID: {prod.id}</Typography>
                    <Typography variant="caption" color="textSecondary">Categoria: {prod.category}</Typography>
                  </Box>
                  <Box sx={{ minWidth: 90, textAlign: 'right', mr: 2 }}>
                    <Typography variant="body2" color="primary">R$ {prod.price.toFixed(2)}</Typography>
                    <Typography variant="caption" color="textSecondary">{prod.type === "premium" ? "Premium" : "Clássico"}</Typography>
                    <Typography variant="caption" color={prod.status === "active" ? "success.main" : "warning.main"} sx={{ display: 'block' }}>
                      {prod.status === "active" ? "Ativo" : "Pausado"}
                    </Typography>
                  </Box>
                </Box>
              );
            })}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenProductModal(false)} color="secondary">Fechar</Button>
          <Button
            onClick={() => {
              setNewCampaign({ ...newCampaign, items: "" });
            }}
            color="error"
            variant="outlined"
          >
            Excluir Selecionados
          </Button>
          <Button onClick={() => setOpenProductModal(false)} variant="contained" color="primary">Aplicar</Button>
        </DialogActions>
      </Dialog>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancelar</Button>
          <Button variant="contained" onClick={handleCreateCampaign}>Criar</Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar: exibe feedback de sucesso ou erro ao usuário */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={3000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
        anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
      >
        <Alert severity={snackbar.severity} sx={{ width: "100%" }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default Otimizacao;