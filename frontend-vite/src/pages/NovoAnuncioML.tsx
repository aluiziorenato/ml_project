import React, { useState } from "react";
import { Box, Grid, TextField, Button, Typography, MenuItem, Divider, Tooltip } from "@mui/material";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';

const categorias = ["MLB5726", "MLB1055", "MLB1430", "MLB1648", "MLB1071", "MLB1246", "MLB1743"];
const categoriaLabels = {
  "MLB5726": "Eletrônicos",
  "MLB1055": "Casa",
  "MLB1430": "Moda",
  "MLB1648": "Informática",
  "MLB1071": "Esportes",
  "MLB1246": "Veículos",
  "MLB1743": "Beleza"
};
const statusList = ["active", "paused", "closed"];
const fiscalTypes = ["Simples Nacional", "Lucro Presumido", "Lucro Real"];
const mockCategoryAttributes = {
  MLB5726: [
    { id: "brand", name: "Marca", required: true, type: "string" },
    { id: "model", name: "Modelo", required: true, type: "string" },
    { id: "voltage", name: "Voltagem", required: false, type: "list", allowed_values: ["110V", "220V", "Bivolt"] },
    { id: "color", name: "Cor", required: false, type: "string" },
    { id: "SKU", name: "SKU", required: false, type: "string" },
  ],
};

