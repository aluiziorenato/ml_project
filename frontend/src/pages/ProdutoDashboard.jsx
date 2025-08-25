// src/pages/ProdutoDashboard.jsx
import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Box, Typography, Paper } from "@mui/material";
import axios from "axios";

export default function ProdutoDashboard() {
  const { id } = useParams();
  const [produto, setProduto] = useState(null);

  useEffect(() => {
    axios.get(`/api/anuncios/${id}`).then((res) => setProduto(res.data));
  }, [id]);

  if (!produto) return null;

  return (
    <Box p={2}>
      <Typography variant="h5">{produto.nome}</Typography>
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography>ROI: {produto.roi}%</Typography>
        <Typography>Preço: R$ {produto.preco}</Typography>
        <Typography>Demanda: {produto.demanda}</Typography>
        <Typography>Concorrência: {produto.concorrencia}</Typography>
      </Paper>
    </Box>
  );
}
