import React, { useState } from "react";
import { Card, Typography, Slider, Button, Grid } from "@mui/material";

export default function Otimizacao() {
  const [param, setParam] = useState(50);
  const sugestoes = ["Aumentar orçamento", "Reduzir CPC", "Testar novo criativo"];

  return (
    <Grid container columns={12} spacing={2}>
      <Grid gridColumn={{ xs: 'span 12', md: 'span 6' }}>
        <Card sx={{ p: 2 }}>
          <Typography variant="h6">Parâmetro de Otimização</Typography>
          <Slider value={param} onChange={(_, v) => setParam(v)} min={0} max={100} />
          <Typography>Valor: {param}</Typography>
          <Button variant="contained" sx={{ mt: 2 }}>Aplicar</Button>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card sx={{ p: 2 }}>
          <Typography variant="h6">Sugestões</Typography>
          {sugestoes.map((s, i) => (
            <Typography key={i}>- {s}</Typography>
          ))}
        </Card>
      </Grid>
    </Grid>
  );
}
