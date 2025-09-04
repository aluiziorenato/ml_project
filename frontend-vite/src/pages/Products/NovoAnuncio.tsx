import PhotoCamera from "@mui/icons-material/PhotoCamera";
import Alert from "@mui/material/Alert";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import CardHeader from "@mui/material/CardHeader";
import Divider from "@mui/material/Divider";
import Grid from "@mui/material/Grid";
import IconButton from "@mui/material/IconButton";
import Snackbar from "@mui/material/Snackbar";
import TextField from "@mui/material/TextField";
import Tooltip from "@mui/material/Tooltip";
import Typography from "@mui/material/Typography";
import { useTheme } from "@mui/material/styles";
import { motion } from "framer-motion";
import type React from "react";
import { useEffect, useState } from "react";
import OptimizeProductModal from "./OptimizeProductModal";
import OptimizeDescriptionModal from "./OptimizeDescriptionModal";
import Stepper from '@mui/material/Stepper';
import Step from '@mui/material/Step';
import StepLabel from '@mui/material/StepLabel';

const _categorias = [
  { id: "MLB1234", nome: "Eletrônicos" },
  { id: "MLB5678", nome: "Moda" },
  // ...adicione mais categorias conforme necessário
];

const _condicoes = [
  { value: "new", label: "Novo" },
  { value: "used", label: "Usado" },
];

// Tipos para variações
interface VariationAttribute {
  name: string;
  value_name: string;
}
interface Variation {
  price: string;
  available_quantity: string;
  attributes: VariationAttribute[];
  pictures: string[];
  sku: string;
  ean: string;
}

interface NovoAnuncioProps {
  productId: string;
}

// Defina o tipo do formulário para evitar referência circular
type FormType = {
  title: string;
  category_id: string;
  price: string;
  available_quantity: string;
  buying_mode: string;
  listing_type_id: string;
  condition: string;
  description: string;
  video_id: string;
  warranty: string;
  pictures: (File | string)[];
  attributes: { name: string; value_name: string }[];
  sale_terms: { id: string; value_name: string }[];
  official_store_id: string;
  brand: string;
  model: string;
  sku: string;
  ean: string;
  color: string;
  size: string;
  weight: string;
  dimensions: string;
  location: string;
};

