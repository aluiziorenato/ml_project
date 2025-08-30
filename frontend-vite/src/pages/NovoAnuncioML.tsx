import React, { useState } from "react";
import { Box, TextField, Button, Typography, MenuItem, Divider, Tooltip } from "@mui/material";
import Grid from "@mui/material/Grid";
import AutoFixHighIcon from '@mui/icons-material/AutoFixHigh';
import KeywordSuggestionModal from "../components/KeywordSuggestionModal";
import VariationModal, { VariationData } from "../components/VariationModal";

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
const statusList = ["Ativo", "Pausado", "Finalizado"];
const tipoAnuncioList = ["Clássico", "Premium"];
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
  // Estado para abrir/fechar o modal de sugestão
  // Estado para modal de categoria
  const [openCategoryModal, setOpenCategoryModal] = useState(false);
  const [selectedCategoryPath, setSelectedCategoryPath] = useState<string[]>([]);
  const [openKeywordModal, setOpenKeywordModal] = useState(false);
  // Estado para armazenar seleção do modal
  const [selectedKeywords, setSelectedKeywords] = useState<{ title: string; longTail: string; mediumTail: string } | null>(null);
  const [semanticIa, setSemanticIa] = useState<{ texto: string; keywords: string[]; recomendacoes: string[]; titulos?: string[] } | null>(null);
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
    status: "Ativo",
    listing_type_id: "Clássico",
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
    pictures: [], // Agora armazena múltiplas imagens
  });
  // Estado para imagens do produto (cache local)
  const [productImages, setProductImages] = useState<Array<{ url: string; file?: File }>>([]);
  // Estado para modal de upload de imagens
  const [openImageModal, setOpenImageModal] = useState(false);
  // Função para adicionar imagem
  function handleAddImage(img: { url: string; file?: File }) {
    if (productImages.length >= 10) return;
    setProductImages(prev => [...prev, img]);
  }
  // Função para remover imagem
  function handleRemoveImage(idx: number) {
    setProductImages(prev => prev.filter((_, i) => i !== idx));
  }
  // Função para reordenar imagens (drag-and-drop)
  function handleReorderImages(newOrder: Array<{ url: string; file?: File }>) {
    setProductImages(newOrder);
  }
  // Função para limpar todas as imagens
  function handleClearImages() {
    setProductImages([]);
  }
  const [variations, setVariations] = useState<any[]>([]);
  const [openVariationModal, setOpenVariationModal] = useState(false);
  const [categoryAttributes, setCategoryAttributes] = useState<CategoryAttribute[]>(mockCategoryAttributes[categorias[0]] || []);

  async function fetchSemanticIa(texto: string) {
    setSemanticLoading(true);
    setSemanticError(null);
    try {
      const res = await fetch("/meli/questions_service/ai_suggestions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto })
      });
      if (!res.ok) throw new Error("Erro ao consultar IA Semântica");
      const data = await res.json();
      // Adapta o retorno para o formato esperado pelo card lateral
      setSemanticIa({
        texto: data.texto ?? "",
        keywords: Array.isArray(data.keywords) ? data.keywords : [],
        recomendacoes: Array.isArray(data.recomendacoes) ? data.recomendacoes : [],
        titulos: Array.isArray(data.titulos) ? data.titulos : []
      });
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
    setOpenVariationModal(true);
  }

  function handleSaveVariation(data: VariationData) {
    setVariations((prev) => [
      ...prev,
      {
        attributes: {},
        price: data.price,
        available_quantity: data.available_quantity,
        picture_ids: data.picture_urls.map(img => img.url),
        ean: data.ean,
        seller_custom_field: data.seller_custom_field,
      }
    ]);
    setOpenVariationModal(false);
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
  // Handler para receber seleção do modal
  async function handleKeywordSelect(selected: { title: string; longTail: string; mediumTail: string }) {
    setSelectedKeywords(selected);
    // Integração direta com IA SEO Intelligence
    setSeoLoading(true);
    setSeoError(null);
    try {
      const res = await fetch("/api/seo_intelligence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          keywords: [selected.title, selected.longTail, selected.mediumTail],
          tipo: "description"
        })
      });
      if (!res.ok) throw new Error("Erro ao consultar IA SEO Intelligence");
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
  return (
    <Box sx={{ maxWidth: 1000, mx: 'auto', mt: 2, p: 0, bgcolor: "#f7f7f7", borderRadius: 4, boxShadow: 3 }}>
      <Typography variant="h4" sx={{ mb: 2, fontWeight: 700, color: '#333', letterSpacing: 1, p: 3 }}>Novo Anúncio Mercado Livre</Typography>
      <form onSubmit={handleSubmit} style={{ background: '#fff', borderRadius: 8, padding: 0, boxShadow: '0 4px 16px #e0e0e0', display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* Exclusivo para cadastro de produtos: não exibe vendas nem visitas */}
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
        {semanticIa.titulos && semanticIa.titulos.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="body2" sx={{ fontWeight: 700, mb: 1 }}>Exemplos de títulos para Moda:</Typography>
                    <Box sx={{ maxHeight: 180, overflowY: 'auto', bgcolor: '#f5f5f5', borderRadius: 2, p: 2, boxShadow: 1 }}>
                      {semanticIa.titulos.map((titulo: string, idx: number) => (
                        <Typography key={idx} variant="body2" sx={{ color: '#333', mb: 0.5 }}>{idx + 1}. {titulo}</Typography>
                      ))}
                    </Box>
                  </Box>
                )}
              </>
            )}
          </Box>
        )}
        {/* Seção: Fotos do Produto */}
        <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Fotos do Produto</Typography>
          <Grid container spacing={2} alignItems="center">
            {/* Imagens já adicionadas */}
            {productImages.map((img, idx) => (
              <Grid item xs={6} sm={3} key={idx} sx={{ position: 'relative' }}>
                <Box sx={{ border: '2px solid #eee', borderRadius: 2, p: 1, bgcolor: '#fafafa', width: 90, height: 90, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', position: 'relative' }}>
                  <img src={img.url} alt={`Foto ${idx + 1}`} style={{ width: 80, height: 80, borderRadius: 4, objectFit: 'cover' }} />
                  {idx === 0 && (
                    <Typography variant="caption" sx={{ position: 'absolute', top: 4, left: 4, bgcolor: '#1976d2', color: '#fff', px: 1, borderRadius: 1, fontSize: 11 }}>Imagem de capa</Typography>
                  )}
                  <Button size="small" color="error" sx={{ mt: 1, fontSize: 12 }} onClick={() => handleRemoveImage(idx)}>Remover</Button>
                </Box>
              </Grid>
            ))}
            {/* Botão de adicionar imagem */}
            {productImages.length < 10 && (
              <Grid item xs={6} sm={3}>
                <Box sx={{ border: '2px dashed #1976d2', borderRadius: 2, width: 90, height: 90, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', bgcolor: '#f0f7ff' }} onClick={() => setOpenImageModal(true)}>
                  <Typography variant="h3" sx={{ color: '#1976d2', fontWeight: 700 }}>+</Typography>
                </Box>
              </Grid>
            )}
          </Grid>
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button variant="outlined" color="error" size="small" onClick={handleClearImages} disabled={productImages.length === 0}>Limpar todas</Button>
            <Typography variant="caption" sx={{ color: '#888' }}>Máximo 10 imagens. Arraste para reordenar.</Typography>
          </Box>
        </Box>
        {/* Modal de upload de imagens */}
        {openImageModal && (
          <Box sx={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', bgcolor: 'rgba(0,0,0,0.25)', zIndex: 1200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Box sx={{ width: 420, bgcolor: '#fff', borderRadius: 4, boxShadow: 6, p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
              <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, color: '#1976d2' }}>Adicionar Imagem</Typography>
              <input type="file" accept="image/*" style={{ marginBottom: 16 }} onChange={e => {
                const file = e.target.files?.[0];
                if (file) {
                  const reader = new FileReader();
                  reader.onload = (ev) => {
                    handleAddImage({ url: ev.target?.result as string, file });
                    setOpenImageModal(false);
                  };
                  reader.readAsDataURL(file);
                }
              }} />
              <Button variant="contained" color="secondary" onClick={() => setOpenImageModal(false)}>Fechar</Button>
              <Typography variant="caption" sx={{ color: '#888', mt: 1 }}>Primeira imagem será capa. Recomenda-se 1200x1200px.</Typography>
            </Box>
          </Box>
        )}
        {/* Seção: Dados Principais */}
        <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 0.5, fontWeight: 600, color: '#0057b8', fontSize: 18, mt: -1 }}>Dados Principais</Typography>
          <Grid container spacing={3} alignItems="flex-start">
            <Grid xs={12} sm={6}>
              {/* Frase e botão para seleção de categoria/subcategoria - AGORA ACIMA DO TÍTULO */}
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: 600, color: '#0057b8' }}>Selecione a categoria do seu produto</Typography>
                <Button variant="outlined" color="primary" sx={{ fontWeight: 600 }} onClick={() => setOpenCategoryModal(true)}>Selecionar Categoria</Button>
                {/* Aqui será exibida a subcategoria selecionada, se houver */}
                {selectedCategoryPath && selectedCategoryPath.length > 0 && (
                  <Typography variant="body2" sx={{ color: '#333', ml: 2 }}>
                    {selectedCategoryPath.join(' > ')}
                  </Typography>
                )}
              </Box>
              <Box sx={{ position: 'relative', mb: 2 }}>
                <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('title')}>
                  <AutoFixHighIcon sx={{ color: '#1976d2', fontSize: 20, mr: 0.5 }} />
                  <Typography variant="caption" sx={{ color: '#1976d2', fontWeight: 600 }} onClick={() => setOpenKeywordModal(true)}>Otimizar</Typography>
                </Box>
                <TextField label="Título" name="title" value={form.title} onChange={handleChange} required fullWidth helperText="Máximo 60 caracteres. Dica: use palavras como 'Novo', 'Original', 'Promoção', 'Garantia', 'Frete grátis' para otimizar o título." inputProps={{ maxLength: 60 }} />
              </Box>
              <Grid container spacing={2} alignItems="center">
                <Grid xs={4}>
                  <TextField label="Preço" name="price" type="number" value={form.price} onChange={handleChange} fullWidth required helperText="Valor do produto." />
                </Grid>
                <Grid xs={4}>
                  <TextField select label="Tipo de anúncio" name="listing_type_id" value={form.listing_type_id} onChange={handleChange} fullWidth required helperText="Escolha o tipo de anúncio.">
                    {tipoAnuncioList.map((tipo) => <MenuItem key={tipo} value={tipo}>{tipo}</MenuItem>)}
                  </TextField>
                </Grid>
                <Grid xs={4} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                  <TextField select label="Status" name="status" value={form.status} onChange={handleChange} fullWidth helperText="Status do anúncio.">
                    {statusList.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
                  </TextField>
                  <Button variant="contained" color="primary" size="small" sx={{ fontWeight: 600, bgcolor: '#0057b8', borderRadius: 2, ml: 1, mt: -2.5, minWidth: 140, px: 2, fontSize: 14, textTransform: 'none' }} onClick={addVariation}>Adicionar Variação</Button>
                </Grid>
              </Grid>
            </Grid>
            <Grid xs={12} sm={12} sx={{ position: 'relative' }}>
              <Box sx={{ position: 'absolute', top: -28, right: 0, display: 'flex', alignItems: 'center', cursor: 'pointer' }} onClick={() => optimize('description')}>
                  {/* Removido botão Otimizar da descrição, pois será gerada automaticamente */}
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
        <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Ficha Técnica</Typography>
          <Grid container spacing={3}>
            {categoryAttributes.map((attr) => (
              <Grid xs={12} sm={4} key={attr.id}>
                {attr.type === "list" ? (
                  <TextField select label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id as keyof typeof form] as string || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'}>
                    {(attr.allowed_values ?? []).map((val: string) => <MenuItem key={val} value={val}>{val}</MenuItem>)}
                  </TextField>
                ) : (
                  <TextField label={attr.name + (attr.required ? ' *' : '')} value={form[attr.id as keyof typeof form] as string || ''} onChange={e => handleAttributeChange(attr.id, e.target.value)} fullWidth required={attr.required} helperText={attr.required ? 'Obrigatório' : 'Opcional'} />
                )}
              </Grid>
            ))}
          </Grid>
        </Box>
        {/* Seção: Dados Fiscais */}
        <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
          <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: 600, color: '#0057b8', fontSize: 18 }}>Dados Fiscais</Typography>
          <Grid container spacing={2}>
            <Grid xs={12} sm={4}>
              <TextField select label="Tipo Fiscal" name="fiscal_type" value={form.fiscal_type} onChange={handleChange} fullWidth helperText="Regime tributário.">
                {fiscalTypes.map((f) => <MenuItem key={f} value={f}>{f}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid xs={12} sm={3}>
              <TextField label="NCM" name="ncm" value={form.ncm} onChange={handleChange} fullWidth helperText="NCM do produto." />
            </Grid>
            <Grid xs={12} sm={3}>
              <TextField label="CEST" name="cest" value={form.cest} onChange={handleChange} fullWidth helperText="CEST do produto." />
            </Grid>
            <Grid xs={12} sm={2}>
              <TextField label="EAN" name="ean" value={form.ean} onChange={handleChange} fullWidth helperText="Código de barras (EAN)." />
            </Grid>
          </Grid>
        </Box>
      {/* Seção: Variações */}
      <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1 }}>
        <Grid container spacing={2}>
          <Grid xs={12} sm={6}>
            <TextField
              label="Garantia"
              name="warranty"
              value={form.warranty}
              onChange={handleChange}
              fullWidth
              helperText="Exemplo: 3 meses, 1 ano, sem garantia."
            />
          </Grid>
          <Grid xs={12} sm={6}>
            <TextField
              label="Prazo de disponibilidade"
              name="availability_time"
              value={form.availability_time ?? ''}
              onChange={e => setForm(prev => ({ ...prev, availability_time: e.target.value }))}
              fullWidth
              helperText="Exemplo: Imediata, 2 dias, 1 semana."
            />
          </Grid>
        </Grid>
      </Box>
        {/* Botão de Salvar */}
        <Box sx={{ p: 2, mb: 2, bgcolor: '#fff', borderRadius: 4, boxShadow: 1, textAlign: 'center' }}>
          <Button variant="contained" color="primary" type="submit" sx={{ fontWeight: 700, mt: 3, bgcolor: '#00a650', fontSize: 16, borderRadius: 2, boxShadow: '0 2px 8px #b2dfdb', mr: 2 }}>Salvar Anúncio</Button>
          <Button variant="contained" color="primary" sx={{ fontWeight: 700, mt: 3, bgcolor: '#1976d2', fontSize: 16, borderRadius: 2, boxShadow: '0 2px 8px #b2dfdb' }} onClick={() => alert('Anúncio enviado para o Mercado Livre!')}>Enviar para Mercado Livre</Button>
        </Box>
      </form>
      {/* Modal de sugestão de palavras-chave */}
      <KeywordSuggestionModal
        open={openKeywordModal}
        onClose={() => setOpenKeywordModal(false)}
        categorias={categorias}
        categoriaLabels={categoriaLabels}
        onSelect={handleKeywordSelect}
      />
      {/* Modal de seleção de categoria/subcategoria */}
      {openCategoryModal && (
        <Box sx={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', bgcolor: 'rgba(0,0,0,0.25)', zIndex: 1300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <Box sx={{ width: 420, bgcolor: '#fff', borderRadius: 4, boxShadow: 6, p: 4, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
            <Typography variant="h6" sx={{ mb: 2, fontWeight: 700, color: '#1976d2' }}>Selecione a Categoria</Typography>
            {/* Lista de categorias principais */}
            {!selectedCategoryPath.length && (
              <>
                {categorias.map((cat) => (
                  <Button key={cat} variant="outlined" sx={{ mb: 1, width: '100%' }} onClick={() => setSelectedCategoryPath([categoriaLabels[cat]])}>
                    {categoriaLabels[cat]}
                  </Button>
                ))}
              </>
            )}
            {/* Exemplo de subcategoria (mock) */}
            {selectedCategoryPath.length === 1 && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Subcategorias de {selectedCategoryPath[0]}</Typography>
                {["Subcat 1", "Subcat 2", "Subcat 3"].map(sub => (
                  <Button key={sub} variant="outlined" sx={{ mb: 1, width: '100%' }} onClick={() => setSelectedCategoryPath([...selectedCategoryPath, sub])}>
                    {sub}
                  </Button>
                ))}
              </>
            )}
            {/* Exemplo de última subcategoria (mock) */}
            {selectedCategoryPath.length === 2 && (
              <>
                <Typography variant="subtitle2" sx={{ mb: 1 }}>Última subcategoria de {selectedCategoryPath[1]}</Typography>
                {["Final 1", "Final 2"].map(final => (
                  <Button key={final} variant="contained" color="primary" sx={{ mb: 1, width: '100%' }} onClick={() => {
                    setSelectedCategoryPath([...selectedCategoryPath, final]);
                    setOpenCategoryModal(false);
                  }}>
                    {final}
                  </Button>
                ))}
              </>
            )}
            <Button variant="text" color="error" sx={{ mt: 2 }} onClick={() => { setOpenCategoryModal(false); setSelectedCategoryPath([]); }}>Cancelar</Button>
          </Box>
        </Box>
      )}
      {/* Modal de variação */}
      <VariationModal
        open={openVariationModal}
        onClose={() => setOpenVariationModal(false)}
        onSave={handleSaveVariation}
      />
    </Box>
  );
}
// ...existing code...