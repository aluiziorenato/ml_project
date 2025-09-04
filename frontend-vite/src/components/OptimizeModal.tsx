import React, { useEffect, useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Typography,
  Box,
  Grid,
  Alert,
} from "@mui/material";

interface OptimizeModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  categoryId: string;
}

export default function OptimizeModal({ open, onClose, title, categoryId }: OptimizeModalProps) {
  const [seoLoading, setSeoLoading] = useState(false);
  const [seoError, setSeoError] = useState<string | null>(null);
  const [seoResults, setSeoResults] = useState<{
    titles: string[];
    longTail: string[];
    mediumTail: string[];
  }>({ titles: [], longTail: [], mediumTail: [] });
  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);
  const [selectedLongTail, setSelectedLongTail] = useState<string[]>([]);
  const [selectedMediumTail, setSelectedMediumTail] = useState<string[]>([]);
  const [optimizerLoading, setOptimizerLoading] = useState(false);
  const [optimizerResult, setOptimizerResult] = useState<{ title: string; description: string } | null>(null);

  useEffect(() => {
    if (!open) return;
    setSeoLoading(true);
    setSeoError(null);
    setSeoResults({ titles: [], longTail: [], mediumTail: [] });
    setSelectedTitles([]);
    setSelectedLongTail([]);
    setSelectedMediumTail([]);
    setOptimizerResult(null);
    fetch("/api/seo-intelligence", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        category: categoryId,
        limit: 200,
      }),
    })
      .then((res) => res.json())
      .then((data) => {
        setSeoResults({
          titles: data.titles || [],
          longTail: data.long_tail || [],
          mediumTail: data.medium_tail || [],
        });
      })
      .catch(() => setSeoError("Erro ao buscar sugestões da IA SEO Intelligence."))
      .finally(() => setSeoLoading(false));
  }, [open, title, categoryId]);

  async function handleOptimizeAI() {
    setOptimizerLoading(true);
    setOptimizerResult(null);
    try {
      const res = await fetch("/api/optimizer-ai", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          selected_titles: selectedTitles,
          selected_long_tail: selectedLongTail,
          selected_medium_tail: selectedMediumTail,
          category: categoryId,
        }),
      });
      const data = await res.json();
      setOptimizerResult({
        title: data.suggested_title,
        description: data.suggested_description,
      });
    } catch {
      setSeoError("Erro ao otimizar com IA Optimizer.");
    } finally {
      setOptimizerLoading(false);
    }
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Otimizar título e descrição com IA</DialogTitle>
      <DialogContent>
        {seoLoading ? (
          <Typography variant="body1">Buscando sugestões da IA SEO Intelligence...</Typography>
        ) : seoError ? (
          <Alert severity="error">{seoError}</Alert>
        ) : optimizerResult ? (
          <Box>
            <Typography variant="h6" color="primary" sx={{ mb: 2 }}>
              Sugestão final da IA
            </Typography>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Título sugerido:
            </Typography>
            <Alert severity="success" sx={{ mb: 2 }}>
              {optimizerResult.title}
            </Alert>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>
              Descrição sugerida:
            </Typography>
            <Alert severity="info">{optimizerResult.description}</Alert>
          </Box>
        ) : (
          <Box>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>
              Selecione 2 títulos, 2 long tail e 2 medium tail para otimização:
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Títulos sugeridos:</Typography>
              <Grid container spacing={1}>
                {seoResults.titles.map((t) => (
                  <Grid item key={t} xs={6} md={4}>
                    <Button
                      variant={selectedTitles.includes(t) ? "contained" : "outlined"}
                      color="primary"
                      fullWidth
                      onClick={() => {
                        setSelectedTitles((sel) =>
                          sel.includes(t)
                            ? sel.filter((x) => x !== t)
                            : sel.length < 2
                            ? [...sel, t]
                            : sel
                        );
                      }}
                      disabled={!selectedTitles.includes(t) && selectedTitles.length >= 2}
                      sx={{ mb: 1 }}
                    >
                      {t}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Long tail:</Typography>
              <Grid container spacing={1}>
                {seoResults.longTail.map((t) => (
                  <Grid item key={t} xs={6} md={4}>
                    <Button
                      variant={selectedLongTail.includes(t) ? "contained" : "outlined"}
                      color="secondary"
                      fullWidth
                      onClick={() => {
                        setSelectedLongTail((sel) =>
                          sel.includes(t)
                            ? sel.filter((x) => x !== t)
                            : sel.length < 2
                            ? [...sel, t]
                            : sel
                        );
                      }}
                      disabled={!selectedLongTail.includes(t) && selectedLongTail.length >= 2}
                      sx={{ mb: 1 }}
                    >
                      {t}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2">Medium tail:</Typography>
              <Grid container spacing={1}>
                {seoResults.mediumTail.map((t) => (
                  <Grid item key={t} xs={6} md={4}>
                    <Button
                      variant={selectedMediumTail.includes(t) ? "contained" : "outlined"}
                      color="success"
                      fullWidth
                      onClick={() => {
                        setSelectedMediumTail((sel) =>
                          sel.includes(t)
                            ? sel.filter((x) => x !== t)
                            : sel.length < 2
                            ? [...sel, t]
                            : sel
                        );
                      }}
                      disabled={!selectedMediumTail.includes(t) && selectedMediumTail.length >= 2}
                      sx={{ mb: 1 }}
                    >
                      {t}
                    </Button>
                  </Grid>
                ))}
              </Grid>
            </Box>
            <Button
              variant="contained"
              color="primary"
              disabled={
                selectedTitles.length !== 2 ||
                selectedLongTail.length !== 2 ||
                selectedMediumTail.length !== 2 ||
                optimizerLoading
              }
              onClick={handleOptimizeAI}
            >
              {optimizerLoading
                ? "Otimizando..."
                : "Gerar título e descrição otimizados"}
            </Button>
          </Box>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="primary">
          Fechar
        </Button>
      </DialogActions>
    </Dialog>
  );
}
