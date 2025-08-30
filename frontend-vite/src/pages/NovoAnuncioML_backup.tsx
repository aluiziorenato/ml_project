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
type CategoryAttribute = {
  id: string;
  name: string;
  required: boolean;
  type: string;
  allowed_values?: string[];
};
const mockCategoryAttributes: Record<string, CategoryAttribute[]> = {
  MLB5726: [
    { id: "brand", name: "Marca", required: true, type: "string" },
    { id: "model", name: "Modelo", required: true, type: "string" },
    { id: "voltage", name: "Voltagem", required: false, type: "list", allowed_values: ["110V", "220V", "Bivolt"] },
    { id: "color", name: "Cor", required: false, type: "string" },
    { id: "SKU", name: "SKU", required: false, type: "string" },
  ],
};

export default function NovoAnuncioML() {
  const [semanticIa, setSemanticIa] = useState<{ texto: string; keywords: string[]; recomendacoes: string[] } | null>(null);
  const [semanticLoading, setSemanticLoading] = useState(false);
  const [semanticError, setSemanticError] = useState<string | null>(null);
  const [showSemanticCard, setShowSemanticCard] = useState(false);
  const [seoIa, setSeoIa] = useState<any>(null);
  const [seoLoading, setSeoLoading] = useState(false);
  const [seoError, setSeoError] = useState<string | null>(null);
  const [showSeoCard, setShowSeoCard] = useState(false);
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
  const [categoryAttributes, setCategoryAttributes] = useState<CategoryAttribute[]>(mockCategoryAttributes[categorias[0]] || []);

  async function fetchSemanticIa(texto: string) {
    setSemanticLoading(true);
    setSemanticError(null);
    try {
      const res = await fetch("/api/semantic_intelligence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
      });
      if (!res.ok) throw new Error("Erro ao consultar IA Semântica");
      const data = await res.json();
      setSemanticIa(data);
      setShowSemanticCard(true);
    } catch (err) {
      setSemanticError("Falha ao buscar sugestão semântica: " + (err instanceof Error ? err.message : String(err)));
      setSemanticIa(null);
      setShowSemanticCard(true);
    } finally {
      setSemanticLoading(false);
    }
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
    if (name === "title") {
      if (value.length > 0) {
        fetchSemanticIa(value);
      } else {
        setShowSemanticCard(false);
      }
    }
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
  async function optimize(field: "title" | "description") {
    setSeoLoading(true);
    setSeoError(null);
    try {
      const res = await fetch("/api/seo_intelligence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          texto: field === "title" ? form.title : form.description,
          tipo: field
        })
      });
      if (!res.ok) throw new Error("Erro ao consultar IA SEO");
      const data = await res.json();
      setSeoIa(data);
      setShowSeoCard(true);
    } catch (err) {
      setSeoError("Falha ao buscar sugestão SEO: " + (err instanceof Error ? err.message : String(err)));
      setSeoIa(null);
      setShowSeoCard(true);
    } finally {
      setSeoLoading(false);
    }
  }
  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    alert("Anúncio salvo com sucesso!");
  }
  return (
    <Box sx={{ maxWidth: 700, ml: 4, mr: 'auto', mt: 4, p: 0, bgcolor: "#f7f7f7", borderRadius: 4, boxShadow: 3 }}>
      <Typography variant="h4" sx={{ mb: 3, fontWeight: 700, color: '#333', letterSpacing: 1, p: 3 }}>Novo Anúncio Mercado Livre</Typography>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 8, padding: 0, boxShadow: '0 4px 16px #e0e0e0', display: 'flex', flexDirection: 'column', gap: 32 }}>
        {/* Card lateral IA SEO Intelligence */}
        {showSeoCard && (
          <Box sx={{ position: 'fixed', top: 100, right: 40, width: 370, maxHeight: 420, overflowY: 'auto', bgcolor: '#fff', borderRadius: 3, boxShadow: 4, p: 3, zIndex: 10 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#00a650', mb: 2 }}>
              Sugestão SEO Intelligence
            </Typography>
            {seoLoading && <Typography variant="body2" sx={{ color: '#888' }}>Carregando...</Typography>}
            {seoError && <Typography variant="body2" sx={{ color: 'red', mb: 2 }}>{seoError}</Typography>}
            {seoIa && (
              <>
                {seoIa.texto && <Typography variant="body2" sx={{ fontWeight: 600, color: '#333', mb: 2 }}>{seoIa.texto}</Typography>}
                {seoIa.keywords && seoIa.keywords.length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    {seoIa.keywords.map((kw: string, idx: number) => (
                      <Button key={idx} variant="outlined" color="primary" sx={{ mb: 1, fontWeight: 600 }}>{kw}</Button>
                    ))}
                  </Box>
                )}
                {typeof seoIa.seo_score === 'number' && (
                  <Typography variant="body2" sx={{ color: '#00a650', fontWeight: 700, mb: 2 }}>Score SEO: {seoIa.seo_score}/10</Typography>
                )}
                {seoIa.recomendacoes && seoIa.recomendacoes.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 700, mb: 1 }}>Recomendações:</Typography>
                    {seoIa.recomendacoes.map((rec: string, idx: number) => (
                      <Button key={idx} variant="text" color="secondary" sx={{ mr: 1, mb: 1 }}>{rec}</Button>
                    ))}
                  </Box>
                )}
              </>
            )}
          </Box>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'flex-start', alignItems: 'center', gap: 3, px: 2, pt: 2 }}>
          <Typography variant="body2" sx={{ color: '#1976d2', fontWeight: 500 }}>Vendas: {form.vendas ?? 0}</Typography>
          <Typography variant="body2" sx={{ color: '#388e3c', fontWeight: 500 }}>Visitas: {form.visitas ?? 0}</Typography>
        </Box>
        {/* Card lateral IA Semântica */}
        {showSemanticCard && (
          <Box sx={{ position: 'fixed', top: 100, right: 40, width: 370, maxHeight: 420, overflowY: 'auto', bgcolor: '#fff', borderRadius: 3, boxShadow: 4, p: 3, zIndex: 10 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, color: '#1976d2', mb: 2 }}>
              Sugestão Semântica para o Título
            </Typography>
            {semanticLoading && <Typography variant="body2" sx={{ color: '#888' }}>Carregando...</Typography>}
            {semanticError && <Typography variant="body2" sx={{ color: 'red', mb: 2 }}>{semanticError}</Typography>}
            {semanticIa && (
              <>
                {semanticIa.texto && <Typography variant="body2" sx={{ fontWeight: 600, color: '#333', mb: 2 }}>{semanticIa.texto}</Typography>}
                {semanticIa.keywords && semanticIa.keywords.length > 0 && (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                    {semanticIa.keywords.map((kw: string, idx: number) => (
                      <Button key={idx} variant="outlined" color="primary" sx={{ mb: 1, fontWeight: 600 }}>{kw}</Button>
                    ))}
                  </Box>
                )}
                {semanticIa.recomendacoes && semanticIa.recomendacoes.length > 0 && (
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: 700, mb: 1 }}>Recomendações:</Typography>
                    {semanticIa.recomendacoes.map((rec: string, idx: number) => (
                      <Button key={idx} variant="text" color="secondary" sx={{ mr: 1, mb: 1 }}>{rec}</Button>
                    ))}
                  </Box>
                )}
              </>
            )}
          </Box>
        )}
        {/* Seção: Fotos do Produto */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Fotos do Produto</Typography>
          <Grid container spacing={3} alignItems="center">
            <Grid xs={12} sm={8}>
              <TextField label="URL da Foto Principal" name="pictures[0].url" value={form.pictures[0].url} onChange={handleChange} fullWidth helperText="Cole o link da imagem do produto." />
            </Grid>
            <Grid xs={12} sm={4}>
              <Button variant="outlined" size="small" sx={{ fontSize: 12, mt: 1 }} startIcon={<AutoFixHighIcon />}>Ler imagem para otimizar título</Button>
            </Grid>
          </Grid>
        </Box>
        {/* Seção: Dados Principais */}
        <Box sx={{ p: 3, mb: 3, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 0.5, fontWeight: 600, color: '#0057b8', fontSize: 18, mt: -1 }}>Dados Principais</Typography>
          <Grid container spacing={3} alignItems="flex-start">
            <Grid xs={12} sm={6}>
              <Box sx={{ position: 'relative', mb: 2 }}>
                <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('title')}>
                  <AutoFixHighIcon sx={{ color: '#1976d2', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 600 }}>Otimizar</Typography>
                </Box>
                <TextField label="Título" name="title" value={form.title} onChange={handleChange} required fullWidth helperText="Máximo 60 caracteres. Dica: use palavras como 'Novo', 'Original', 'Promoção', 'Garantia', 'Frete grátis' para otimizar o título." inputProps={{ maxLength: 60 }} />
              </Box>
              <TextField select label="Categoria" name="category_id" value={form.category_id} onChange={handleCategoryChange} fullWidth required helperText="Escolha a categoria." sx={{ mb: 2 }}>
                {categorias.map((cat) => <MenuItem key={cat} value={cat}>{categoriaLabels[cat as keyof typeof categoriaLabels]}</MenuItem>)}
              </TextField>
              <Grid container spacing={2} alignItems="center">
                <Grid xs={6}>
                  <TextField label="Preço" name="price" type="number" value={form.price} onChange={handleChange} fullWidth required helperText="Valor do produto." />
                </Grid>
                <Grid xs={6}>
                  <TextField select label="Status" name="status" value={form.status} onChange={handleChange} fullWidth helperText="Status do anúncio.">
                    {statusList.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </TextField>
                </Grid>
              </Grid>
            </Grid>
            <Grid xs={12} sm={12} sx={{ position: 'relative' }}>
              <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('description')}>
                <AutoFixHighIcon sx={{ color: '#1976d2', fontSize: 20, mr: 0.5 }} />
                <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 600 }}>Otimizar</Typography>
              </Box>
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
            {categoryAttributes.map((attr) => (
              <Grid xs={12} sm={4} key={attr.id}>
                {attr.type === "list" ? (
                  <TextField select label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id as keyof typeof form] as string || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'}>
                    {attr.allowed_values?.map((val: string) => <MenuItem key={val} value={val}>{val}</MenuItem>)}
                  </TextField>
                ) : (
                  <TextField label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id as keyof typeof form] as string || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'} />
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
