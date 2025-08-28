import React, { useState, useEffect } from 'react';
import { X, Search, Filter, RefreshCw } from 'lucide-react';
import axios from 'axios';

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

interface FilterOption {
  value: string | boolean | null;
  label: string;
}

interface Category {
  id: string;
  name: string;
}

interface AdvancedFiltersProps {
  filters: any;
  onApplyFilters: (filters: any) => void;
  onClearFilters: () => void;
}

const statusOptions: FilterOption[] = [
  { value: '', label: 'Todos os status' },
  { value: 'active', label: 'Ativo' },
  { value: 'paused', label: 'Pausado' },
  { value: 'closed', label: 'Finalizado' }
];

const listingTypeOptions: FilterOption[] = [
  { value: '', label: 'Todos os tipos' },
  { value: 'gold_special', label: 'Clássico' },
  { value: 'gold_pro', label: 'Premium' },
  { value: 'free', label: 'Gratuito' }
];

const shippingModeOptions: FilterOption[] = [
  { value: '', label: 'Todos os fretes' },
  { value: 'me2', label: 'Mercado Envios' },
  { value: 'not_specified', label: 'Não especificado' },
  { value: 'custom', label: 'Personalizado' }
];

const campaignOptions: FilterOption[] = [
  { value: null, label: 'Todas' },
  { value: true, label: 'Com campanhas' },
  { value: false, label: 'Sem campanhas' }
];

const AdvancedFilters: React.FC<AdvancedFiltersProps> = ({ filters, onApplyFilters, onClearFilters }) => {
  const [localFilters, setLocalFilters] = useState<any>(filters);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loadingCategories, setLoadingCategories] = useState(false);

  const loadCategories = async () => {
    setLoadingCategories(true);
    try {
      const token = localStorage.getItem('access_token');
      const response = await api.get('/meli/categories', {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.data && Array.isArray(response.data)) {
        setCategories([
          { id: '', name: 'Todas as categorias' },
          ...response.data.map((cat: any) => ({ id: cat.id, name: cat.name }))
        ]);
      }
    } catch (error) {
      setCategories([
        { id: '', name: 'Todas as categorias' }
      ]);
    } finally {
      setLoadingCategories(false);
    }
  };

  useEffect(() => {
    loadCategories();
  }, []);

  // ...existing code...

  return (
    <div>
      {/* Renderize os filtros avançados conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AdvancedFilters;
