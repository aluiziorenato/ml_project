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

interface Suggestion {
  title: string;
  description: string;
}

interface OptimizeProductModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description: string;
  onApply: (suggestion: Partial<Suggestion>) => void;
}

export default function OptimizeProductModal({ open, onClose, title, description, onApply }: OptimizeProductModalProps) {
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number | null>(null);

  React.useEffect(() => {
    if (!open) return;
    setLoading(true);
    // Chama backend para obter sugestões de IA
    fetch("/api/optimize-product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, description }),
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
  }, [open, title, description]);

  const handleApply = () => {
    if (selectedIdx === null || !suggestions[selectedIdx]) return;
    onApply(suggestions[selectedIdx]);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Otimizar título e descrição com IA</DialogTitle>
      <DialogContent>
        <Typography variant="body2" color="text.secondary" mb={2}>
          Receba sugestões de título e descrição otimizados com base em anúncios de destaque e copywriting inteligente. Selecione uma opção para aplicar ao seu anúncio.
        </Typography>
        {loading ? (
          <CircularProgress />
        ) : suggestions.length > 0 ? (
          <List>
            {suggestions.map((s, idx) => (
              <ListItem key={idx} disablePadding>
                <ListItemButton selected={selectedIdx === idx} onClick={() => setSelectedIdx(idx)}>
                  <ListItemText
                    primary={s.title}
                    secondary={s.description}
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
