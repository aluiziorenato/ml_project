import React, { useState } from "react";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import List from "@mui/material/List";
import ListItem from "@mui/material/ListItem";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemText from "@mui/material/ListItemText";
import CircularProgress from "@mui/material/CircularProgress";

interface OptimizeDescriptionModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  instruction: string;
  onApply: (description: string) => void;
}

export default function OptimizeDescriptionModal({ open, onClose, title, instruction, onApply }: OptimizeDescriptionModalProps) {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  React.useEffect(() => {
    if (!open) return;
    setLoading(true);
    // Chama backend para obter sugestões de descrição
    fetch("/api/optimize-description", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, instruction }),
    })
      .then(res => res.json())
      .then(data => {
        setSuggestions(data.suggestions || []);
        setLoading(false);
      })
      .catch(() => {
        setSuggestions([]);
        setLoading(false);
      });
  }, [open, title, instruction]);

  const handleApply = () => {
    if (selectedIdx === null || !suggestions[selectedIdx]) return;
    onApply(suggestions[selectedIdx]);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Otimizar descrição com IA</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Receba sugestões de descrição otimizadas com base no título do produto e copywriting inteligente. Selecione uma opção para aplicar ao seu anúncio.
        </Typography>
        {loading ? (
          <CircularProgress />
        ) : suggestions.length > 0 ? (
          <List>
            {suggestions.map((desc, idx) => (
              <ListItem key={idx} disablePadding>
                <ListItemButton selected={selectedIdx === idx} onClick={() => setSelectedIdx(idx)}>
                  <ListItemText
                    primary={desc}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        ) : (
          <Typography variant="body2" color="text.secondary">Nenhuma sugestão encontrada.</Typography>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleApply} disabled={selectedIdx === null || loading || suggestions.length === 0} variant="contained" color="primary">
          Aplicar sugestão
        </Button>
      </DialogActions>
    </Dialog>
  );
}
