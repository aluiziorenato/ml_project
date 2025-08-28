import React, { useState } from "react";
import { Box, Grid, Typography, Button, Card, CardContent, CardActions, Avatar, Chip, Tooltip } from "@mui/material";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import EditIcon from '@mui/icons-material/Edit';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';

// Mock de anúncios
const anuncios = [
  {
    id: 1,
    imagem: "https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
    titulo: "Smartphone Samsung Galaxy S23 Ultra 256GB",
    preco: 5999.99,
    categoria: "Eletrônicos",
    tipo: "gold_pro"
  },
  {
    id: 2,
    imagem: "https://http2.mlstatic.com/D_NQ_NP_2X_954825-MLB54981385767_042023-F.webp",
    titulo: "Notebook Dell Inspiron 15 8GB 256GB SSD",
    preco: 3999.90,
    categoria: "Informática",
    tipo: "gold_special"
  }
];

export default function AnunciosPage() {
  const [lista, setLista] = useState(anuncios);

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
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Imagem</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Título</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Preço</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Categoria</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Tipo</th>
              <th style={{ padding: '8px 4px', textAlign: 'left' }}>Ações</th>
            </tr>
          </thead>
          <tbody>
            {lista.map(anuncio => (
              <tr key={anuncio.id} style={{ borderBottom: '1px solid #eee' }}>
                <td style={{ padding: '6px 4px' }}>
                  <img src={anuncio.imagem} alt={anuncio.titulo} style={{ width: 48, height: 48, objectFit: 'cover', borderRadius: 6 }} />
                </td>
                <td style={{ padding: '6px 4px', maxWidth: 320 }}>{anuncio.titulo}</td>
                <td style={{ padding: '6px 4px' }}>R$ {anuncio.preco.toFixed(2)}</td>
                <td style={{ padding: '6px 4px' }}>{anuncio.categoria}</td>
                <td style={{ padding: '6px 4px' }}>{anuncio.tipo}</td>
                <td style={{ padding: '6px 4px', minWidth: 120 }}>
                  <Tooltip title="Editar anúncio" arrow>
                    <Button size="small" startIcon={<EditIcon />} onClick={() => handleEditar(anuncio.id)} sx={{ fontSize: 12, minWidth: 0, px: 1 }}>Editar</Button>
                  </Tooltip>
                  <Tooltip title="Otimizar anúncio com IA" arrow>
                    <Button size="small" startIcon={<AutoFixHighIcon />} onClick={() => handleOtimizar(anuncio.id)} sx={{ fontSize: 12, minWidth: 0, px: 1, ml: 1 }}>Otimizar</Button>
                  </Tooltip>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Box>
    </Box>
  );
}

