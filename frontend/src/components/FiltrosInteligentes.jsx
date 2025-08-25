// src/components/FiltrosInteligentes.jsx
import { useEffect, useState } from "react";
import { Box, Chip, Slider, Select, MenuItem, Typography } from "@mui/material";
import axios from "axios";

export default function FiltrosInteligentes({ onFilter }) {
  const [categorias, setCategorias] = useState([]);
  const [categoria, setCategoria] = useState("");
  const [preco, setPreco] = useState([0, 1000]);
  const [roi, setRoi] = useState([0, 100]);
  const [tags, setTags] = useState([]);

  useEffect(() => {
    axios.get("/api/categories").then((res) => setCategorias(res.data));
  }, []);

  useEffect(() => {
    axios
      .post("/api/anuncios/filter", {
        categoria,
        preco_min: preco[0],
        preco_max: preco[1],
        roi_min: roi[0],
        roi_max: roi[1],
      })
      .then((res) => {
        onFilter(res.data);
        setTags(res.data.tags || []);
      });
  }, [categoria, preco, roi]);

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h6">Filtros Inteligentes</Typography>

      <Select value={categoria} onChange={(e) => setCategoria(e.target.value)} fullWidth>
        {categorias.map((cat) => (
          <MenuItem key={cat.id} value={cat.nome}>{cat.nome}</MenuItem>
        ))}
      </Select>

      <Typography mt={2}>Faixa de Preço</Typography>
      <Slider value={preco} onChange={(e, val) => setPreco(val)} min={0} max={5000} />

      <Typography mt={2}>ROI (%)</Typography>
      <Slider value={roi} onChange={(e, val) => setRoi(val)} min={0} max={100} />

      <Box mt={2}>
        {tags.map((tag, i) => (
          <Chip key={i} label={tag} color="primary" sx={{ mr: 1 }} />
        ))}
      </Box>
    </Box>
  );
}
