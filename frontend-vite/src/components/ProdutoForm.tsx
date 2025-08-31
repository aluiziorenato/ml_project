import React, { useState } from "react";
import { TextField, Button, Grid, MenuItem, Typography } from "@mui/material";

const categorias = [
  "MLB5726", // Eletrônicos
  "MLB1055", // Casa
  "MLB1430", // Moda
  "MLB1648", // Informática
  "MLB1071", // Esportes
  "MLB1246", // Beleza
  "MLB1743"  // Automotivo
];
const categoriaLabels = {
  "MLB5726": "Eletrônicos",
  "MLB1055": "Casa",
  "MLB1430": "Moda",
  "MLB1648": "Informática",
  "MLB1071": "Esportes",
  "MLB1246": "Beleza",
  "MLB1743": "Automotivo"
};
const statusList = ["active", "paused", "closed"];
const condicoes = ["new", "used"];
const buyingModes = ["buy_it_now", "auction"];
const listingTypes = ["gold_pro", "gold_special", "gold_premium", "silver"];
const currencyList = ["BRL", "USD"];

export default function ProdutoForm({ produto = {}, onSubmit, onCancel }: any) {
  const [form, setForm] = useState({
    title: produto.title || produto.titulo || produto.nome || "",
    category_id: produto.category_id || produto.categoria || "",
    price: produto.price || produto.preco || "",
    currency_id: produto.currency_id || "BRL",
    available_quantity: produto.available_quantity || produto.estoque || "",
    status: produto.status || "active",
    description: produto.description || produto.descricao || "",
    condition: produto.condition || produto.condicao || "new",
    buying_mode: produto.buying_mode || "buy_it_now",
    listing_type_id: produto.listing_type_id || "gold_pro",
    warranty: produto.warranty || produto.garantia || "",
    sku: produto.sku || "",
    marca: produto.marca || "",
    modelo: produto.modelo || "",
    peso: produto.peso || "",
    altura: produto.altura || "",
    largura: produto.largura || "",
    comprimento: produto.comprimento || "",
    imagem: produto.imagem || "",
    video_id: produto.video_id || "",
    official_store_id: produto.official_store_id || "",
    views: produto.views || "",
    vendas: produto.vendas || "",
    turnover: produto.turnover || "",
    pictures: produto.pictures || [{ url: produto.imagem || "" }]
  });

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  function handlePictureChange(idx: number, value: string) {
    setForm((prev) => {
      const pics = [...prev.pictures];
      pics[idx] = { url: value };
      return { ...prev, pictures: pics };
    });
  }

  function handleAddPicture() {
    setForm((prev) => ({ ...prev, pictures: [...prev.pictures, { url: "" }] }));
  }

  function handleRemovePicture(idx: number) {
    setForm((prev) => {
      const pics = prev.pictures.filter((_: any, i: number) => i !== idx);
      return { ...prev, pictures: pics };
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (onSubmit) onSubmit(form);
  }

  return (
    <form onSubmit={handleSubmit} style={{ fontFamily: 'Inter, Segoe UI, Roboto, Arial, sans-serif', background: '#fff', borderRadius: 12, boxShadow: '0 4px 24px #e5e7eb', padding: 24 }}>
      <Typography variant="h6" gutterBottom style={{ fontSize: 18, fontWeight: 600, color: '#11110D', marginBottom: 12 }}>
        {produto.id ? "Alterar Produto" : "Cadastrar Produto"}
      </Typography>
      <Grid container columns={12} spacing={3}>
        <Grid>
          <TextField label="Título" name="title" value={form.title} onChange={handleChange} fullWidth required InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14, boxShadow: '0 1px 4px #e5e7eb' } }} />
        </Grid>
        <Grid>
          <TextField select label="Categoria" name="category_id" value={form.category_id} onChange={handleChange} fullWidth required InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {categorias.map((cat) => <MenuItem key={cat} value={cat}>{categoriaLabels[cat]}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid>
          <TextField label="Preço" name="price" type="number" value={form.price} onChange={handleChange} fullWidth required InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid>
          <TextField select label="Moeda" name="currency_id" value={form.currency_id} onChange={handleChange} fullWidth required InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {currencyList.map((cur) => <MenuItem key={cur} value={cur}>{cur}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid>
          <TextField label="Estoque" name="available_quantity" type="number" value={form.available_quantity} onChange={handleChange} fullWidth required InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid>
          <TextField select label="Status" name="status" value={form.status} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {statusList.map((s) => <MenuItem key={s} value={s}>{s}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid>
          <TextField label="Descrição" name="description" value={form.description} onChange={handleChange} fullWidth multiline rows={2} InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid>
          <TextField select label="Condição" name="condition" value={form.condition} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {condicoes.map((c) => <MenuItem key={c} value={c}>{c}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid item xs={3}>
          <TextField select label="Modo de Compra" name="buying_mode" value={form.buying_mode} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {buyingModes.map((m) => <MenuItem key={m} value={m}>{m}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid item xs={3}>
          <TextField select label="Tipo de Anúncio" name="listing_type_id" value={form.listing_type_id} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}>
            {listingTypes.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
          </TextField>
        </Grid>
        <Grid item xs={3}>
          <TextField label="Garantia" name="warranty" value={form.warranty} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={6}>
          <TextField label="SKU" name="sku" value={form.sku} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={6}>
          <TextField label="Marca" name="marca" value={form.marca} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={6}>
          <TextField label="Modelo" name="modelo" value={form.modelo} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={12}>
          <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 600, color: '#11110D' }}>Imagens do Produto</Typography>
          {form.pictures.map((pic: any, idx: number) => (
            <Grid container spacing={1} alignItems="center" key={idx} sx={{ mb: 1 }}>
              <Grid item xs={9}>
                <TextField
                  label={`Imagem ${idx + 1} (URL)`}
                  value={pic.url}
                  onChange={e => handlePictureChange(idx, e.target.value)}
                  fullWidth
                  InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }}
                />
              </Grid>
              <Grid item xs={2}>
                {pic.url && (
                  <img src={pic.url} alt={`Preview ${idx + 1}`} style={{ width: 56, height: 56, objectFit: 'cover', borderRadius: 8, border: '1px solid #E5E7EB', boxShadow: '0 1px 4px #e5e7eb' }} />
                )}
              </Grid>
              <Grid item xs={1}>
                {form.pictures.length > 1 && (
                  <Button color="error" onClick={() => handleRemovePicture(idx)} style={{ fontSize: 13, minWidth: 32, padding: '3px 8px', borderRadius: 6, background: '#F43F5E', color: '#fff', boxShadow: '0 2px 8px #e5e7eb', border: 'none', cursor: 'pointer', transition: 'background 0.2s' }} onMouseOver={e => (e.currentTarget.style.background='#be123c')} onMouseOut={e => (e.currentTarget.style.background='#F43F5E')}>-</Button>
                )}
              </Grid>
            </Grid>
          ))}
          <Button variant="outlined" color="primary" onClick={handleAddPicture} style={{ fontSize: 13, padding: '5px 12px', borderRadius: 6, background: '#1976D2', color: '#fff', boxShadow: '0 2px 8px #e5e7eb', border: 'none', cursor: 'pointer', transition: 'background 0.2s' }} onMouseOver={e => (e.currentTarget.style.background='#1565c0')} onMouseOut={e => (e.currentTarget.style.background='#1976D2')}>Adicionar Imagem</Button>
        </Grid>
        <Grid item xs={6}>
          <TextField label="Vídeo ID" name="video_id" value={form.video_id} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={6}>
          <TextField label="Loja Oficial ID" name="official_store_id" type="number" value={form.official_store_id} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={3}>
          <TextField label="Peso (kg)" name="peso" type="number" value={form.peso} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={3}>
          <TextField label="Altura (cm)" name="altura" type="number" value={form.altura} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={3}>
          <TextField label="Largura (cm)" name="largura" type="number" value={form.largura} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={3}>
          <TextField label="Comprimento (cm)" name="comprimento" type="number" value={form.comprimento} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={4}>
          <TextField label="Views" name="views" type="number" value={form.views} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={4}>
          <TextField label="Vendas" name="vendas" type="number" value={form.vendas} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={4}>
          <TextField label="Turnover" name="turnover" type="number" value={form.turnover} onChange={handleChange} fullWidth InputProps={{ style: { borderRadius: 8, background: '#F6F7F9', fontSize: 14 } }} />
        </Grid>
        <Grid item xs={12} style={{ display: "flex", gap: 8, justifyContent: "flex-end" }}>
          <Button variant="contained" color="primary" type="submit" style={{ fontSize: 15, padding: '8px 22px', borderRadius: 6, background: '#10B981', color: '#fff', boxShadow: '0 2px 8px #e5e7eb', border: 'none', cursor: 'pointer', transition: 'background 0.2s' }} onMouseOver={e => (e.currentTarget.style.background='#059669')} onMouseOut={e => (e.currentTarget.style.background='#10B981')}>
            {produto.id ? "Salvar Alterações" : "Cadastrar"}
          </Button>
          {onCancel && (
            <Button variant="outlined" color="secondary" onClick={onCancel} style={{ fontSize: 15, padding: '8px 22px', borderRadius: 6, background: '#F43F5E', color: '#fff', boxShadow: '0 2px 8px #e5e7eb', border: 'none', cursor: 'pointer', transition: 'background 0.2s' }} onMouseOver={e => (e.currentTarget.style.background='#be123c')} onMouseOut={e => (e.currentTarget.style.background='#F43F5E')}>Cancelar</Button>
          )}
        </Grid>
      </Grid>
    </form>
  );
}
