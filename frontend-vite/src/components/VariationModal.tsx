import React, { useState } from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, TextField, Grid, Typography, Box } from "@mui/material";

interface VariationModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: VariationData) => void;
}

export interface VariationData {
  price: string;
  available_quantity: string;
  picture_urls: Array<{ url: string; file?: File }>;
  ean: string;
  seller_custom_field: string;
}

export default function VariationModal({ open, onClose, onSave }: VariationModalProps) {
  const [price, setPrice] = useState("");
  const [availableQuantity, setAvailableQuantity] = useState("");
  const [pictureUrls, setPictureUrls] = useState<Array<{ url: string; file?: File }>>([]);
  const [ean, setEan] = useState("");
  const [sellerCustom, setSellerCustom] = useState("");

  function handleAddImage(img: { url: string; file?: File }) {
    if (pictureUrls.length >= 10) return;
    setPictureUrls(prev => [...prev, img]);
  }
  function handleRemoveImage(idx: number) {
    setPictureUrls(prev => prev.filter((_, i) => i !== idx));
  }
  function handleClearImages() {
    setPictureUrls([]);
  }

  function handleSave() {
    onSave({
      price,
      available_quantity: availableQuantity,
      picture_urls: pictureUrls,
      ean,
      seller_custom_field: sellerCustom,
    });
    setPrice("");
    setAvailableQuantity("");
    setPictureUrls([]);
    setEan("");
    setSellerCustom("");
    onClose();
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>Adicionar Variação</DialogTitle>
      <DialogContent>
        <Grid container spacing={2}>
          <Grid xs={6}>
            <TextField label="Preço" type="number" value={price} onChange={e => setPrice(e.target.value)} fullWidth required />
          </Grid>
          <Grid xs={6}>
            <TextField label="Quantidade" type="number" value={availableQuantity} onChange={e => setAvailableQuantity(e.target.value)} fullWidth required />
          </Grid>
          <Grid xs={12}>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>Imagens do Produto</Typography>
            <Box sx={{ bgcolor: '#fff', borderRadius: 4, boxShadow: 1, p: 2, mb: 2, minWidth: 900 }}>
              <Grid container spacing={2} alignItems="center">
                {pictureUrls.map((img, idx) => (
                  <Grid xs={6} sm={1.2} key={idx} sx={{ position: 'relative' }}>
                    <Box sx={{ border: '2px solid #eee', borderRadius: 2, p: 1, bgcolor: '#fafafa', width: 90, height: 90, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                      <img src={img.url} alt={`Foto ${idx + 1}`} style={{ width: 80, height: 80, borderRadius: 4, objectFit: 'cover' }} />
                      {idx === 0 && (
                        <Typography variant="caption" sx={{ position: 'absolute', top: 4, left: 4, bgcolor: '#1976d2', color: '#fff', px: 1, borderRadius: 1, fontSize: 11 }}>Imagem de capa</Typography>
                      )}
                      {/* Ícone de lixeira no canto inferior direito */}
                      <Box sx={{ position: 'absolute', bottom: 4, right: 4 }}>
                        <Button size="small" color="error" sx={{ minWidth: 0, p: 0 }} onClick={() => handleRemoveImage(idx)}>
                          <span className="material-icons" style={{ fontSize: 18 }}>delete</span>
                        </Button>
                      </Box>
                    </Box>
                  </Grid>
                ))}
                {pictureUrls.length < 10 && (
                  <Grid xs={6} sm={1.2}>
                    <Box sx={{ border: '2px dashed #1976d2', borderRadius: 2, width: 90, height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', bgcolor: '#f0f7ff' }} onClick={() => {
                      const input = document.createElement('input');
                      input.type = 'file';
                      input.accept = 'image/*';
                      input.onchange = e => {
                        const file = (e.target as HTMLInputElement).files?.[0];
                        if (file) {
                          const reader = new FileReader();
                          reader.onload = (ev) => {
                            handleAddImage({ url: ev.target?.result as string, file });
                          };
                          reader.readAsDataURL(file);
                        }
                      };
                      input.click();
                    }}>
                      <Typography variant="h3" sx={{ color: '#1976d2', fontWeight: 700 }}>+</Typography>
                    </Box>
                  </Grid>
                )}
              </Grid>
              <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                <Button variant="outlined" color="error" size="small" onClick={handleClearImages} disabled={pictureUrls.length === 0}>Limpar todas</Button>
                <Typography variant="caption" sx={{ color: '#888' }}>Máximo 10 imagens. Arraste para reordenar.</Typography>
              </Box>
            </Box>
          </Grid>
          <Grid xs={6}>
            <TextField label="EAN" value={ean} onChange={e => setEan(e.target.value)} fullWidth />
          </Grid>
          <Grid xs={6}>
            <TextField label="Código Interno (seller_custom)" value={sellerCustom} onChange={e => setSellerCustom(e.target.value)} fullWidth />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancelar</Button>
        <Button onClick={handleSave} variant="contained" color="primary">Salvar</Button>
      </DialogActions>
    </Dialog>
  );
}
