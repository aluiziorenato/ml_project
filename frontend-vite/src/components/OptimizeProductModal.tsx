import React, { useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, CircularProgress, Typography } from "@mui/material";

interface OptimizeProductModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  categoryId: string;
  productData: any;
}

export default function OptimizeProductModal({ open, onClose, title, categoryId, productData }: OptimizeProductModalProps) {
  const [loading, setLoading] = useState(false);
  const [seoResult, setSeoResult] = useState<any>(null);
  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [optimized, setOptimized] = useState<any>(null);

  // Fluxo simplificado: busca SEO, seleção, otimização
  const handleStart = async () => {
    setLoading(true);
    // 1. Chama backend para sugestões SEO
    const res = await fetch("/api/optimize-product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title, category_id: categoryId, product_data: productData })
    });
    const data = await res.json();
    setSeoResult(data.seo);
    setLoading(false);
  };

  const handleOptimize = async () => {
    setLoading(true);
    // 2. Chama backend para otimização final
    const res = await fetch("/api/optimize-product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title,
        category_id: categoryId,
        product_data: productData,
        selected_titles: selectedTitles,
        selected_keywords: selectedKeywords
      })
    });
    const data = await res.json();
    setOptimized(data.optimized);
    setLoading(false);
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Otimizar anúncio com IA</DialogTitle>
      <DialogContent>
        {loading && <CircularProgress />}
        {!loading && !seoResult && (
          <Button variant="contained" onClick={handleStart}>Buscar sugestões SEO</Button>
        )}
        {!loading && seoResult && !optimized && (
          <>
            <Typography variant="subtitle1">Sugestões de títulos:</Typography>
            {seoResult.titles.map((t: string) => (
              <Button key={t} onClick={() => setSelectedTitles([t])} variant={selectedTitles.includes(t) ? "contained" : "outlined"} sx={{ m: 1 }}>{t}</Button>
            ))}
            <Typography variant="subtitle1">Palavras-chave long tail:</Typography>
            {seoResult.long_tail.map((k: string) => (
              <Button key={k} onClick={() => setSelectedKeywords([k])} variant={selectedKeywords.includes(k) ? "contained" : "outlined"} sx={{ m: 1 }}>{k}</Button>
            ))}
            <Button variant="contained" onClick={handleOptimize} sx={{ mt: 2 }}>Otimizar anúncio</Button>
          </>
        )}
        {!loading && optimized && (
          <>
            <Typography variant="h6">Título otimizado:</Typography>
            <Typography>{optimized.title}</Typography>
            <Typography variant="h6" sx={{ mt: 2 }}>Descrição otimizada:</Typography>
            <Typography>{optimized.description}</Typography>
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fechar</Button>
      </DialogActions>
    </Dialog>
  );
}
