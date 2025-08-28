import React, { useState } from "react";
import { Grid, Card, Typography, Slider, Button } from "@mui/material";

const OtimizacaoTest: React.FC = () => {
  const [param, setParam] = useState<number>(50);
  const sugestoes: string[] = ["Aumentar orçamento", "Reduzir CPC", "Testar novo criativo"];

  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Card sx={{ p: 2 }}>
          <Typography variant="h6">Parâmetro de Otimização</Typography>
          <Slider value={param} onChange={(_, v) => setParam(v as number)} min={0} max={100} />
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
};

export default OtimizacaoTest;
