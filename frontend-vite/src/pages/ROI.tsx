import React, { useState } from "react";
import { Card, Typography, TextField, Button } from "@mui/material";

const ROI: React.FC = () => {
  const [investimento, setInvestimento] = useState<number>(1000);
  const [retorno, setRetorno] = useState<number>(2500);
  const roi = ((retorno - investimento) / investimento * 100).toFixed(2);

  return (
    <Card sx={{ p: 2 }}>
      <Typography variant="h5">Simulador de ROI</Typography>
      <TextField label="Investimento" type="number" value={investimento} onChange={e => setInvestimento(Number(e.target.value))} sx={{ m: 1 }} />
      <TextField label="Retorno" type="number" value={retorno} onChange={e => setRetorno(Number(e.target.value))} sx={{ m: 1 }} />
      <Typography>ROI: {roi}%</Typography>
      <Button variant="contained" sx={{ mt: 2 }}>Exportar Relatório</Button>
    </Card>
  );
};

export default ROI;
