import React, { useState } from 'react';
import { 
  Eye, Edit, Play, Pause, DollarSign, Package, 
  Camera, Settings, TrendingUp, ExternalLink, Star 
} from 'lucide-react';
import AIOptimizationModal from './AIOptimizationModal';

interface Ad {
  id: string;
  price: number;
  available_quantity: number;
  currency_id?: string;
  status: string;
  title?: string;
  [key: string]: any;
}

interface AdCardProps {
  ad: Ad;
  selected: boolean;
  onSelect: (adId: string) => void;
  onAction: (adId: string, action: string, value: number) => Promise<boolean>;
}

const AdCard: React.FC<AdCardProps> = ({ ad, selected, onSelect, onAction }) => {
  const [showActions, setShowActions] = useState(false);
  const [editing, setEditing] = useState<{ price: boolean; stock: boolean }>({ price: false, stock: false });
  const [newPrice, setNewPrice] = useState(ad.price || 0);
  const [newStock, setNewStock] = useState(ad.available_quantity || 0);
  const [showAIModal, setShowAIModal] = useState(false);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50';
      case 'paused': return 'text-yellow-600 bg-yellow-50';
      case 'closed': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Ativo';
      case 'paused': return 'Pausado';
      case 'closed': return 'Finalizado';
      default: return status;
    }
  };

  const handlePriceUpdate = async () => {
    if (newPrice !== ad.price) {
      const success = await onAction(ad.id, 'update_price', newPrice);
      if (success) {
        setEditing({ ...editing, price: false });
      }
    } else {
      setEditing({ ...editing, price: false });
    }
  };

  const handleStockUpdate = async () => {
    if (newStock !== ad.available_quantity) {
      const success = await onAction(ad.id, 'update_stock', newStock);
      if (success) {
        setEditing({ ...editing, stock: false });
      }
    } else {
      setEditing({ ...editing, stock: false });
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: ad.currency_id || 'BRL'
    }).format(price);
  };

  // ...existing code...

  return (
    <div>
      {/* Renderize o card do anúncio conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AdCard;
