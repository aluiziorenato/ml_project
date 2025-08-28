import React from "react";
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Button } from "@mui/material";

interface Concorrente {
  nome: string;
  preco: number;
  estoque: number;
}

const concorrentes: Concorrente[] = [
  { nome: "Loja A", preco: 199, estoque: 20 },
  { nome: "Loja B", preco: 210, estoque: 15 },
];

const Concorrentes: React.FC = () => {
  return (
    <TableContainer component={Paper}>
      <Typography variant="h5" sx={{ m: 2 }}>Inteligência de Concorrentes</Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Nome</TableCell>
            <TableCell>Preço</TableCell>
            <TableCell>Estoque</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {concorrentes.map((c) => (
            <TableRow key={c.nome}>
              <TableCell>{c.nome}</TableCell>
              <TableCell>{c.preco}</TableCell>
              <TableCell>{c.estoque}</TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
      <Button variant="outlined" sx={{ mt: 1 }}>Ação IA</Button>
      <Button variant="outlined" sx={{ mt: 1 }}>Detectar Novas Tendências (IA)</Button>
      <Button variant="outlined" sx={{ mt: 1 }}>Comparativo Inteligente</Button>
      <Button variant="outlined" sx={{ mt: 1 }}>Sugestão de estratégia (IA)</Button>
      <Button variant="outlined" sx={{ mt: 1 }}>Análise preditiva de concorrência</Button>
    </TableContainer>
  );
};

export default Concorrentes;
