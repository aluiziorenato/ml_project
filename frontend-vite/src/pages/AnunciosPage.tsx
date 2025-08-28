import React, { useState } from "react";
import { Box, Grid, Typography, Button, Card, CardContent, CardActions, Avatar, Chip, Tooltip, Menu, MenuItem, Collapse, IconButton } from "@mui/material";
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import EditIcon from '@mui/icons-material/Edit';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import MenuIcon from '@mui/icons-material/Menu';

// Mock de anúncios
const anuncios = [
  {
    id: 1,
    imagem: "https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
    titulo: "Smartphone Samsung Galaxy S23 Ultra 256GB",
    preco: 5999.99,
    categoria: "Eletrônicos",
    tipo: "gold_pro",
    frete: 29.90,
    desconto: 10,
    promocao: true,
    estoque: 15,
    variacoes: [{}, {}, {}],
    vendas: 120,
    visitas: 350,
    relevancia: 87
  },
  {
    id: 2,
    imagem: "https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
    titulo: "Notebook Dell Inspiron 15 8GB 256GB SSD",
    preco: 3999.90,
    categoria: "Informática",
    tipo: "gold_special",
    frete: 19.90,
    desconto: 5,
    promocao: false,
    estoque: 8,
    variacoes: [{}],
    vendas: 45,
    visitas: 80,
    relevancia: 65
  }
];

