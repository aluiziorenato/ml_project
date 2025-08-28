import React from "react";
import { Card, Typography, Grid } from "@mui/material";

interface Tendencia {
  nome: string;
  periodo: string;
}

const tendencias: Tendencia[] = [
  { nome: "Aumento de buscas por eletrônicos", periodo: "Última semana" },
  { nome: "Queda em moda masculina", periodo: "Últimos 30 dias" },
];

const Tendencias: React.FC = () => {
  return (
    <Grid container spacing={2}>
      {tendencias.map((t, i) => (
        <Grid item xs={12} sm={6} key={i}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">{t.nome}</Typography>
            <Typography>Período: {t.periodo}</Typography>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default Tendencias;
