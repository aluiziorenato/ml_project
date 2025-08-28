import React, { useState } from "react";
import { Card, Typography, TextField, Button } from "@mui/material";

const IntencaoSemantica: React.FC = () => {
  const [texto, setTexto] = useState<string>("");
  const [resultado, setResultado] = useState<string>("");

  const analisar = () => {
    setResultado("Intenção mockada: Compra");
  };

  return (
    <Card sx={{ p: 2 }}>
      <Typography variant="h5">Análise de Intenção Semântica</Typography>
      <TextField label="Texto" value={texto} onChange={e => setTexto(e.target.value)} fullWidth sx={{ m: 1 }} />
      <Button variant="contained" onClick={analisar}>Analisar</Button>
      {resultado && <Typography sx={{ mt: 2 }}>{resultado}</Typography>}
    </Card>
  );
};

export default IntencaoSemantica;