export default function NovoAnuncio({ productId }: NovoAnuncioProps) {
  const theme = useTheme();
  // Estado do formulário principal
  const [form, setForm] = useState<FormType>({
    title: "",
    category_id: "",
    price: "",
    available_quantity: "",
    buying_mode: "buy_it_now",
    listing_type_id: "gold_pro",
    condition: "new",
    description: "",
    video_id: "",
    warranty: "",
    pictures: [] as (File | string)[],
    attributes: [{ name: "", value_name: "" }],
    sale_terms: [{ id: "", value_name: "" }],
    official_store_id: "",
    brand: "",
    model: "",
    sku: "",
    ean: "",
    color: "",
    size: "",
    weight: "",
    dimensions: "",
    location: "",
  });
  const [imagePreviews, setImagePreviews] = useState<string[]>([]);
  const [categoriaModalOpen, setCategoriaModalOpen] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: "", severity: "success" });
  const [variations, setVariations] = useState<Variation[]>([
    {
      price: '',
      available_quantity: '',
      attributes: [{ name: '', value_name: '' }],
      pictures: [],
      sku: '',
      ean: '',
    },
  ]);
  const [categorySupportsVariations, setCategorySupportsVariations] = useState(false);
  const [optimizeModalOpen, setOptimizeModalOpen] = useState(false);
  const [optimizeDescriptionModalOpen, setOptimizeDescriptionModalOpen] = useState(false);
  const [activeStep, setActiveStep] = useState(0);

  // Estado para atributos e sale_terms dinâmicos
  const [dynamicAttributes, setDynamicAttributes] = useState<any[]>([]);
  const [dynamicSaleTerms, setDynamicSaleTerms] = useState<any[]>([]);

  const steps = ['Fotos', 'Informações', 'Características', 'Otimização', 'Preview', 'Publicação'];

  // Função para buscar atributos e sale_terms da categoria
  async function fetchCategoryDetails(categoryId: string) {
    // Exemplo de endpoint da API ML
    // const attributesRes = await fetch(`https://api.mercadolibre.com/categories/${categoryId}/attributes`);
    // const saleTermsRes = await fetch(`https://api.mercadolibre.com/categories/${categoryId}/sale_terms`);
    // const attributes = await attributesRes.json();
    // const saleTerms = await saleTermsRes.json();
    // Simulação: retorna campos dinâmicos
    return {
      attributes: [
        { id: "COLOR", name: "Cor", value_type: "string", required: true },
        { id: "SIZE", name: "Tamanho", value_type: "string", required: false },
      ],
      sale_terms: [
        { id: "WARRANTY_TYPE", name: "Tipo de garantia", value_type: "string", required: false },
        { id: "WARRANTY_TIME", name: "Tempo de garantia", value_type: "string", required: false },
      ],
    };
  }

  // Validação simples
  const validateForm = () => {
    return (
      form.title.length > 0 &&
      (!categorySupportsVariations ? form.price.length > 0 : true) &&
      form.description.length > 0 &&
      form.category_id.length > 0 &&
      (!categorySupportsVariations ? form.available_quantity.length > 0 : true)
    );
  };

  // Handlers do formulário principal
  type FormField = keyof typeof form;
  const handleChange = (field: FormField, value: string | number) => {
    setForm({ ...form, [field]: value });
  };
  const getCategoriaNome = (id: string) => {
    const cat = _categorias.find(c => c.id === id);
    return cat ? cat.nome : '';
  };
  const handleAttributeChange = (idx: number, field: "name" | "value_name", value: string) => {
    const updated = form.attributes.map((attr, i) =>
      i === idx ? { ...attr, [field]: value } : attr,
    );
    setForm({ ...form, attributes: updated });
  };
  const handleAddAttribute = () => {
    setForm({ ...form, attributes: [...form.attributes, { name: "", value_name: "" }] });
  };
  const handleRemoveAttribute = (idx: number) => {
    setForm({ ...form, attributes: form.attributes.filter((_, i) => i !== idx) });
  };
  const handleRemovePicture = (idx: number) => {
    const newPictures = form.pictures.filter((_: any, i: number) => i !== idx);
    setForm({ ...form, pictures: newPictures });
    setImagePreviews(imagePreviews.filter((_, i) => i !== idx));
  };
  const handlePictureUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    // Filtra apenas arquivos do tipo File
    const newPictures: File[] = form.pictures.filter((p): p is File => p instanceof File);
    const newPreviews: string[] = [...imagePreviews];
    for (let i = 0; i < files.length && newPictures.length < 10; i++) {
      newPictures.push(files[i]);
      newPreviews.push(URL.createObjectURL(files[i]));
    }
    setForm({ ...form, pictures: newPictures });
    setImagePreviews(newPreviews);
  };
  const handleSaleTermChange = (idx: number, field: "id" | "value_name", value: string) => {
    const updated = form.sale_terms.map((term, i) =>
      i === idx ? { ...term, [field]: value } : term,
    );
    setForm({ ...form, sale_terms: updated });
  };
  const handleAddSaleTerm = () => {
    setForm({ ...form, sale_terms: [...form.sale_terms, { id: "", value_name: "" }] });
  };
  const handleRemoveSaleTerm = (idx: number) => {
    setForm({ ...form, sale_terms: form.sale_terms.filter((_, i) => i !== idx) });
  };
  const handleSubmit = async () => {
    if (!validateForm()) {
      setSnackbar({ open: true, message: "Preencha todos os campos obrigatórios.", severity: "error" });
      return;
    }
    try {
      const payload = { ...form, variations };
      const res = await fetch(`/api/produtos/${productId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Erro ao atualizar produto");
      setSnackbar({ open: true, message: "Produto atualizado com sucesso!", severity: "success" });
    } catch (err) {
      setSnackbar({ open: true, message: "Erro ao atualizar produto.", severity: "error" });
    }
  };

  // Função para aplicar sugestões do modal
  const handleApplyOptimized = (optimized: { title?: string; description?: string }) => {
    setForm({
      ...form,
      ...(optimized.title ? { title: optimized.title } : {}),
      ...(optimized.description ? { description: optimized.description } : {}),
    });
    setOptimizeModalOpen(false);
    setSnackbar({ open: true, message: "Sugestão aplicada!", severity: "success" });
  };

  // Função para aplicar sugestão de descrição
  const handleApplyOptimizedDescription = (description: string) => {
    setForm({ ...form, description });
    setOptimizeDescriptionModalOpen(false);
    setSnackbar({ open: true, message: "Descrição otimizada aplicada!", severity: "success" });
  };

  // Handlers de variações
  const handleVariationChange = (idx: number, field: keyof Variation, value: string) => {
    const updated = variations.map((v, i) =>
      i === idx ? { ...v, [field]: value } : v
    );
    setVariations(updated);
  };
  const handleVariationAttributeChange = (varIdx: number, attrIdx: number, field: keyof VariationAttribute, value: string) => {
    const updated = variations.map((v, i) => {
      if (i !== varIdx) return v;
      const attrs = v.attributes.map((a, j) =>
        j === attrIdx ? { ...a, [field]: value } : a
      );
      return { ...v, attributes: attrs };
    });
    setVariations(updated);
  };
  const handleAddVariation = () => {
    setVariations([
      ...variations,
      {
        price: '',
        available_quantity: '',
        attributes: [{ name: '', value_name: '' }],
        pictures: [],
        sku: '',
        ean: '',
      },
    ]);
  };
  const handleRemoveVariation = (idx: number) => {
    setVariations(variations.filter((_, i) => i !== idx));
  };
  const handleAddVariationAttribute = (varIdx: number) => {
    const updated = variations.map((v, i) =>
      i === varIdx
        ? { ...v, attributes: [...v.attributes, { name: '', value_name: '' }] }
        : v
    );
    setVariations(updated);
  };
  const handleRemoveVariationAttribute = (varIdx: number, attrIdx: number) => {
    const updated = variations.map((v, i) => {
      if (i !== varIdx) return v;
      return {
        ...v,
        attributes: v.attributes.filter((_, j) => j !== attrIdx),
      };
    });
    setVariations(updated);
  };

  // Carrega dados do produto ao abrir a tela
  useEffect(() => {
    if (!productId) return;
    async function fetchProduct() {
      try {
        const res = await fetch(`/api/produtos/${productId}`);
        if (!res.ok) throw new Error("Erro ao buscar produto");
        const data = await res.json();
        setForm({ ...form, ...data });
        if (data.variations) setVariations(data.variations);
        if (data.pictures) setImagePreviews(data.pictures);
      } catch (err) {
        setSnackbar({ open: true, message: "Erro ao carregar produto.", severity: "error" });
      }
    }
    fetchProduct();
  }, [productId]);

  // Atualiza atributos/sale_terms ao selecionar categoria
  useEffect(() => {
    if (!form.category_id) return;
    fetchCategoryDetails(form.category_id).then(data => {
      setDynamicAttributes(data.attributes);
      setDynamicSaleTerms(data.sale_terms);
    });
  }, [form.category_id]);

  // Função para gerar descrição automática baseada apenas no título
  function gerarDescricaoAutomatica(form: FormType) {
    if (!form.title) return "Preencha o título para gerar a descrição.";
    return `Este anúncio refere-se ao produto: ${form.title}. Aproveite esta oferta exclusiva!`;
  }

  // Novo: instrução para IA de copywriting
  // Diretiva completa para IA de copywriting
  const INSTRUCAO_COPYWRITER = `# Persona: Copywriter Sênior Especialista em Otimização de Títulos e Descrições de Anúncios\n\n## Objetivo\nAtue como um copywriter sênior, especialista em criar, revisar e otimizar títulos e descrições de anúncios para marketplaces, e-commerces, landing pages e plataformas digitais.\n\n## Compromissos e Diretrizes\n\n- **Otimização máxima para SEO e relevância:**\n  - Identifique e utilize as melhores palavras-chave para o produto, público e plataforma.\n  - Garanta que o título seja atraente, direto, relevante e maximize o potencial de busca.\n  - Inclua palavras-chave primárias e secundárias de forma natural e estratégica.\n\n- **Descrição persuasiva e agradável:**\n  - Redija descrições claras, detalhadas e organizadas, destacando benefícios e diferenciais do produto/serviço.\n  - Use técnicas de persuasão, storytelling e gatilhos mentais (escassez, novidade, autoridade, confiança).\n  - Torne a leitura fluida, com frases curtas, linguagem positiva e orientada à solução.\n  - Evite exageros, promessas enganosas ou clichês vazios.\n  - Sempre revise para remover ambiguidades, repetições ou informações desnecessárias.\n\n- **Aumento da visibilidade do anúncio:**\n  - Inclua sugestões de palavras-chave de alto potencial.\n  - Estruture o texto para facilitar escaneabilidade (bullet points, subtítulos, destaques).\n  - Adapte o copy para o perfil do público-alvo e plataforma (Mercado Livre, Amazon, Google Shopping, etc.).\n  - Garanta que a descrição atenda às diretrizes da plataforma e seja aprovada nos filtros automáticos.\n\n- **Personalização e diferenciação:**\n  - Analise o conteúdo recebido ou detectado automaticamente.\n  - Destaque o que torna o produto único e competitivo.\n  - Sugira melhorias contínuas para o copy, sempre visando conversão e relevância.\n\n## Como agir\n\n- Analise automaticamente o conteúdo do anúncio (título e descrição).\n- Gere título otimizado, seguido de descrição persuasiva e orientada para conversão.\n- Liste as palavras-chave utilizadas e sugira outras que possam aumentar a visibilidade.\n- Apresente justificativa técnica para cada melhoria ou ajuste proposto.\n- Ofereça instruções para adaptar o texto a outros canais/plataformas se necessário.\n\n## Frase de ativação\n\n“Aja como um copywriter sênior, especialista em otimização automática de títulos e descrições para anúncios digitais. Seu compromisso é entregar textos agradáveis, persuasivos e otimizados para aumentar a visibilidade e conversão, utilizando palavras-chave relevantes e técnicas avançadas de copywriting.”\n`;

  // Função para gerar descrição automática via IA
  const handleGerarDescricaoAutomatica = async () => {
    if (!form.title) {
      setSnackbar({ open: true, message: "Preencha o título para gerar a descrição.", severity: "error" });
      return;
    }
    try {
      const res = await fetch("/api/optimize-description", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ title: form.title, instruction: INSTRUCAO_COPYWRITER }),
      });
      if (!res.ok) throw new Error("Erro ao otimizar descrição");
      const data = await res.json();
      setForm({ ...form, description: data.suggestions?.[0] || "", category_id: data.category || "MLB1234" });
      setSnackbar({ open: true, message: "Descrição otimizada aplicada!", severity: "success" });
    } catch (err) {
      setSnackbar({ open: true, message: "Erro ao otimizar descrição.", severity: "error" });
    }
  };

  // Função para otimizar atributos via IA
  const handleOtimizarAtributosIA = async () => {
    try {
      const res = await fetch("/api/optimize-attributes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ attributes: dynamicAttributes, title: form.title, description: form.description }),
      });
      if (!res.ok) throw new Error("Erro ao otimizar atributos");
      const data = await res.json();
      // Aplica sugestões nos atributos obrigatórios
      setForm(f => ({
        ...f,
        attributes: dynamicAttributes.map((attr, idx) => ({
          name: attr.name,
          value_name: data.suggestions?.[idx] || f.attributes[idx]?.value_name || ""
        }))
      }));
      setSnackbar({ open: true, message: "Atributos otimizados com IA!", severity: "success" });
    } catch {
      setSnackbar({ open: true, message: "Erro ao otimizar atributos.", severity: "error" });
    }
  };

  // Função para otimizar termos via IA
  const handleOtimizarTermosIA = async () => {
    try {
      const res = await fetch("/api/optimize-terms", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sale_terms: dynamicSaleTerms, title: form.title, description: form.description }),
      });
      if (!res.ok) throw new Error("Erro ao otimizar termos");
      const data = await res.json();
      setForm(f => ({
        ...f,
        sale_terms: dynamicSaleTerms.map((term, idx) => ({
          id: term.id,
          value_name: data.suggestions?.[idx] || f.sale_terms[idx]?.value_name || ""
        }))
      }));
      setSnackbar({ open: true, message: "Termos otimizados com IA!", severity: "success" });
    } catch {
      setSnackbar({ open: true, message: "Erro ao otimizar termos.", severity: "error" });
    }
  };

  // Função para otimizar variações via IA
  const handleOtimizarVariacoesIA = async () => {
    try {
      const res = await fetch("/api/optimize-variations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ variations, title: form.title, description: form.description }),
      });
      if (!res.ok) throw new Error("Erro ao otimizar variações");
      const data = await res.json();
      setVariations(data.suggestions || variations);
      setSnackbar({ open: true, message: "Variações otimizadas com IA!", severity: "success" });
    } catch {
      setSnackbar({ open: true, message: "Erro ao otimizar variações.", severity: "error" });
    }
  };

  // Preview dinâmico do anúncio
  function PreviewAnuncio({ form, imagePreviews }: { form: FormType; imagePreviews: string[] }) {
    return (
      <Card elevation={4} sx={{ mb: 4, bgcolor: '#fffbe6', border: '2px solid #ffe066', width: '100%' }}>
        <CardHeader title={<Typography variant="h6" fontWeight={700} color="warning.main">Preview do anúncio</Typography>} />
        <Divider />
        <CardContent>
          <Box sx={{ display: 'grid', gridTemplateColumns: '1fr', width: '100%', justifyItems: 'center', alignItems: 'center', gap: 2 }}>
            <Box sx={{ width: '100%', display: 'grid', justifyItems: 'center' }}>
              {imagePreviews[0] ? (
                <img src={imagePreviews[0]} alt="Preview" style={{ width: '100%', maxWidth: 320, borderRadius: 8, boxShadow: '0px 2px 8px rgba(0,0,0,0.1)' }} />
              ) : (
                <Box sx={{ width: 320, height: 180, bgcolor: '#eee', borderRadius: 8, display: 'grid', alignItems: 'center', justifyItems: 'center' }}>
                  <Typography color="text.secondary">Sem imagem</Typography>
                </Box>
              )}
            </Box>
            <Box sx={{ width: '100%' }}>
              <Typography variant="h5" fontWeight={700} color="primary" gutterBottom align="center">{form.title || 'Título do produto'}</Typography>
              <Typography variant="h6" color="success.main" gutterBottom align="center">R$ {form.price || '--'}</Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom align="center">{form.description || 'Descrição do produto.'}</Typography>
              <Typography variant="caption" color="text.secondary" align="center">Categoria: {getCategoriaNome(form.category_id) || 'Não definida'}</Typography>
            </Box>
          </Box>
          {/* Novo preview em Box abaixo do primeiro */}
          <Box sx={{ mt: 4, p: 3, bgcolor: '#e3f2fd', borderRadius: 2, border: '1px solid #90caf9', width: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <Typography variant="h6" fontWeight={700} color="primary" sx={{ mb: 2 }}>Preview alternativo</Typography>
            {imagePreviews[0] ? (
              <img src={imagePreviews[0]} alt="Preview alternativo" style={{ width: '100%', maxWidth: 320, borderRadius: 8, boxShadow: '0px 2px 8px rgba(0,0,0,0.1)', marginBottom: 16 }} />
            ) : (
              <Box sx={{ width: 320, height: 180, bgcolor: '#eee', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 2 }}>
                <Typography color="text.secondary">Sem imagem</Typography>
              </Box>
            )}
            <Typography variant="h5" fontWeight={700} color="primary" gutterBottom align="center">{form.title || 'Título do produto'}</Typography>
            <Typography variant="h6" color="success.main" gutterBottom align="center">R$ {form.price || '--'}</Typography>
            <Typography variant="body1" color="text.secondary" gutterBottom align="center">{form.description || 'Descrição do produto.'}</Typography>
            <Typography variant="caption" color="text.secondary" align="center">Categoria: {getCategoriaNome(form.category_id) || 'Não definida'}</Typography>
          </Box>
        </CardContent>
      </Card>
    );
  }

  // --- NOVO LAYOUT MELIIA ---
  // 1. Fotos e preview à esquerda, campos principais à direita
  // 2. Título, preço, condição e categoria agrupados no topo
  // 3. Descrição ampla abaixo dos principais
  // 4. Cards separados para atributos, termos, variações
  // 5. Botão de ação destacado no final

  return (
    <Box sx={{ bgcolor: theme.palette.grey[100], minHeight: "100vh", py: 4 }}>
      <Box sx={{ maxWidth: 1100, mx: "auto", px: { xs: 1, sm: 2, md: 0 } }}>
        {/* Stepper interativo */}
        <Stepper activeStep={activeStep} alternativeLabel sx={{ mb: 4 }}>
          {steps.map((label, idx) => (
            <Step key={label} completed={activeStep > idx}>
              <StepLabel
                sx={{ cursor: 'pointer', fontWeight: activeStep === idx ? 700 : 400, color: activeStep === idx ? 'primary.main' : 'inherit' }}
                onClick={() => setActiveStep(idx)}
              >
                {label}
              </StepLabel>
            </Step>
          ))}
        </Stepper>
        <Grid container columns={12} spacing={3} alignItems="flex-start">
          {/* Coluna esquerda: Fotos e preview */}
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 5' } }}>
            <Card elevation={3} sx={{ mb: 3 }}>
              <CardHeader title={<Typography variant="h6" fontWeight={700}>Fotos do produto</Typography>} />
              <Divider />
              <CardContent>
                <Button component="label" variant="contained" startIcon={<PhotoCamera />} sx={{ mb: 2, bgcolor: theme.palette.primary.main, color: '#fff', fontWeight: 700 }}>
                  Adicionar fotos
                  <input type="file" accept="image/*" multiple hidden onChange={handlePictureUpload} aria-label="Upload de fotos" />
                </Button>
                <Grid container spacing={2}>
                  {imagePreviews.map((src, idx) => (
                    <Box key={src} sx={{ position: "relative", width: "100%", pt: "100%", borderRadius: 2, overflow: "hidden", boxShadow: 1, mb: 1 }}>
                      <img src={src} alt={`Foto ${idx + 1}`} style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%", objectFit: "cover" }} />
                      <IconButton aria-label="Remover foto" size="small" color="error" sx={{ position: "absolute", top: 4, right: 4 }} onClick={() => handleRemovePicture(idx)}>
                        Remover
                      </IconButton>
                    </Box>
                  ))}
                </Grid>
                <Typography variant="caption" color="text.secondary">Máximo 10 imagens</Typography>
              </CardContent>
            </Card>
            {/* Preview dinâmico do anúncio - apenas Box, sem Card ou Grid */}
            <Box sx={{ width: '100%', bgcolor: '#fffbe6', border: '2px solid #ffe066', borderRadius: 2, mb: 4, p: 3, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <Typography variant="h6" fontWeight={700} color="warning.main" sx={{ mb: 2 }}>Preview do anúncio</Typography>
              {imagePreviews[0] ? (
                <img src={imagePreviews[0]} alt="Preview" style={{ width: '100%', maxWidth: 320, borderRadius: 8, boxShadow: '0px 2px 8px rgba(0,0,0,0.1)', marginBottom: 16 }} />
              ) : (
                <Box sx={{ width: 320, height: 180, bgcolor: '#eee', borderRadius: 8, display: 'grid', alignItems: 'center', justifyItems: 'center', mb: 2 }}>
                  <Typography color="text.secondary">Sem imagem</Typography>
                </Box>
              )}
              <Typography variant="h5" fontWeight={700} color="primary" gutterBottom align="center">{form.title || 'Título do produto'}</Typography>
              <Typography variant="h6" color="success.main" gutterBottom align="center">R$ {form.price || '--'}</Typography>
              <Typography variant="body1" color="text.secondary" gutterBottom align="center">{form.description || 'Descrição do produto.'}</Typography>
              <Typography variant="caption" color="text.secondary" align="center">Categoria: {getCategoriaNome(form.category_id) || 'Não definida'}</Typography>
            </Box>
          </Grid>
          {/* Coluna direita: campos principais */}
          <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 7' } }}>
            {/* TÍTULO EM CARD EXCLUSIVO */}
            <Card elevation={3} sx={{ mb: 3 }}>
              <CardHeader title={<Typography variant="h6" fontWeight={700}>Título do anúncio</Typography>} />
              <Divider />
              <CardContent>
                <Tooltip title="Escolha um título direto, relevante e com até 65 caracteres para maximizar o SEO." arrow>
                  <TextField
                    label="Título *"
                    fullWidth
                    required
                    value={form.title}
                    onChange={e => handleChange("title", e.target.value)}
                    inputProps={{ maxLength: 65 }}
                    helperText="Até 65 caracteres"
                    aria-label="Título do produto"
                    error={form.title.length === 0}
                  />
                </Tooltip>
              </CardContent>
            </Card>
            {/* DESCRIÇÃO EM CARD EXCLUSIVO */}
            <Card elevation={3} sx={{ mb: 3 }}>
              <CardHeader title={<Typography variant="h6" fontWeight={700}>Descrição do anúncio</Typography>} />
              <Divider />
              <CardContent>
                <Tooltip title="Descreva o produto de forma clara, detalhada e persuasiva. Use palavras-chave e destaque diferenciais." arrow>
                  <TextField
                    label="Descrição *"
                    multiline
                    minRows={6}
                    fullWidth
                    required
                    value={form.description}
                    onChange={e => handleChange("description", e.target.value)}
                    aria-label="Descrição"
                    error={form.description.length === 0}
                  />
                </Tooltip>
                <Button
                  variant="contained"
                  color="primary"
                  sx={{ fontWeight: 700, whiteSpace: 'nowrap', mt: 2 }}
                  onClick={handleGerarDescricaoAutomatica}
                >
                  Otimizar descrição
                </Button>
              </CardContent>
            </Card>
            {/* CAMPOS PRINCIPAIS EM CARD SEPARADO */}
            <Card elevation={3} sx={{ mb: 3 }}>
              <CardHeader title={<Typography variant="h6" fontWeight={700}>Informações principais</Typography>} />
              <Divider />
              <CardContent>
                <Grid container columns={12} spacing={2} alignItems="center">
                  <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                    <TextField select label="Categoria *" fullWidth required SelectProps={{ native: true }} value={form.category_id} onChange={e => handleChange("category_id", e.target.value)} aria-label="Categoria">
                      {_categorias.map(opt => <option key={opt.id} value={opt.id}>{opt.nome}</option>)}
                    </TextField>
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <TextField select label="Condição *" fullWidth required SelectProps={{ native: true }} value={form.condition} onChange={e => handleChange("condition", e.target.value)} aria-label="Condição">
                      {_condicoes.map(opt => <option key={opt.value} value={opt.value}>{opt.label}</option>)}
                    </TextField>
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <Tooltip title="Defina o preço competitivo, considerando o mercado e margens. Use valores reais para maior conversão." arrow>
                      <TextField label="Preço *" type="number" fullWidth required value={form.price} onChange={e => handleChange("price", e.target.value)} InputProps={{ inputProps: { min: 1 } }} aria-label="Preço" error={form.price.length === 0} />
                    </Tooltip>
                  </Grid>
                  {/* Botão IA */}
                  <Grid sx={{ gridColumn: 'span 12' }}>
                    <Button
                      variant="outlined"
                      color="secondary"
                      sx={{ fontWeight: 700, whiteSpace: 'nowrap', mt: 1 }}
                      onClick={() => setOptimizeModalOpen(true)}
                    >
                      Otimizar com IA
                    </Button>
                  </Grid>
                  {/* Loja oficial, vídeo, garantia, marca, modelo, SKU, EAN */}
                  <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                    <TextField label="ID loja oficial" fullWidth value={form.official_store_id} onChange={e => handleChange("official_store_id", e.target.value)} aria-label="ID loja oficial" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                    <TextField label="Vídeo (YouTube ID)" fullWidth value={form.video_id} onChange={e => handleChange("video_id", e.target.value)} aria-label="Vídeo" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 4' } }}>
                    <TextField label="Garantia" fullWidth value={form.warranty} onChange={e => handleChange("warranty", e.target.value)} aria-label="Garantia" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <TextField label="Marca" fullWidth value={form.brand} onChange={e => handleChange("brand", e.target.value)} aria-label="Marca" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <TextField label="Modelo" fullWidth value={form.model} onChange={e => handleChange("model", e.target.value)} aria-label="Modelo" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <TextField label="SKU" fullWidth value={form.sku} onChange={e => handleChange("sku", e.target.value)} aria-label="SKU" />
                  </Grid>
                  <Grid sx={{ gridColumn: { xs: 'span 6', md: 'span 3' } }}>
                    <TextField label="EAN" fullWidth value={form.ean} onChange={e => handleChange("ean", e.target.value)} aria-label="EAN" />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
            {/* Cards secundários: características, atributos, termos, variações */}
            <Grid container columns={12} spacing={2}>
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Card elevation={2} sx={{ mb: 2 }}>
                  <CardHeader title={<Typography variant="h6" fontWeight={700}>Características físicas</Typography>} />
                  <Divider />
                  <CardContent>
                    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                      <TextField label="Cor" fullWidth value={form.color} onChange={e => handleChange("color", e.target.value)} aria-label="Cor" />
                      <TextField label="Tamanho" fullWidth value={form.size} onChange={e => handleChange("size", e.target.value)} aria-label="Tamanho" />
                      <TextField label="Peso" fullWidth value={form.weight} onChange={e => handleChange("weight", e.target.value)} aria-label="Peso" />
                      <TextField label="Dimensões" fullWidth value={form.dimensions} onChange={e => handleChange("dimensions", e.target.value)} aria-label="Dimensões" />
                      <TextField label="Marca" fullWidth value={form.brand} onChange={e => handleChange("brand", e.target.value)} aria-label="Marca" />
                      <TextField label="Modelo" fullWidth value={form.model} onChange={e => handleChange("model", e.target.value)} aria-label="Modelo" />
                      <TextField label="SKU" fullWidth value={form.sku} onChange={e => handleChange("sku", e.target.value)} aria-label="SKU" />
                      <TextField label="EAN" fullWidth value={form.ean} onChange={e => handleChange("ean", e.target.value)} aria-label="EAN" />
                      <Box sx={{ gridColumn: '1 / -1' }}>
                        <TextField label="Localização" fullWidth value={form.location} onChange={e => handleChange("location", e.target.value)} aria-label="Localização" />
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              <Grid sx={{ gridColumn: { xs: 'span 12', md: 'span 6' } }}>
                <Card elevation={2} sx={{ mb: 2 }}>
                  <CardHeader title={<Typography variant="h6" fontWeight={700}>Vídeo e garantia</Typography>} />
                  <Divider />
                  <CardContent>
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <TextField label="Vídeo (YouTube ID)" fullWidth value={form.video_id} onChange={e => handleChange("video_id", e.target.value)} aria-label="Vídeo" />
                      <TextField label="Garantia" fullWidth value={form.warranty} onChange={e => handleChange("warranty", e.target.value)} aria-label="Garantia" />
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
            {/* Cards de atributos, termos, variações, estoque */}
            <Grid container columns={12} spacing={2}>
              {/* Card de atributos dinâmicos */}
              <Grid sx={{ gridColumn: 'span 12' }}>
                <Card elevation={2} sx={{ mb: 3 }}>
                  <CardHeader title={<Typography variant="h6" fontWeight={700}>Atributos</Typography>} />
                  <Divider />
                  <CardContent>
                    {/* Se dynamicAttributes vier do backend, exibe conforme regras; senão, mantém manual */}
                    {dynamicAttributes.length > 0 ? (
                      dynamicAttributes.map((attr, idx) => (
                        <Tooltip key={attr.id} title={(!form.attributes[idx]?.value_name && attr.required) ? `Preencha o atributo obrigatório: ${attr.name}` : `Preencha corretamente para maior relevância.`} arrow>
                          <TextField
                            label={attr.name + (attr.required ? " *" : "")}
                            fullWidth
                            required={attr.required}
                            value={form.attributes[idx]?.value_name || ""}
                            onChange={e => handleAttributeChange(idx, "value_name", e.target.value)}
                            sx={{ mb: 2 }}
                            error={!form.attributes[idx]?.value_name && attr.required}
                          />
                        </Tooltip>
                      ))
                    ) : (
                      <>
                        {form.attributes.map((attr, idx) => (
                          <Grid container spacing={1} alignItems="center" key={attr.name + attr.value_name} sx={{ mb: 1 }}>
                            <Box sx={{ gridColumn: 'span 5' }}>
                              <TextField label="Nome" fullWidth value={attr.name} onChange={e => handleAttributeChange(idx, "name", e.target.value)} aria-label="Nome atributo" />
                            </Box>
                            <Box sx={{ gridColumn: 'span 5' }}>
                              <TextField label="Valor" fullWidth value={attr.value_name} onChange={e => handleAttributeChange(idx, "value_name", e.target.value)} aria-label="Valor atributo" />
                            </Box>
                            <Box sx={{ gridColumn: 'span 2' }}>
                              <Button color="error" onClick={() => handleRemoveAttribute(idx)} disabled={form.attributes.length === 1}>Remover</Button>
                            </Box>
                          </Grid>
                        ))}
                        <Button variant="outlined" onClick={handleAddAttribute} sx={{ mt: 1 }}>Adicionar atributo</Button>
                      </>
                    )}
                  </CardContent>
                </Card>
              </Grid>

              {/* Card de termos de venda dinâmicos */}
              <Grid sx={{ gridColumn: 'span 12' }}>
                <Card elevation={2} sx={{ mb: 3 }}>
                  <CardHeader title={<Typography variant="h6" fontWeight={700}>Termos de venda</Typography>} />
                  <Divider />
                  <CardContent>
                    {form.sale_terms.map((term, idx) => (
                      <Grid container spacing={1} alignItems="center" key={term.id + term.value_name} sx={{ mb: 1 }}>
                        <Box sx={{ gridColumn: 'span 5' }}>
                          <TextField label="ID" fullWidth value={term.id} onChange={e => handleSaleTermChange(idx, "id", e.target.value)} aria-label="ID termo" />
                        </Box>
                        <Box sx={{ gridColumn: 'span 5' }}>
                          <TextField label="Valor" fullWidth value={term.value_name} onChange={e => handleSaleTermChange(idx, "value_name", e.target.value)} aria-label="Valor termo" />
                        </Box>
                        <Box sx={{ gridColumn: 'span 2' }}>
                          <Button color="error" onClick={() => handleRemoveSaleTerm(idx)} disabled={form.sale_terms.length === 1}>Remover</Button>
                        </Box>
                      </Grid>
                    ))}
                    <Button variant="outlined" onClick={handleAddSaleTerm} sx={{ mt: 1 }}>Adicionar termo</Button>
                  </CardContent>
                </Card>
              </Grid>

              {/* Card de variações (aparece só se a categoria suporta) */}
              {categorySupportsVariations && (
                <Grid sx={{ gridColumn: 'span 12' }}>
                  <Card elevation={2} sx={{ mb: 3 }}>
                    <CardHeader title={<Typography variant="h6" fontWeight={700}>Variações</Typography>} />
                    <Divider />
                    <CardContent>
                      {variations.map((v, idx) => (
                        <Box key={idx} sx={{ mb: 3, p: 2, border: '1px solid #eee', borderRadius: 2 }}>
                          <Grid container spacing={2} alignItems="center">
                            <Box sx={{ gridColumn: 'span 3' }}>
                              <Tooltip title={v.price.length === 0 ? 'Campo obrigatório' : 'Preço da variação'} arrow>
                                <TextField label="Preço *" type="number" fullWidth required value={v.price} onChange={e => handleVariationChange(idx, 'price', e.target.value)} InputProps={{ inputProps: { min: 1 } }} aria-label="Preço variação" error={v.price.length === 0} />
                              </Tooltip>
                            </Box>
                            <Box sx={{ gridColumn: 'span 3' }}>
                              <Tooltip title={v.available_quantity.length === 0 ? 'Campo obrigatório' : 'Estoque da variação'} arrow>
                                <TextField label="Estoque *" type="number" fullWidth required value={v.available_quantity} onChange={e => handleVariationChange(idx, 'available_quantity', e.target.value)} InputProps={{ inputProps: { min: 1 } }} aria-label="Estoque variação" error={v.available_quantity.length === 0} />
                              </Tooltip>
                            </Box>
                            <Box sx={{ gridColumn: 'span 3' }}>
                              <Tooltip title="SKU único para rastreamento e controle." arrow>
                                <TextField label="SKU" fullWidth value={v.sku} onChange={e => handleVariationChange(idx, 'sku', e.target.value)} aria-label="SKU variação" />
                              </Tooltip>
                            </Box>
                            <Box sx={{ gridColumn: 'span 3' }}>
                              <Tooltip title="EAN para identificação universal do produto." arrow>
                                <TextField label="EAN" fullWidth value={v.ean} onChange={e => handleVariationChange(idx, 'ean', e.target.value)} aria-label="EAN variação" />
                              </Tooltip>
                            </Box>
                          </Grid>
                          {/* Atributos da variação */}
                          <Box sx={{ mt: 2 }}>
                            <Typography variant="subtitle2" fontWeight={700}>Atributos da variação</Typography>
                            {v.attributes.map((attr, aIdx) => (
                              <Grid container spacing={1} alignItems="center" key={aIdx} sx={{ mb: 1 }}>
                                <Box sx={{ gridColumn: 'span 5' }}>
                                  <Tooltip title={attr.name.length === 0 ? 'Campo obrigatório' : 'Nome do atributo'} arrow>
                                    <TextField label="Nome" fullWidth value={attr.name} onChange={e => handleVariationAttributeChange(idx, aIdx, 'name', e.target.value)} aria-label="Nome atributo variação" error={attr.name.length === 0} />
                                  </Tooltip>
                                </Box>
                                <Box sx={{ gridColumn: 'span 5' }}>
                                  <Tooltip title={attr.value_name.length === 0 ? 'Campo obrigatório' : 'Valor do atributo'} arrow>
                                    <TextField label="Valor" fullWidth value={attr.value_name} onChange={e => handleVariationAttributeChange(idx, aIdx, 'value_name', e.target.value)} aria-label="Valor atributo variação" error={attr.value_name.length === 0} />
                                  </Tooltip>
                                </Box>
                                <Box sx={{ gridColumn: 'span 2' }}>
                                  <Button color="error" onClick={() => handleRemoveVariationAttribute(idx, aIdx)} disabled={v.attributes.length === 1}>Remover</Button>
                                </Box>
                              </Grid>
                            ))}
                            <Button variant="outlined" onClick={() => handleAddVariationAttribute(idx)} sx={{ mt: 1 }}>Adicionar atributo</Button>
                          </Box>
                          <Button color="error" onClick={() => handleRemoveVariation(idx)} sx={{ mt: 2 }} disabled={variations.length === 1}>Remover variação</Button>
                        </Box>
                      ))}
                      <Button variant="outlined" onClick={handleAddVariation}>Adicionar variação</Button>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Card de atributos dinâmicos da categoria */}
              {dynamicAttributes.length > 0 && (
                <Grid sx={{ gridColumn: 'span 12' }}>
                  <Card elevation={2} sx={{ mb: 3 }}>
                    <CardHeader title={<Typography variant="h6" fontWeight={700}>Atributos obrigatórios da categoria</Typography>} />
                    <Divider />
                    <CardContent>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {dynamicAttributes.map((attr, idx) => (
                          <TextField
                            key={attr.id}
                            label={attr.name + (attr.required ? " *" : "")}
                            fullWidth
                            required={attr.required}
                            value={form.attributes[idx]?.value_name || ""}
                            onChange={e => handleAttributeChange(idx, "value_name", e.target.value)}
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}

              {/* Card de termos de venda dinâmicos da categoria */}
              {dynamicSaleTerms.length > 0 && (
                <Grid sx={{ gridColumn: 'span 12' }}>
                  <Card elevation={2} sx={{ mb: 3 }}>
                    <CardHeader title={<Typography variant="h6" fontWeight={700}>Termos de venda da categoria</Typography>} />
                    <Divider />
                    <CardContent>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                        {dynamicSaleTerms.map((term, idx) => (
                          <TextField
                            key={term.id}
                            label={term.name + (term.required ? " *" : "")}
                            fullWidth
                            required={term.required}
                            value={form.sale_terms[idx]?.value_name || ""}
                            onChange={e => handleSaleTermChange(idx, "value_name", e.target.value)}
                          />
                        ))}
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              )}
            </Grid>
          </Grid>
        </Grid>
        {/* Botão de ação principal */}
        <Box sx={{ px: 0, py: 4, display: "flex", justifyContent: "flex-end" }}>
          <motion.div whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.98 }}>
            <Button onClick={handleSubmit} variant="contained" size="large" sx={{ fontWeight: 700, py: 1.5, px: 6, bgcolor: theme.palette.primary.main, color: "#fff", boxShadow: 3, borderRadius: 2, textTransform: "none", fontSize: 18, letterSpacing: 0.5, transition: "0.2s", '&:hover': { bgcolor: theme.palette.primary.dark } }} disabled={!validateForm() || (dynamicAttributes.some((a, idx) => a.required && !form.attributes[idx]?.value_name) || dynamicSaleTerms.some((t, idx) => t.required && !form.sale_terms[idx]?.value_name) || (categorySupportsVariations && variations.some(v => v.price.length === 0 || v.available_quantity.length === 0 || v.attributes.some(a => a.name.length === 0 || a.value_name.length === 0)) ))}>
              Atualizar anúncio
            </Button>
          </motion.div>
        </Box>
        <Snackbar open={snackbar.open} autoHideDuration={4000} onClose={() => setSnackbar({ ...snackbar, open: false })} anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
          <Alert severity={snackbar.severity as "success" | "error" | "info" | "warning"} sx={{ width: '100%' }}>
            {snackbar.message}
          </Alert>
        </Snackbar>
        <OptimizeProductModal
          open={optimizeModalOpen}
          onClose={() => setOptimizeModalOpen(false)}
          title={form.title}
          description={form.description}
          onApply={handleApplyOptimized}
        />
        <OptimizeDescriptionModal
          open={optimizeDescriptionModalOpen}
          onClose={() => setOptimizeDescriptionModalOpen(false)}
          title={form.title}
          instruction={INSTRUCAO_COPYWRITER}
          onApply={handleApplyOptimizedDescription}
        />
      </Box>
    </Box>
  );
}