export default function AnunciosPage() {
  const [openVaria, setOpenVaria] = useState<number | null>(null);
  const [lista, setLista] = useState(anuncios);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [menuId, setMenuId] = useState<number | null>(null);

  function handleMenuAbrir(event: React.MouseEvent<HTMLElement>, id: number) {
    setMenuAnchor(event.currentTarget);
    setMenuId(id);
  }
  function handleMenuFechar() {
    setMenuAnchor(null);
    setMenuId(null);
  }
  function handleAcao(id: number, acao: string) {
    alert(`Anúncio ${id}: ${acao}`);
    handleMenuFechar();
  }
  function handleEditar(id: number) {
    window.location.href = `/novo-anuncio?id=${id}`;
  }

  function handleOtimizar(id: number) {
    alert(`Otimizar anúncio ${id}`);
  }

  function handleCriar() {
    window.location.href = '/novo-anuncio';
  }

  return (
    <Box sx={{ maxWidth: 1200, mx: "auto", mt: 4, p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 600 }}>Anúncios Mercado Livre</Typography>
        <Button variant="contained" startIcon={<AddCircleOutlineIcon />} onClick={handleCriar} sx={{ fontWeight: 500 }}>Criar Anúncio</Button>
      </Box>
      <Box sx={{ overflowX: 'auto', bgcolor: '#fff', borderRadius: 2, boxShadow: 1 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
          <thead>
            <tr style={{ background: '#f5f6fa', color: '#222a36' }}>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>ID</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Imagem</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Título</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Vendas</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Visitas</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Variações</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Estoque</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Preço</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Categoria</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Tipo</th>
              <th style={{ padding: '8px 4px', textAlign: 'center' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {lista.map(anuncio => (
              <React.Fragment key={anuncio.id}>
                <tr style={{ borderBottom: '1px solid #eee' }}>
                  <td style={{ padding: '6px 4px', verticalAlign: 'top', fontSize: 11, color: '#888', textAlign: 'center' }}>{anuncio.id}</td>
                  <td style={{ padding: '6px 4px' }}>
                    <img src={anuncio.imagem} alt={anuncio.titulo} style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 6 }} />
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'center', fontWeight: 500 }}>
                    {anuncio.titulo}
                    {anuncio.variacoes && anuncio.variacoes.length > 0 && (
                      <IconButton size="small" sx={{ ml: 1 }} onClick={() => setOpenVaria(openVaria === anuncio.id ? null : anuncio.id)}>
                        <ExpandMoreIcon style={{ transform: openVaria === anuncio.id ? 'rotate(180deg)' : 'rotate(0deg)', transition: '0.2s' }} />
                      </IconButton>
                    )}
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'center' }}>
                    <span style={{ display: 'inline-block', border: '1px solid #1976d2', borderRadius: 4, padding: '2px 6px', fontSize: 11, background: '#e3f2fd', color: '#1976d2', minWidth: 28 }}>{anuncio.vendas ?? 0}</span>
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'center' }}>
                    <span style={{ display: 'inline-block', border: '1px solid #388e3c', borderRadius: 4, padding: '2px 6px', fontSize: 11, background: '#e8f5e9', color: '#388e3c', minWidth: 28 }}>{anuncio.visitas ?? 0}</span>
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'center' }}>
                    <span style={{ display: 'inline-block', border: '1px solid #bbb', borderRadius: 4, padding: '2px 6px', fontSize: 11, background: '#f5f6fa', color: '#222a36', minWidth: 28 }}>{anuncio.variacoes?.length || 0}</span>
                  </td>
                  <td style={{ padding: '6px 4px', textAlign: 'center' }}>
                    <span style={{ display: 'inline-block', border: '1px solid #4caf50', borderRadius: 4, padding: '2px 6px', fontSize: 11, background: '#e8f5e9', color: '#388e3c', minWidth: 28 }}>{anuncio.estoque ?? 0}</span>
                  </td>
                  <td style={{ padding: '6px 4px' }}>
                    <div>R$ {anuncio.preco.toFixed(2)}</div>
                    {anuncio.frete && (
                      <div style={{ fontSize: 11, color: '#ff9800', fontWeight: 500, marginTop: 2 }}>
                        Frete: R$ {anuncio.frete.toFixed(2)}
                      </div>
                    )}
                    {anuncio.desconto || anuncio.promocao ? (
                      <div style={{ fontSize: 11, color: '#ff9800', fontWeight: 500, marginTop: 2 }}>
                        {anuncio.desconto ? `Desconto: ${anuncio.desconto}%` : ''}
                        {anuncio.promocao ? `Promoção` : ''}
                      </div>
                    ) : null}
                  </td>
                  <td style={{ padding: '6px 4px' }}>{anuncio.categoria}</td>
                  <td style={{ padding: '6px 4px' }}>{anuncio.tipo === 'gold_pro' ? 'Clássico' : anuncio.tipo === 'gold_special' ? 'Premium' : anuncio.tipo}</td>
                  <td style={{ padding: '6px 4px', minWidth: 120, textAlign: 'center' }}>
                    {/* Relevância após otimizar */}
                    {typeof anuncio.relevancia === 'number' && (
                      <div style={{
                        fontSize: 12,
                        fontWeight: 600,
                        marginBottom: 4,
                        color:
                          anuncio.relevancia < 70 ? '#d32f2f'
                          : anuncio.relevancia < 90 ? '#ff9800'
                          : '#388e3c',
                        background:
                          anuncio.relevancia < 70 ? '#fdecea'
                          : anuncio.relevancia < 90 ? '#fff3e0'
                          : '#e8f5e9',
                        borderRadius: 4,
                        padding: '2px 8px',
                        display: 'inline-block',
                      }}>
                        Relevância: {anuncio.relevancia}%
                      </div>
                    )}
                    <Tooltip title="Editar anúncio" arrow>
                      <Button size="small" startIcon={<EditIcon />} onClick={() => handleEditar(anuncio.id)} sx={{ fontSize: 12, minWidth: 0, px: 1 }}>Editar</Button>
                    </Tooltip>
                    <Tooltip title="Otimizar anúncio com IA" arrow>
                      <Button size="small" startIcon={<AutoFixHighIcon />} onClick={() => handleOtimizar(anuncio.id)} sx={{ fontSize: 12, minWidth: 0, px: 1, ml: 1 }}>Otimizar</Button>
                    </Tooltip>
                    <Button size="small" sx={{ minWidth: 0, p: 0, ml: 1 }} onClick={e => handleMenuAbrir(e, anuncio.id)}>
                      <MenuIcon />
                    </Button>
                    <Menu
                      anchorEl={menuAnchor}
                      open={menuId === anuncio.id}
                      onClose={handleMenuFechar}
                      anchorOrigin={{ vertical: 'bottom', horizontal: 'left' }}
                      transformOrigin={{ vertical: 'top', horizontal: 'left' }}
                    >
                      <MenuItem onClick={() => handleAcao(anuncio.id, 'Ativar')}>Ativar</MenuItem>
                      <MenuItem onClick={() => handleAcao(anuncio.id, 'Pausar')}>Pausar</MenuItem>
                      <MenuItem onClick={() => handleAcao(anuncio.id, 'Desativar')}>Desativar</MenuItem>
                      <MenuItem onClick={() => handleAcao(anuncio.id, 'Excluir')} sx={{ color: '#d32f2f' }}>Excluir</MenuItem>
                    </Menu>
                  </td>
                </tr>
                {anuncio.variacoes && anuncio.variacoes.length > 0 && (
                  <tr>
                    <td colSpan={12} style={{ padding: 0, background: '#f9f9f9' }}>
                      <Collapse in={openVaria === anuncio.id} timeout="auto" unmountOnExit>
                        <Box sx={{ p: 2 }}>
                          <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>Variações</Typography>
                          {anuncio.variacoes.map((v: any, idx: any) => (
                            <Box key={idx} sx={{ display: 'flex', gap: 2, alignItems: 'center', mb: 1, borderBottom: '1px solid #eee', pb: 1 }}>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>SKU: {'-'}</Typography>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>Preço: R$ {(v.preco ?? anuncio.preco).toFixed(2)}</Typography>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>Estoque: {v.estoque ?? anuncio.estoque ?? '-'}</Typography>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>Vendas: {v.vendas ?? anuncio.vendas ?? '-'}</Typography>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>Visitas: {v.visitas ?? anuncio.visitas ?? '-'}</Typography>
                              <Typography sx={{ minWidth: 80, fontSize: 13, color: '#222' }}>Variações: {anuncio.variacoes.length}</Typography>
                            </Box>
                          ))}
                        </Box>
                      </Collapse>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </Box>
    </Box>
  );
}

