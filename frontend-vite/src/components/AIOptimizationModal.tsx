import React, { useState, useEffect } from 'react';
import { X, Wand2, TrendingUp, Eye, Target, Zap, Save, RefreshCw } from 'lucide-react';
import axios from 'axios';

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
});

interface Ad {
  id: string;
  title: string;
  [key: string]: any;
}

interface Optimization {
  original_text: string;
  optimized_text: string;
  keywords: string[];
  seo_score: number;
  readability_score: number;
  performance_lift: number;
  improvements: any[];
}

interface OptimizationOptions {
  target_audience: string;
  product_category: string;
  optimization_goal: string;
  keywords: string[];
  segment: string;
  budget_range: string;
  priority_metrics: string[];
}

interface AIOptimizationModalProps {
  ad: Ad;
  isOpen: boolean;
  onClose: () => void;
  onSave: (optimization: Optimization) => void;
}

const audienceOptions = [
  { value: 'general', label: 'Público Geral' },
  { value: 'young_adults', label: 'Jovens Adultos' },
  { value: 'families', label: 'Famílias' },
  { value: 'professionals', label: 'Profissionais' },
  { value: 'seniors', label: 'Terceira Idade' }
];

const goalOptions = [
  { value: 'conversions', label: 'Maximizar Conversões' },
  { value: 'clicks', label: 'Aumentar Cliques' },
  { value: 'seo', label: 'Melhorar SEO' },
  { value: 'brand_awareness', label: 'Aumentar Reconhecimento' }
];

const segmentOptions = [
  { value: 'millennial', label: 'Millennials' },
  { value: 'gen_z', label: 'Geração Z' },
  { value: 'b2b', label: 'B2B' },
  { value: 'b2c_premium', label: 'B2C Premium' },
  { value: 'b2c_popular', label: 'B2C Popular' }
];

const AIOptimizationModal: React.FC<AIOptimizationModalProps> = ({ ad, isOpen, onClose, onSave }) => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('copywriting');
  const [optimization, setOptimization] = useState<Optimization>({
    original_text: ad?.title || '',
    optimized_text: '',
    keywords: [],
    seo_score: 0,
    readability_score: 0,
    performance_lift: 0,
    improvements: []
  });
  const [optimizationOptions, setOptimizationOptions] = useState<OptimizationOptions>({
    target_audience: 'general',
    product_category: 'electronics',
    optimization_goal: 'conversions',
    keywords: [],
    segment: 'millennial',
    budget_range: 'medium',
    priority_metrics: ['seo', 'readability', 'compliance']
  });

  useEffect(() => {
    if (isOpen && ad) {
      setOptimization({
        original_text: ad.title,
        optimized_text: '',
        keywords: [],
        seo_score: 0,
        readability_score: 0,
        performance_lift: 0,
        improvements: []
      });
    }
  }, [isOpen, ad]);

  // ...existing code...

  return (
    <div>
      {/* Renderize o modal e os controles conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AIOptimizationModal;
