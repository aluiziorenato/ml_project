import React from "react";
import { Card, Typography, Grid, Button } from "@mui/material";

interface Campanha {
  nome: string;
  status: string;
  vendas: number;
}

const campanhas: Campanha[] = [
  { nome: "Campanha Black Friday", status: "Ativa", vendas: 500 },
  { nome: "Campanha Verão", status: "Finalizada", vendas: 320 },
];

const Campanhas: React.FC = () => {
  return (
    <Grid container columns={12} spacing={2}>
      {campanhas.map((c) => (
        <Grid key={c.nome} gridColumn="span 4">
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">{c.nome}</Typography>
            <Typography>Status: {c.status}</Typography>
            <Typography>Vendas: {c.vendas}</Typography>
            <Button variant="contained" sx={{ mt: 2 }}>Ver Detalhes</Button>
          </Card>
        </Grid>
      ))}
      <Grid gridColumn="span 12">
        <Button variant="outlined">Criar Nova Campanha</Button>
      </Grid>
    </Grid>
  );
};

export default Campanhas;
