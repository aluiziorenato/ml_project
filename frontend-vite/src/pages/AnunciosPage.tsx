import React, { useState, useEffect } from 'react';
import axios from 'axios';
import AnimatedCard from '../components/AnimatedCard';
import AdCard from '../components/AdCard';
import AdTable from '../components/AdTable';
import AdvancedFilters from '../components/AdvancedFilters';
import AdActions from '../components/AdActions';
import { Search, Grid, List, Filter, RefreshCw, Plus, TrendingUp } from 'lucide-react';

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

const itemsPerPage = 20;

const AnunciosPage: React.FC = () => {
  const [ads, setAds] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'table'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedAds, setSelectedAds] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalAds, setTotalAds] = useState(0);
  const [filters, setFilters] = useState<any>({
    category_id: '',
    status: '',
    listing_type_id: '',
    shipping_mode: '',
    has_campaigns: null,
    min_price: '',
    max_price: '',
    min_stock: '',
    max_stock: ''
  });

  // Carrega anúncios
  const loadAds = async (page = 1, appliedFilters: any = null) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('access_token');
      const offset = (page - 1) * itemsPerPage;
      let endpoint = `/api/anuncios/list?offset=${offset}&limit=${itemsPerPage}`;
      let response;
      if (appliedFilters && Object.values(appliedFilters).some(v => v !== '' && v !== null)) {
        const filterData = { ...appliedFilters };
        if (searchTerm) {
          filterData.search = searchTerm;
        }
        response = await api.post(`/api/anuncios/filter?offset=${offset}&limit=${itemsPerPage}`, 
          filterData, {
            headers: { Authorization: `Bearer ${token}` }
          }
        );
      } else {
        response = await api.get(endpoint, {
          headers: { Authorization: `Bearer ${token}` }
        });
      }
      if (response.data) {
        setAds(response.data.ads || []);
        setTotalAds(response.data.total || 0);
        setSummary(response.data.summary || null);
      }
    } catch (error) {
      setAds([]);
      setTotalAds(0);
      setSummary(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAds(currentPage, filters);
    // eslint-disable-next-line
  }, [currentPage, filters, searchTerm]);

  // ...existing code...

  return (
    <div>
      {/* Renderize a página de anúncios conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AnunciosPage;
