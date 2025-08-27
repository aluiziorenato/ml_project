import React, { useState } from "react";
import { Box, TextField, Button, Typography, Paper } from "@mui/material";

export default function ChatbotUpload() {
  const [mensagem, setMensagem] = useState("");
  const [conversa, setConversa] = useState([
    { usuario: "Você", texto: "Olá!" },
    { usuario: "Bot", texto: "Olá, como posso ajudar?" },
  ]);
  const [imagem, setImagem] = useState(null);

  const enviar = () => {
    if (mensagem.trim() || imagem) {
      setConversa([
        ...conversa,
        { usuario: "Você", texto: mensagem, imagem },
        { usuario: "Bot", texto: "Resposta mockada." },
      ]);
      setMensagem("");
      setImagem(null);
    }
  };

  const handleFile = (e) => {
    if (e.target.files[0]) {
      setImagem(URL.createObjectURL(e.target.files[0]));
    }
  };

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5">Chatbot com Upload de Imagem</Typography>
      <Box sx={{ mb: 2 }}>
        {conversa.map((msg, i) => (
          <Box key={i} sx={{ mb: 1 }}>
            <Typography><b>{msg.usuario}:</b> {msg.texto}</Typography>
            {msg.imagem && <img src={msg.imagem} alt="enviada" width={80} />}
          </Box>
        ))}
      </Box>
      <TextField value={mensagem} onChange={e => setMensagem(e.target.value)} label="Mensagem" fullWidth sx={{ mb: 1 }} />
      <input type="file" accept="image/*" onChange={handleFile} />
      <Button onClick={enviar} variant="contained" sx={{ mt: 1 }} disabled={!mensagem && !imagem}>Enviar</Button>
    </Paper>
  );
}
