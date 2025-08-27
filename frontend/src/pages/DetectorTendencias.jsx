import React from "react";
import { Card, Typography, Grid } from "@mui/material";

const alertas = [
  { nome: "Nova tendência detectada: Eletrônicos", data: "26/08/2025" },
  { nome: "Queda em moda feminina", data: "25/08/2025" },
];

export default function DetectorTendencias() {
  return (
    <Grid container columns={12} spacing={2}>
      {alertas.map((a, i) => (
        <Grid key={i} gridColumn={{ xs: 'span 12', sm: 'span 6' }}>
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">{a.nome}</Typography>
            <Typography>Data: {a.data}</Typography>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
