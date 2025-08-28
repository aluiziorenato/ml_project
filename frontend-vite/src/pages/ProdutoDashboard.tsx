import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import { Box, Typography, Paper } from "@mui/material";
import axios from "axios";

interface Produto {
  nome: string;
  roi: number;
  preco: number;
  demanda: string;
  concorrencia: string;
}

const ProdutoDashboard: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [produto, setProduto] = useState<Produto | null>(null);

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
};

export default ProdutoDashboard;
