import React from "react";
import { Card, Typography, Grid } from "@mui/material";

const tendencias = [
  { nome: "Aumento de buscas por eletrônicos", periodo: "Última semana" },
  { nome: "Queda em moda masculina", periodo: "Últimos 30 dias" },
];

export default function Tendencias() {
  return (
    <Grid container columns={12} spacing={2}>
      {tendencias.map((t, i) => (
        <Grid key={i} gridColumn={{ xs: 'span 12', sm: 'span 6' }}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">{t.nome}</Typography>
            <Typography>Período: {t.periodo}</Typography>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
