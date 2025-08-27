import React, { useState } from "react";
import { Box, TextField, Button, Typography, Paper } from "@mui/material";

const respostasMock = [
  { usuario: "Você", texto: "Olá!" },
  { usuario: "Bot", texto: "Olá, como posso ajudar?" },
];

export default function Chatbot() {
  const [mensagem, setMensagem] = useState("");
  const [conversa, setConversa] = useState(respostasMock);

  const enviar = () => {
    if (mensagem.trim()) {
      setConversa([...conversa, { usuario: "Você", texto: mensagem }, { usuario: "Bot", texto: "Resposta mockada." }]);
      setMensagem("");
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5">Chatbot</Typography>
      <Box sx={{ mb: 2 }}>
        {conversa.map((msg, i) => (
          <Typography key={i}><b>{msg.usuario}:</b> {msg.texto}</Typography>
        ))}
      </Box>
      <TextField value={mensagem} onChange={e => setMensagem(e.target.value)} label="Mensagem" fullWidth />
      <Button onClick={enviar} variant="contained" sx={{ mt: 1 }}>Enviar</Button>
    </Paper>
  );
}
