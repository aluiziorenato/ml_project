import React, { useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, MenuItem, Typography, Box, CircularProgress, Checkbox, FormControlLabel, Slide } from "@mui/material";

export type KeywordSuggestionModalProps = {
  open: boolean;
  onClose: () => void;
  categorias: string[];
  categoriaLabels: Record<string, string>;
  onSelect: (selected: { title: string; longTail: string; mediumTail: string }) => void;
};

export default function KeywordSuggestionModal({ open, onClose, categorias, categoriaLabels, onSelect }: KeywordSuggestionModalProps) {
  const [categoria, setCategoria] = useState<string>(categorias[0]);
  const [textoBusca, setTextoBusca] = useState<string>("");
  const [excludedTags, setExcludedTags] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [keywords, setKeywords] = useState<string[]>([]);
  const [selectedTitle, setSelectedTitle] = useState<string>("");
  const [selectedLongTail, setSelectedLongTail] = useState<string>("");
  const [selectedMediumTail, setSelectedMediumTail] = useState<string>("");

  const handleTagChange = (tag: string) => {
    setExcludedTags(prev => prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]);
  };

  async function fetchKeywords() {
    setLoading(true);
    setError(null);
    setKeywords([]);
    try {
      const res = await fetch("/meli/questions_service/ai_suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          texto: textoBusca,
          categoria,
          tags_excluir: excludedTags
        })
      });
      if (!res.ok) throw new Error("Erro ao buscar palavras-chave");
      const data = await res.json();
      setKeywords(Array.isArray(data.keywords) ? data.keywords : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  function handleConfirm() {
    if (!selectedTitle || !selectedLongTail || !selectedMediumTail) {
      setError("Selecione uma palavra para título, uma long tail e uma medium tail.");
      return;
    }
    onSelect({ title: selectedTitle, longTail: selectedLongTail, mediumTail: selectedMediumTail });
    onClose();
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="lg" fullWidth TransitionComponent={Slide}>
      <DialogTitle sx={{ fontSize: 28, py: 3 }}>Sugestão de Palavras-Chave Otimizadas</DialogTitle>
      <DialogContent sx={{ minHeight: 400, py: 4 }}>
        <Box sx={{ mb: 2 }}>
          <TextField select label="Categoria" value={categoria} onChange={e => setCategoria(e.target.value)} fullWidth sx={{ mb: 2 }}>
            {categorias.map(cat => (
              <MenuItem key={cat} value={cat}>{categoriaLabels[cat]}</MenuItem>
            ))}
          </TextField>
          <TextField label="Texto de Busca" value={textoBusca} onChange={e => setTextoBusca(e.target.value)} fullWidth sx={{ mb: 2 }} />
          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" sx={{ mb: 2, fontWeight: 600 }}>Excluir tags:</Typography>
            <FormControlLabel control={<Checkbox checked={excludedTags.includes('promoções')} onChange={() => handleTagChange('promoções')} />} label="promoções" />
            <FormControlLabel control={<Checkbox checked={excludedTags.includes('patrocinados')} onChange={() => handleTagChange('patrocinados')} />} label="patrocinados" />
            <FormControlLabel control={<Checkbox checked={excludedTags.includes('lojas oficiais')} onChange={() => handleTagChange('lojas oficiais')} />} label="lojas oficiais" />
          </Box>
          <Button variant="contained" color="primary" onClick={fetchKeywords} disabled={loading || !textoBusca} sx={{ mb: 2 }}>Buscar Sugestões</Button>
        </Box>
        {loading && <CircularProgress size={32} sx={{ mb: 2 }} />}
        {error && <Typography color="error" sx={{ mb: 2 }}>{error}</Typography>}
        {keywords.length > 0 && (
          <Box>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Selecione as palavras-chave:</Typography>
            <TextField select label="Título" value={selectedTitle} onChange={e => setSelectedTitle(e.target.value)} fullWidth sx={{ mb: 2 }}>
              {keywords.map((kw, idx) => <MenuItem key={idx} value={kw}>{kw}</MenuItem>)}
            </TextField>
            <TextField select label="Long Tail" value={selectedLongTail} onChange={e => setSelectedLongTail(e.target.value)} fullWidth sx={{ mb: 2 }}>
              {keywords.map((kw, idx) => <MenuItem key={idx} value={kw}>{kw}</MenuItem>)}
            </TextField>
            <TextField select label="Medium Tail" value={selectedMediumTail} onChange={e => setSelectedMediumTail(e.target.value)} fullWidth sx={{ mb: 2 }}>
              {keywords.map((kw, idx) => <MenuItem key={idx} value={kw}>{kw}</MenuItem>)}
            </TextField>
          </Box>
        )}
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 3 }}>
        <Button onClick={onClose} sx={{ fontSize: 18, px: 4 }}>Cancelar</Button>
        <Button variant="contained" color="primary" onClick={handleConfirm} sx={{ fontSize: 18, px: 4 }}>Selecionar</Button>
      </DialogActions>
    </Dialog>
  );
}