export default function NovoAnuncioML() {
  const [showKeywords, setShowKeywords] = useState<{ type: "title" | "description" | null, keywords: { word: string, score: number, tail?: 'long' | 'medium' }[] }>({ type: null, keywords: [] });
  const [selectedLong, setSelectedLong] = useState<string | null>(null);
  const [selectedMedium, setSelectedMedium] = useState<string | null>(null);
  const [form, setForm] = useState({
    title: "",
    category_id: categorias[0],
    price: "",
    currency_id: "BRL",
    available_quantity: "",
    status: "active",
    description: "",
    condition: "new",
    fiscal_type: "",
    ncm: "",
    cest: "",
    ean: "",
    brand: "",
    model: "",
    warranty: "",
    sku: "",
    pictures: [{ url: "" }],
    vendas: 120,
    visitas: 350,
  });
  const [variations, setVariations] = useState<any[]>([]);
  const [categoryAttributes, setCategoryAttributes] = useState<any[]>(mockCategoryAttributes[categorias[0]] || []);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }
  function handleCategoryChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { value } = e.target;
    setForm((prev) => ({ ...prev, category_id: value }));
    setCategoryAttributes(mockCategoryAttributes[value] ? [...mockCategoryAttributes[value]] : []);
  }
  function handleAttributeChange(attrId: string, value: string) {
    setForm((prev) => ({ ...prev, [attrId]: value }));
  }
  function addVariation() {
    setVariations((prev) => [...prev, { attributes: {}, price: '', available_quantity: '', picture_ids: [] }]);
  }
  function handleVariationChange(index: number, attrId: string, value: string) {
    setVariations((prev) => {
      const updated = [...prev];
      updated[index].attributes[attrId] = value;
      return updated;
    });
  }
  function handleVariationFieldChange(index: number, field: string, value: string) {
    setVariations((prev) => {
      const updated = [...prev];
      updated[index][field] = value;
      return updated;
    });
  }
  function optimize(field: "title" | "description") {
    if (field === "title") {
      setShowKeywords({
        type: field,
        keywords: [
          { word: "Novo", score: 0.98 },
          { word: "Original", score: 0.95 },
          { word: "Promoção", score: 0.93 },
          { word: "Garantia", score: 0.91 },
          { word: "Frete grátis", score: 0.89 }
        ]
      });
    } else {
      setShowKeywords({
        type: field,
        keywords: [
          // Long tail
          { word: "Capa protetora para notebook 15.6 polegadas resistente à água", score: 0.97, tail: 'long' },
          { word: "Bolsa térmica fitness com compartimento para marmita", score: 0.96, tail: 'long' },
          { word: "Fone bluetooth com cancelamento de ruído e microfone embutido", score: 0.95, tail: 'long' },
          { word: "Tênis esportivo masculino para corrida leve e confortável", score: 0.94, tail: 'long' },
          { word: "Relógio digital resistente à água com pulseira de silicone", score: 0.93, tail: 'long' },
          // Medium tail
          { word: "Bolsa térmica fitness", score: 0.92, tail: 'medium' },
          { word: "Fone bluetooth com microfone", score: 0.91, tail: 'medium' },
          { word: "Tênis esportivo masculino", score: 0.90, tail: 'medium' },
          { word: "Relógio digital resistente à água", score: 0.89, tail: 'medium' },
          { word: "Capa protetora para notebook", score: 0.88, tail: 'medium' }
        ]
      });
      setSelectedLong(null);
      setSelectedMedium(null);
    }
  }
  function handleKeywordSelect(keyword: string) {
    setSelectedKeywords((prev) =>
      prev.includes(keyword)
        ? prev.filter((k) => k !== keyword)
        : [...prev, keyword]
    );
  }
  function applyKeywords() {
    if (showKeywords.type === "title") {
      setForm((prev) => ({ ...prev, title: prev.title + " " + selectedKeywords.join(" ") }));
    } else if (showKeywords.type === "description") {
      setForm((prev) => ({ ...prev, description: prev.description + " " + selectedKeywords.join(" ") }));
    }
    setShowKeywords({ type: null, keywords: [] });
    setSelectedKeywords([]);
  }
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    alert("Anúncio salvo com sucesso!");
  }
  return (
    <Box sx={{ maxWidth: 900, mx: "auto", mt: 4, p: 0, bgcolor: "#f7f7f7", borderRadius: 4, boxShadow: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700, color: '#333', letterSpacing: 1, p: 3 }}>Novo Anúncio Mercado Livre</Typography>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 8, padding: 0, boxShadow: '0 4px 16px #e0e0e0', display: 'flex', flexDirection: 'column', gap: 32 }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'center', gap: 3, px: 2, pt: 2 }}>
          <Typography variant="body2" sx={{ color: '#1976d2', fontWeight: 500 }}>Vendas: {form.vendas ?? 0}</Typography>
          <Typography variant="body2" sx={{ color: '#388e3c', fontWeight: 500 }}>Visitas: {form.visitas ?? 0}</Typography>
        </Box>
        {/* Seção: Fotos do Produto */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Fotos do Produto</Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid item xs={12} sm={8}>
              <TextField label="URL da Foto Principal" name="pictures[0].url" value={form.pictures[0].url} onChange={handleChange} fullWidth helperText="Cole o link da imagem do produto." />
            </Grid>
            <Grid item xs={12} sm={4}>
              <Button variant="outlined" size="small" sx={{ fontSize: 12, mt: 1 }} startIcon={<AutoFixHighIcon />}>Ler imagem para otimizar título</Button>
            </Grid>
          </Grid>
        </Box>
        {/* Seção: Dados Principais */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 0.5, fontWeight: 600, color: '#0057b8', fontSize: 18, mt: -1 }}>Dados Principais</Typography>
          <Grid container spacing={3} alignItems="flex-start">
            <Grid item xs={12} sm={6}>
              <Box sx={{ position: 'relative', mb: 2 }}>
                <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('title')}>
                  <AutoFixHighIcon sx={{ color: '#1976d2', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 600 }}>Otimizar</Typography>
                </Box>
                <TextField label="Título" name="title" value={form.title} onChange={handleChange} required fullWidth helperText="Máximo 60 caracteres. Dica: use palavras como 'Novo', 'Original', 'Promoção', 'Garantia', 'Frete grátis' para otimizar o título." inputProps={{ maxLength: 60 }} />
              </Box>
              <TextField select label="Categoria" name="category_id" value={form.category_id} onChange={handleCategoryChange} fullWidth required helperText="Escolha a categoria." sx={{ mb: 2 }}>
                {categorias.map((cat) => <MenuItem key={cat} value={cat}>{categoriaLabels[cat]}</MenuItem>)}
              </TextField>
              <Grid container spacing={2} alignItems="center">
                <Grid item xs={6}>
                  <TextField label="Preço" name="price" type="number" value={form.price} onChange={handleChange} fullWidth required helperText="Valor do produto." />
                </Grid>
                <Grid item xs={6}>
                  <TextField select label="Status" name="status" value={form.status} onChange={handleChange} fullWidth helperText="Status do anúncio.">
                    {statusList.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </TextField>
                </Grid>
              </Grid>
            </Grid>
            <Grid item xs={12} sm={12} sx={{ position: 'relative' }}>
              <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('description')}>
                <AutoFixHighIcon sx={{ color: '#1976d2', fontSize: 20, mr: 0.5 }} />
                <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 600 }}>Otimizar</Typography>
              </Box>
      {/* Card lateral de sugestões */}
      {showKeywords.type && showKeywords.keywords.length > 0 && (
        <Box sx={{ position: 'fixed', top: 100, right: 40, width: 370, maxHeight: 420, overflowY: 'auto', bgcolor: '#fff', borderRadius: 3, boxShadow: 4, p: 3, zIndex: 10 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1976d2', mb: 2 }}>
            Sugestões para {showKeywords.type === 'title' ? 'Título' : 'Descrição'}
          </Typography>
          {showKeywords.type === 'description' ? (
            <>
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#333', mb: 1 }}>Long tail</Typography>
              {showKeywords.keywords.filter(kw => kw.tail === 'long').map((kw) => (
                <Box key={kw.word} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, p: 1, borderRadius: 2, bgcolor: selectedLong === kw.word ? '#bbdefb' : '#e3f2fd', cursor: 'pointer' }} onClick={() => setSelectedLong(kw.word)}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{kw.word}</Typography>
                  <Typography variant="caption" sx={{ color: '#00a650', fontWeight: 700 }}>Índice: {kw.score.toFixed(2)}</Typography>
                </Box>
              ))}
              <Divider sx={{ my: 2 }} />
              <Typography variant="body2" sx={{ fontWeight: 700, color: '#333', mb: 1 }}>Medium tail</Typography>
              {showKeywords.keywords.filter(kw => kw.tail === 'medium').map((kw) => (
                <Box key={kw.word} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, p: 1, borderRadius: 2, bgcolor: selectedMedium === kw.word ? '#bbdefb' : '#f5f5f5', cursor: 'pointer' }} onClick={() => setSelectedMedium(kw.word)}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{kw.word}</Typography>
                  <Typography variant="caption" sx={{ color: '#00a650', fontWeight: 700 }}>Índice: {kw.score.toFixed(2)}</Typography>
                </Box>
              ))}
              <Button variant="contained" size="small" sx={{ mt: 2 }} disabled={!selectedLong || !selectedMedium} onClick={() => {
                setForm((prev) => ({ ...prev, description: prev.description + ' ' + selectedLong + ' ' + selectedMedium }));
                setShowKeywords({ type: null, keywords: [] });
                setSelectedLong(null);
                setSelectedMedium(null);
              }}>Aplicar</Button>
            </>
          ) : (
            <>
              {showKeywords.keywords.map((kw, idx) => (
                <Box key={kw.word} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1, p: 1, borderRadius: 2, bgcolor: idx % 2 === 0 ? '#e3f2fd' : '#f5f5f5' }}>
                  <Typography variant="body2" sx={{ fontWeight: 500 }}>{kw.word}</Typography>
                  <Typography variant="caption" sx={{ color: '#00a650', fontWeight: 700 }}>Índice: {kw.score.toFixed(2)}</Typography>
                </Box>
              ))}
              <Button variant="outlined" size="small" sx={{ mt: 2 }} onClick={() => setShowKeywords({ type: null, keywords: [] })}>Fechar</Button>
            </>
          )}
        </Box>
      )}
              <TextField
                label="Descrição"
                name="description"
                value={form.description}
                onChange={handleChange}
                multiline
                rows={12}
                fullWidth
                helperText="Máximo 500 caracteres. Dica: use termos como 'Alta qualidade', 'Entrega rápida', 'Produto exclusivo', 'Desconto especial', 'Suporte 24h' para otimizar a descrição."
                inputProps={{ maxLength: 500 }}
                sx={{ minHeight: 300, height: '100%', mt: 0, fontSize: 16 }}
              />
            </Grid>
          </Grid>
        </Box>
        {/* Seção: Ficha Técnica */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Ficha Técnica</Typography>
          <Grid container spacing={3}>
            {categoryAttributes.map(attr => (
              <Grid item xs={12} sm={4} key={attr.id}>
                {attr.type === "list" ? (
                  <TextField select label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id] || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'}>
                    {attr.allowed_values.map(val => <MenuItem key={val} value={val}>{val}</MenuItem>)}
                  </TextField>
                ) : (
                  <TextField label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id] || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'} />
                )}
              </Grid>
            ))}
          </Grid>
        </Box>
        {/* Seção: Dados Fiscais */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Dados Fiscais</Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField select label="Tipo Fiscal" name="fiscal_type" value={form.fiscal_type} onChange={handleChange} fullWidth helperText="Regime tributário.">
                {fiscalTypes.map((f) => <MenuItem key={f} value={f}>{f}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField label="NCM" name="ncm" value={form.ncm} onChange={handleChange} fullWidth helperText="NCM do produto." />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField label="CEST" name="cest" value={form.cest} onChange={handleChange} fullWidth helperText="CEST do produto." />
            </Grid>
            <Grid item xs={12} sm={2}>
              <TextField label="EAN" name="ean" value={form.ean} onChange={handleChange} fullWidth helperText="Código de barras (EAN)." />
            </Grid>
          </Grid>
        </Box>
        {/* Seção: Variações */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Variações</Typography>
          {variations.map((variation, idx) => (
            <Box key={idx} sx={{ mb: 3, p: 3, bgcolor: '#e3f2fd', borderRadius: 3, boxShadow: 2 }}>
              <Grid container spacing={3}>
                {categoryAttributes.filter(attr => attr.allowed_values).map(attr => (
                  <Grid item xs={12} sm={3} key={attr.id}>
                    <TextField select label={attr.name} value={variation.attributes[attr.id] || ''} onChange={e => handleVariationChange(idx, attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'}>
                      {attr.allowed_values.map(val => <MenuItem key={val} value={val}>{val}</MenuItem>)}
                    </TextField>
                  </Grid>
                ))}
                <Grid item xs={12} sm={2}>
                  <TextField label="Preço" type="number" value={variation.price || ''} onChange={e => handleVariationFieldChange(idx, 'price', e.target.value)} fullWidth required helperText="Preço da variação" />
                </Grid>
                <Grid item xs={12} sm={2}>
                  <TextField label="Quantidade" type="number" value={variation.available_quantity || ''} onChange={e => handleVariationFieldChange(idx, 'available_quantity', e.target.value)} fullWidth required helperText="Qtd. disponível" />
                </Grid>
                <Grid item xs={12} sm={3}>
                  <TextField label="Fotos (IDs)" value={variation.picture_ids.join(', ')} onChange={e => handleVariationFieldChange(idx, 'picture_ids', e.target.value.split(',').map(s => s.trim()))} fullWidth helperText="IDs das fotos" />
                </Grid>
              </Grid>
            </Box>
          ))}
          <Button variant="contained" color="primary" size="medium" sx={{ mb: 3, fontWeight: 600, bgcolor: '#0057b8', borderRadius: 2 }} onClick={addVariation}>Adicionar Variação</Button>
        </Box>
        {/* Botão de Salvar */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1, textAlign: 'center' }}>
          <Button variant="contained" color="primary" type="submit" sx={{ fontWeight: 700, mt: 3, bgcolor: '#00a650', fontSize: 16, borderRadius: 2, boxShadow: '0 2px 8px #b2dfdb', mr: 2 }}>Salvar Anúncio</Button>
          <Button variant="contained" color="primary" sx={{ fontWeight: 700, mt: 3, bgcolor: '#1976d2', fontSize: 16, borderRadius: 2, boxShadow: '0 2px 8px #b2dfdb' }} onClick={() => alert('Anúncio enviado para o Mercado Livre!')}>Enviar para Mercado Livre</Button>
        </Box>
      </form>
    </Box>
  );
}
// ...existing code...
