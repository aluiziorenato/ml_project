import { Box, Chip, MenuItem, Select, Typography } from '@mui/material';
import { useState } from 'react';

const categorias = ['Smartphones', 'Notebooks', 'Acessórios'];
const sazonalidades = ['Black Friday', 'Natal', 'Volta às Aulas'];

export default function FilterBar({ onFilterChange }: { onFilterChange: (filters: any) => void }) {
  const [categoria, setCategoria] = useState('');
  const [sazonalidade, setSazonalidade] = useState('');

  const handleChange = () => {
    onFilterChange({ categoria, sazonalidade });
  };

  return (
    <Box display="flex" gap={2} alignItems="center" mb={2}>
      <Typography variant="subtitle1">Filtros:</Typography>

      <Select
        value={categoria}
        onChange={(e) => { setCategoria(e.target.value); handleChange(); }}
        displayEmpty
        size="small"
      >
        <MenuItem value="">Todas Categorias</MenuItem>
        {categorias.map((cat) => <MenuItem key={cat} value={cat}>{cat}</MenuItem>)}
      </Select>

      <Select
        value={sazonalidade}
        onChange={(e) => { setSazonalidade(e.target.value); handleChange(); }}
        displayEmpty
        size="small"
      >
        <MenuItem value="">Todas Sazonalidades</MenuItem>
        {sazonalidades.map((saz) => <MenuItem key={saz} value={saz}>{saz}</MenuItem>)}
      </Select>

      <Chip label="Alta Demanda" color="success" size="small" />
      <Chip label="Baixa Concorrência" color="warning" size="small" />
    </Box>
  );
}
