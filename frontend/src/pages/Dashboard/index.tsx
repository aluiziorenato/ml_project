import { useState } from 'react';
import { Box } from '@mui/material';
import FilterBar from '../../components/FilterBar';
import WidgetGrid from '../../components/WidgetGrid';

type Filters = {
  categoria?: string;
  dataInicio?: string;
  dataFim?: string;
  [key: string]: string | undefined;
};

export default function Dashboard() {
  const [filters, setFilters] = useState<Filters>({});

  const handleFilterChange = (newFilters: Filters) => {
    setFilters(newFilters);
    // Os filtros podem ser usados para condicionar os widgets exibidos
  };

  return (
    <Box p={2}>
      <FilterBar onFilterChange={handleFilterChange} />
      <WidgetGrid filters={filters} />
    </Box>
  );
}
