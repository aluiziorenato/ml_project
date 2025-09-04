import {
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  TextField,
  Typography
} from "@mui/material";
import type React from "react";
import { useEffect, useState } from "react";
type Produto = {
  nome: string;
  categoria: string;
  status: string;
  preco: number;
  roi: number;
  sazonalidade: string;
  views: number;
  vendas: number;
  estoque: number;
  turnover: number;
  imagem?: string;
  attributes: Array<{ name: string; value: string }>;
};

interface EditProductModalProps {
	open: boolean;
	produto: Produto | null;
	onClose: () => void;
	onSave: (updated: Produto) => void;
}

const EditProductModal: React.FC<EditProductModalProps> = ({ open, produto, onClose, onSave }) => {
  const [form, setForm] = useState<Produto | null>(produto);
  const [attributes, setAttributes] = useState<Array<{ name: string; value: string }>>([]);

  useEffect(() => {
	setForm(produto);
	setAttributes(produto?.attributes || []);
  }, [produto]);

  if (!form) return null;

  const handleAttributeChange = (idx: number, field: "name" | "value", value: string) => {
	const updated = attributes.map((attr, i) => i === idx ? { ...attr, [field]: value } : attr);
	setAttributes(updated);
	setForm({ ...form, attributes: updated });
  };

  const handleAddAttribute = () => {
	const updated = [...attributes, { name: "", value: "" }];
	setAttributes(updated);
	setForm({ ...form, attributes: updated });
  };

  const handleRemoveAttribute = (idx: number) => {
	const updated = attributes.filter((_, i) => i !== idx);
	setAttributes(updated);
	setForm({ ...form, attributes: updated });
  };

  return (
	<Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
	  <DialogTitle sx={{ fontWeight: 700, fontSize: 22, pb: 0 }}>Cadastrar Produto</DialogTitle>
	  <DialogContent sx={{ pt: 2 }}>
		<Box component="form" sx={{ display: "flex", flexDirection: "column", gap: 3 }}>
		  {/* Dados principais */}
		  <Box sx={{ display: "flex", gap: 3 }}>
			<Box sx={{ flex: 1 }}>
			  <TextField label="Nome do Produto" placeholder="Ex: Smartphone XYZ" fullWidth value={form.nome || ""} onChange={e => setForm({ ...form, nome: e.target.value })} sx={{ mb: 2 }} />
			  <TextField label="Categoria" placeholder="Ex: Eletrônicos" fullWidth value={form.categoria || ""} onChange={e => setForm({ ...form, categoria: e.target.value })} sx={{ mb: 2 }} />
			  <TextField label="Status" placeholder="Ex: Ativo" fullWidth value={form.status || ""} onChange={e => setForm({ ...form, status: e.target.value })} sx={{ mb: 2 }} />
			</Box>
			<Box sx={{ flex: 1, display: "flex", flexDirection: "column", gap: 2 }}>
			  <TextField label="Preço" placeholder="Ex: 1999.99" type="number" fullWidth value={form.preco || ""} onChange={e => setForm({ ...form, preco: Number(e.target.value) })} />
			  <TextField label="ROI (%)" placeholder="Ex: 15" type="number" fullWidth value={form.roi || ""} onChange={e => setForm({ ...form, roi: Number(e.target.value) })} />
			  <TextField label="Sazonalidade" placeholder="Ex: Verão" fullWidth value={form.sazonalidade || ""} onChange={e => setForm({ ...form, sazonalidade: e.target.value })} />
			</Box>
		  </Box>
		  {/* Métricas */}
		  <Box sx={{ display: "flex", gap: 3 }}>
			<TextField label="Views" placeholder="Ex: 1200" type="number" fullWidth value={form.views || ""} onChange={e => setForm({ ...form, views: Number(e.target.value) })} />
			<TextField label="Vendas" placeholder="Ex: 300" type="number" fullWidth value={form.vendas || ""} onChange={e => setForm({ ...form, vendas: Number(e.target.value) })} />
			<TextField label="Estoque" placeholder="Ex: 50" type="number" fullWidth value={form.estoque || ""} onChange={e => setForm({ ...form, estoque: Number(e.target.value) })} />
			<TextField label="Turnover" placeholder="Ex: 2.5" type="number" fullWidth value={form.turnover || ""} onChange={e => setForm({ ...form, turnover: Number(e.target.value) })} />
		  </Box>
		  {/* Imagem */}
		  <Box sx={{ display: "flex", alignItems: "center", gap: 2, mt: 2 }}>
			<TextField label="Imagem (URL)" placeholder="Cole o link da imagem" fullWidth value={form.imagem || ""} onChange={e => setForm({ ...form, imagem: e.target.value })} />
			<Button variant="outlined" sx={{ height: 56 }}>Upload</Button>
		  </Box>
		  {/* Ficha Técnica */}
		  <Box sx={{ mt: 3 }}>
			<Typography variant="subtitle1" fontWeight={600} mb={1}>Ficha Técnica</Typography>
			{attributes.map((attr, idx) => (
		<Grid container spacing={1} alignItems="center" key={`${attr.name}-${attr.value}`}
		  sx={{ mb: 1 }}>
		  <Grid xs={5}>
			<TextField label="Atributo" placeholder="Ex: Cor" fullWidth value={attr.name} onChange={e => handleAttributeChange(idx, "name", e.target.value)} />
		  </Grid>
		  <Grid xs={5}>
			<TextField label="Valor" placeholder="Ex: Azul" fullWidth value={attr.value} onChange={e => handleAttributeChange(idx, "value", e.target.value)} />
		  </Grid>
		  <Grid xs={2}>
			<Button color="error" onClick={() => handleRemoveAttribute(idx)}>Remover</Button>
		  </Grid>
		</Grid>
			))}
			<Button variant="outlined" onClick={handleAddAttribute} sx={{ mt: 1 }}>Adicionar atributo</Button>
		  </Box>
		</Box>
	  </DialogContent>
	  <DialogActions sx={{ px: 3, pb: 2 }}>
		<Button onClick={onClose} sx={{ fontWeight: 600 }}>Cancelar</Button>
		<Button onClick={() => form && onSave(form)} variant="contained" sx={{ fontWeight: 600, minWidth: 120 }}>Salvar</Button>
	  </DialogActions>
	</Dialog>
  );
};

export default EditProductModal;

