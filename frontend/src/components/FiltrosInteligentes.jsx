// src/components/FiltrosInteligentes.jsx
import { useEffect, useMemo, useRef, useState } from "react";
import {
  Box,
  Stack,
  Chip,
  Slider,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
  OutlinedInput,
  Checkbox,
  ListItemText,
  CircularProgress,
} from "@mui/material";
import { useFilterOptions } from "../hooks/useFilterOptions";

const DEFAULTS = {
  categorias: [],
  status: [],
  preco: [0, 1000],
  roiMin: 0,
  sazonalidade: "",
  tags: { altaDemanda: false, baixaConcorrencia: false },
};

function getKey(userId) {
  return `filters:${userId ?? "anon"}`;
}

export default function FiltrosInteligentes({
  userId,
  onFilter,
  initialFilters,
  loading: loadingParent,
}) {
  const { categorias, status, loading: loadingOptions } = useFilterOptions();

  // Carrega ordem de precedência: localStorage > initialFilters > DEFAULTS
  const hydratedInitial = useMemo(() => {
    try {
      const fromLS = localStorage.getItem(getKey(userId));
      if (fromLS) return JSON.parse(fromLS);
    } catch {}
    return { ...DEFAULTS, ...(initialFilters || {}) };
  }, [userId, initialFilters]);

  const [filtros, setFiltros] = useState(hydratedInitial);
  const debounceRef = useRef(null);

  // Persistência + debounce de emissão
  useEffect(() => {
    try {
      localStorage.setItem(getKey(userId), JSON.stringify(filtros));
    } catch {}
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      onFilter?.(filtros);
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [filtros, onFilter, userId]);

  const isLoading = loadingParent || loadingOptions;

  const handleChangeArray = (key) => (event) => {
    setFiltros((prev) => ({ ...prev, [key]: event.target.value }));
  };

  const handleChangeSlider = (key) => (_, value) => {
    setFiltros((prev) => ({ ...prev, [key]: value }));
  };

  const toggleTag = (key) => () => {
    setFiltros((prev) => ({
      ...prev,
      tags: { ...prev.tags, [key]: !prev.tags[key] },
    }));
  };

  return (
    <Box sx={{ p: 2, borderRadius: 2, bgcolor: "background.paper", border: "1px solid", borderColor: "divider" }}>
      <Stack direction={{ xs: "column", md: "row" }} spacing={2} alignItems="center">
        {/* Categorias */}
        <FormControl sx={{ minWidth: 220 }}>
          <InputLabel id="cat-label">Categorias</InputLabel>
          <Select
            labelId="cat-label"
            multiple
            value={filtros.categorias}
            onChange={handleChangeArray("categorias")}
            input={<OutlinedInput label="Categorias" />}
            renderValue={(selected) => selected.join(", ")}
          >
            {categorias.map((name) => (
              <MenuItem key={name} value={name}>
                <Checkbox checked={filtros.categorias.indexOf(name) > -1} />
                <ListItemText primary={name} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Status */}
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel id="status-label">Status</InputLabel>
          <Select
            labelId="status-label"
            multiple
            value={filtros.status}
            onChange={handleChangeArray("status")}
            input={<OutlinedInput label="Status" />}
            renderValue={(selected) => selected.join(", ")}
          >
            {status.map((name) => (
              <MenuItem key={name} value={name}>
                <Checkbox checked={filtros.status.indexOf(name) > -1} />
                <ListItemText primary={name} />
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {/* Preço */}
        <Box sx={{ minWidth: 240 }}>
          <InputLabel shrink>Faixa de preço</InputLabel>
          <Slider
            value={filtros.preco}
            onChange={handleChangeSlider("preco")}
            valueLabelDisplay="auto"
            min={0}
            max={10000}
            step={10}
          />
        </Box>

        {/* ROI mínimo */}
        <Box sx={{ minWidth: 200 }}>
          <InputLabel shrink>ROI mínimo</InputLabel>
          <Slider
            value={filtros.roiMin}
            onChange={handleChangeSlider("roiMin")}
            valueLabelDisplay="auto"
            min={0}
            max={10}
            step={0.1}
          />
        </Box>

        {/* Sazonalidade */}
        <FormControl sx={{ minWidth: 180 }}>
          <InputLabel id="saz-label">Sazonalidade</InputLabel>
          <Select
            labelId="saz-label"
            value={filtros.sazonalidade}
            label="Sazonalidade"
            onChange={(e) =>
              setFiltros((prev) => ({ ...prev, sazonalidade: e.target.value }))
            }
          >
            <MenuItem value=""><em>Todas</em></MenuItem>
            <MenuItem value="Baixa">Baixa</MenuItem>
            <MenuItem value="Média">Média</MenuItem>
            <MenuItem value="Alta">Alta</MenuItem>
          </Select>
        </FormControl>

        {/* Chips de tags (filtros) */}
        <Stack direction="row" spacing={1}>
          <Chip
            label="Alta Demanda"
            color={filtros.tags.altaDemanda ? "primary" : "default"}
            variant={filtros.tags.altaDemanda ? "filled" : "outlined"}
            onClick={toggleTag("altaDemanda")}
          />
          <Chip
            label="Baixa Concorrência"
            color={filtros.tags.baixaConcorrencia ? "primary" : "default"}
            variant={filtros.tags.baixaConcorrencia ? "filled" : "outlined"}
            onClick={toggleTag("baixaConcorrencia")}
          />
        </Stack>

        {isLoading && <CircularProgress size={24} />}
      </Stack>
    </Box>
  );
}
