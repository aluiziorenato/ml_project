import React, { useState } from "react";
import { Box, TextField, Button, Typography, Paper } from "@mui/material";

interface Mensagem {
  usuario: string;
  texto: string;
}

const respostasMock: Mensagem[] = [
  { usuario: "Você", texto: "Olá!" },
  { usuario: "Bot", texto: "Olá, como posso ajudar?" },
];

const Chatbot: React.FC = () => {
  const [mensagem, setMensagem] = useState<string>("");
  const [conversa, setConversa] = useState<Mensagem[]>(respostasMock);

  const enviar = () => {
    if (mensagem.trim()) {
      setConversa([
        ...conversa,
        { usuario: "Você", texto: mensagem },
        { usuario: "Bot", texto: "Resposta mockada." },
      ]);
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
};

export default Chatbot;
