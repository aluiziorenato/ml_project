import React, { useState } from 'react';
import { 
  Eye, Edit, Play, Pause, ExternalLink, TrendingUp, 
  ChevronUp, ChevronDown, Star, Package 
} from 'lucide-react';
import AIOptimizationModal from './AIOptimizationModal';

interface Ad {
  id: string;
  price: number;
  available_quantity: number;
  sold_quantity?: number;
  [key: string]: any;
}

interface AdTableProps {
  ads: Ad[];
  selectedAds: string[];
  onSelect: (adId: string) => void;
  onSelectAll: () => void;
  onAction: (adId: string, action: string, value: number) => Promise<void>;
}

const AdTable: React.FC<AdTableProps> = ({ ads, selectedAds, onSelect, onSelectAll, onAction }) => {
  const [sortField, setSortField] = useState<string>('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  const [editingCell, setEditingCell] = useState<string | null>(null);
  const [editValue, setEditValue] = useState<string>('');
  const [showAIModal, setShowAIModal] = useState(false);
  const [selectedAdForAI, setSelectedAdForAI] = useState<Ad | null>(null);

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getSortedAds = () => {
    if (!sortField) return ads;
    return [...ads].sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      if (sortField === 'price' || sortField === 'available_quantity' || sortField === 'sold_quantity') {
        aValue = parseFloat(aValue) || 0;
        bValue = parseFloat(bValue) || 0;
      }
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase();
        bValue = (bValue || '').toLowerCase();
      }
      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  };

  const startEditing = (adId: string, field: string, currentValue: number | string) => {
    setEditingCell(`${adId}-${field}`);
    setEditValue(currentValue.toString());
  };

  const saveEdit = async (adId: string, field: string) => {
    if (editValue !== '') {
      const action = field === 'price' ? 'update_price' : 'update_stock';
      const value = field === 'price' ? parseFloat(editValue) : parseInt(editValue);
      await onAction(adId, action, value);
    }
  };

  // ...existing code...

  return (
    <div>
      {/* Renderize a tabela de anúncios conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AdTable;
