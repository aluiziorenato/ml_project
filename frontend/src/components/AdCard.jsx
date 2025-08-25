import React, { useState } from 'react'
import { 
  Eye, Edit, Play, Pause, DollarSign, Package, 
  Camera, Settings, TrendingUp, ExternalLink, Star 
} from 'lucide-react'
import AIOptimizationModal from './AIOptimizationModal'

export default function AdCard({ ad, selected, onSelect, onAction }) {
  const [showActions, setShowActions] = useState(false)
  const [editing, setEditing] = useState({ price: false, stock: false })
  const [newPrice, setNewPrice] = useState(ad.price || 0)
  const [newStock, setNewStock] = useState(ad.available_quantity || 0)
  const [showAIModal, setShowAIModal] = useState(false)

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-600 bg-green-50'
      case 'paused': return 'text-yellow-600 bg-yellow-50'
      case 'closed': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Ativo'
      case 'paused': return 'Pausado'
      case 'closed': return 'Finalizado'
      default: return status
    }
  }

  const handlePriceUpdate = async () => {
    if (newPrice !== ad.price) {
      const success = await onAction(ad.id, 'update_price', newPrice)
      if (success) {
        setEditing({ ...editing, price: false })
      }
    } else {
      setEditing({ ...editing, price: false })
    }
  }

  const handleStockUpdate = async () => {
    if (newStock !== ad.available_quantity) {
      const success = await onAction(ad.id, 'update_stock', newStock)
      if (success) {
        setEditing({ ...editing, stock: false })
      }
    } else {
      setEditing({ ...editing, stock: false })
    }
  }

  const formatPrice = (price) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: ad.currency_id || 'BRL'
    }).format(price)
  }

  return (
    <div className={`relative bg-white rounded-lg border-2 shadow-sm hover:shadow-md transition-all ${
      selected ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
    }`}>
      {/* Checkbox de seleção */}
      <div className="absolute top-3 left-3 z-10">
        <input
          type="checkbox"
          checked={selected}
          onChange={onSelect}
          className="w-4 h-4 text-blue-600 rounded"
        />
      </div>

      {/* Badge de status */}
      <div className="absolute top-3 right-3 z-10">
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(ad.status)}`}>
          {getStatusText(ad.status)}
        </span>
      </div>

      {/* Imagem do produto */}
      <div className="relative h-48 bg-gray-100 rounded-t-lg overflow-hidden">
        {ad.thumbnail || (ad.pictures && ad.pictures[0]) ? (
          <img
            src={ad.thumbnail || ad.pictures[0]?.url}
            alt={ad.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              e.target.style.display = 'none'
              e.target.nextSibling.style.display = 'flex'
            }}
          />
        ) : null}
        
        {/* Fallback para imagem */}
        <div className="w-full h-full flex items-center justify-center text-gray-400">
          <Camera className="h-12 w-12" />
        </div>

        {/* Indicador de campanhas */}
        {ad.has_campaigns && (
          <div className="absolute bottom-2 left-2">
            <span className="bg-purple-500 text-white text-xs px-2 py-1 rounded-full flex items-center gap-1">
              <Star className="h-3 w-3" />
              Campanha
            </span>
          </div>
        )}
      </div>

      {/* Conteúdo */}
      <div className="p-4">
        {/* Título */}
        <h3 className="font-medium text-gray-900 mb-2 line-clamp-2 min-h-[2.5rem]">
          {ad.title}
        </h3>

        {/* Preço */}
        <div className="mb-3">
          {editing.price ? (
            <div className="flex items-center gap-2">
              <input
                type="number"
                value={newPrice}
                onChange={(e) => setNewPrice(parseFloat(e.target.value))}
                className="w-24 px-2 py-1 text-sm border rounded"
                step="0.01"
                onBlur={handlePriceUpdate}
                onKeyPress={(e) => e.key === 'Enter' && handlePriceUpdate()}
                autoFocus
              />
              <button
                onClick={handlePriceUpdate}
                className="text-green-600 hover:text-green-700"
              >
                ✓
              </button>
            </div>
          ) : (
            <div 
              className="text-xl font-bold text-green-600 cursor-pointer hover:bg-green-50 p-1 rounded"
              onClick={() => setEditing({ ...editing, price: true })}
            >
              {formatPrice(ad.price)}
            </div>
          )}
        </div>

        {/* Estoque e vendidos */}
        <div className="flex justify-between items-center text-sm text-gray-600 mb-3">
          <div className="flex items-center gap-1">
            <Package className="h-4 w-4" />
            {editing.stock ? (
              <input
                type="number"
                value={newStock}
                onChange={(e) => setNewStock(parseInt(e.target.value))}
                className="w-16 px-1 py-0.5 text-xs border rounded"
                onBlur={handleStockUpdate}
                onKeyPress={(e) => e.key === 'Enter' && handleStockUpdate()}
                autoFocus
              />
            ) : (
              <span 
                className="cursor-pointer hover:bg-gray-100 px-1 rounded"
                onClick={() => setEditing({ ...editing, stock: true })}
              >
                Estoque: {ad.available_quantity}
              </span>
            )}
          </div>
          <span>Vendidos: {ad.sold_quantity || 0}</span>
        </div>

        {/* Tipo de anúncio e frete */}
        <div className="flex justify-between text-xs text-gray-500 mb-3">
          <span>{ad.listing_type_id}</span>
          <span>{ad.shipping?.mode || 'N/A'}</span>
        </div>

        {/* Ações rápidas */}
        <div className="flex gap-2">
          {/* Toggle status */}
          <button
            onClick={() => onAction(ad.id, ad.status === 'active' ? 'pause' : 'activate')}
            className={`flex-1 px-3 py-2 rounded text-sm font-medium transition-colors ${
              ad.status === 'active'
                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {ad.status === 'active' ? (
              <>
                <Pause className="h-4 w-4 inline mr-1" />
                Pausar
              </>
            ) : (
              <>
                <Play className="h-4 w-4 inline mr-1" />
                Ativar
              </>
            )}
          </button>

          {/* Menu de ações */}
          <div className="relative">
            <button
              onClick={() => setShowActions(!showActions)}
              className="px-3 py-2 border border-gray-300 rounded hover:bg-gray-50"
            >
              <Settings className="h-4 w-4" />
            </button>

            {showActions && (
              <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
                <button
                  onClick={() => window.open(ad.permalink, '_blank')}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <ExternalLink className="h-4 w-4" />
                  Ver no ML
                </button>
                <button
                  onClick={() => {
                    // TODO: Abrir modal de edição
                    setShowActions(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Edit className="h-4 w-4" />
                  Editar
                </button>
                <button
                  onClick={() => {
                    setShowAIModal(true)
                    setShowActions(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <TrendingUp className="h-4 w-4" />
                  Otimizar com IA
                </button>
                <button
                  onClick={() => {
                    // TODO: Ver analytics
                    setShowActions(false)
                  }}
                  className="w-full px-4 py-2 text-left hover:bg-gray-50 flex items-center gap-2"
                >
                  <Eye className="h-4 w-4" />
                  Analytics
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Overlay para fechar menu */}
      {showActions && (
        <div 
          className="fixed inset-0 z-10" 
          onClick={() => setShowActions(false)}
        />
      )}

      {/* Modal de otimização IA */}
      <AIOptimizationModal
        ad={ad}
        isOpen={showAIModal}
        onClose={() => setShowAIModal(false)}
        onSave={onAction}
      />
    </div>
  )
}