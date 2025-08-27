import React, { useState } from "react";
import { Card, Typography, TextField, Button } from "@mui/material";

export default function IntencaoSemantica() {
  const [texto, setTexto] = useState("");
  const [resultado, setResultado] = useState("");

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
}
