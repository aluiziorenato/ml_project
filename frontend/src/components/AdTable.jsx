import React, { useState } from 'react'
import { 
  Eye, Edit, Play, Pause, ExternalLink, TrendingUp, 
  ChevronUp, ChevronDown, Star, Package 
} from 'lucide-react'
import AIOptimizationModal from './AIOptimizationModal'

export default function AdTable({ ads, selectedAds, onSelect, onSelectAll, onAction }) {
  const [sortField, setSortField] = useState('')
  const [sortDirection, setSortDirection] = useState('asc')
  const [editingCell, setEditingCell] = useState(null)
  const [editValue, setEditValue] = useState('')
  const [showAIModal, setShowAIModal] = useState(false)
  const [selectedAdForAI, setSelectedAdForAI] = useState(null)

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortDirection('asc')
    }
  }

  const getSortedAds = () => {
    if (!sortField) return ads

    return [...ads].sort((a, b) => {
      let aValue = a[sortField]
      let bValue = b[sortField]

      // Tratamento especial para valores numéricos
      if (sortField === 'price' || sortField === 'available_quantity' || sortField === 'sold_quantity') {
        aValue = parseFloat(aValue) || 0
        bValue = parseFloat(bValue) || 0
      }

      // Tratamento para strings
      if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = (bValue || '').toLowerCase()
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1
      return 0
    })
  }

  const startEditing = (adId, field, currentValue) => {
    setEditingCell(`${adId}-${field}`)
    setEditValue(currentValue.toString())
  }

  const saveEdit = async (adId, field) => {
    if (editValue !== '') {
      const action = field === 'price' ? 'update_price' : 'update_stock'
      const value = field === 'price' ? parseFloat(editValue) : parseInt(editValue)
      await onAction(adId, action, value)
    }
    setEditingCell(null)
    setEditValue('')
  }

  const cancelEdit = () => {
    setEditingCell(null)
    setEditValue('')
  }

  const getStatusBadge = (status) => {
    const colors = {
      active: 'bg-green-100 text-green-800',
      paused: 'bg-yellow-100 text-yellow-800',
      closed: 'bg-red-100 text-red-800'
    }
    const labels = {
      active: 'Ativo',
      paused: 'Pausado',
      closed: 'Finalizado'
    }
    
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${colors[status] || 'bg-gray-100 text-gray-800'}`}>
        {labels[status] || status}
      </span>
    )
  }

  const formatPrice = (price, currency = 'BRL') => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: currency
    }).format(price)
  }

  const SortHeader = ({ field, children }) => (
    <th 
      className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
      onClick={() => handleSort(field)}
    >
      <div className="flex items-center gap-1">
        {children}
        {sortField === field && (
          sortDirection === 'asc' ? 
            <ChevronUp className="h-4 w-4" /> : 
            <ChevronDown className="h-4 w-4" />
        )}
      </div>
    </th>
  )

  const EditableCell = ({ adId, field, value, type = 'text' }) => {
    const cellKey = `${adId}-${field}`
    const isEditing = editingCell === cellKey

    if (isEditing) {
      return (
        <input
          type={type}
          value={editValue}
          onChange={(e) => setEditValue(e.target.value)}
          onBlur={() => saveEdit(adId, field)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') saveEdit(adId, field)
            if (e.key === 'Escape') cancelEdit()
          }}
          className="w-full px-2 py-1 border rounded text-sm"
          autoFocus
        />
      )
    }

    return (
      <div 
        className="cursor-pointer hover:bg-gray-100 px-2 py-1 rounded"
        onClick={() => startEditing(adId, field, value)}
      >
        {field === 'price' ? formatPrice(value) : value}
      </div>
    )
  }

  const sortedAds = getSortedAds()

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left">
              <input
                type="checkbox"
                checked={selectedAds.length === ads.length && ads.length > 0}
                onChange={onSelectAll}
                className="rounded"
              />
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Produto
            </th>
            <SortHeader field="title">Título</SortHeader>
            <SortHeader field="price">Preço</SortHeader>
            <SortHeader field="available_quantity">Estoque</SortHeader>
            <SortHeader field="sold_quantity">Vendidos</SortHeader>
            <SortHeader field="status">Status</SortHeader>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Categoria
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Frete
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Ações
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {sortedAds.map((ad) => (
            <tr key={ad.id} className={`hover:bg-gray-50 ${selectedAds.includes(ad.id) ? 'bg-blue-50' : ''}`}>
              {/* Checkbox */}
              <td className="px-4 py-4">
                <input
                  type="checkbox"
                  checked={selectedAds.includes(ad.id)}
                  onChange={() => onSelect(ad.id)}
                  className="rounded"
                />
              </td>

              {/* Imagem */}
              <td className="px-4 py-4">
                <div className="flex items-center">
                  <div className="h-12 w-12 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                    {ad.thumbnail ? (
                      <img
                        src={ad.thumbnail}
                        alt={ad.title}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center">
                        <Package className="h-6 w-6 text-gray-400" />
                      </div>
                    )}
                  </div>
                  {ad.has_campaigns && (
                    <Star className="h-4 w-4 text-purple-500 ml-2" />
                  )}
                </div>
              </td>

              {/* Título */}
              <td className="px-4 py-4">
                <div className="max-w-xs">
                  <div className="text-sm font-medium text-gray-900 line-clamp-2">
                    {ad.title}
                  </div>
                  <div className="text-sm text-gray-500">
                    ID: {ad.id}
                  </div>
                </div>
              </td>

              {/* Preço */}
              <td className="px-4 py-4">
                <EditableCell 
                  adId={ad.id} 
                  field="price" 
                  value={ad.price} 
                  type="number"
                />
              </td>

              {/* Estoque */}
              <td className="px-4 py-4">
                <EditableCell 
                  adId={ad.id} 
                  field="available_quantity" 
                  value={ad.available_quantity} 
                  type="number"
                />
              </td>

              {/* Vendidos */}
              <td className="px-4 py-4 text-sm text-gray-900">
                {ad.sold_quantity || 0}
              </td>

              {/* Status */}
              <td className="px-4 py-4">
                {getStatusBadge(ad.status)}
              </td>

              {/* Categoria */}
              <td className="px-4 py-4 text-sm text-gray-900">
                <div className="max-w-24 truncate">
                  {ad.category_id}
                </div>
              </td>

              {/* Frete */}
              <td className="px-4 py-4 text-sm text-gray-900">
                {ad.shipping?.mode || 'N/A'}
              </td>

              {/* Ações */}
              <td className="px-4 py-4">
                <div className="flex items-center gap-2">
                  {/* Toggle Status */}
                  <button
                    onClick={() => onAction(ad.id, ad.status === 'active' ? 'pause' : 'activate')}
                    className={`p-1 rounded hover:bg-gray-200 ${
                      ad.status === 'active' ? 'text-yellow-600' : 'text-green-600'
                    }`}
                    title={ad.status === 'active' ? 'Pausar' : 'Ativar'}
                  >
                    {ad.status === 'active' ? (
                      <Pause className="h-4 w-4" />
                    ) : (
                      <Play className="h-4 w-4" />
                    )}
                  </button>

                  {/* Ver no ML */}
                  <button
                    onClick={() => window.open(ad.permalink, '_blank')}
                    className="p-1 rounded hover:bg-gray-200 text-blue-600"
                    title="Ver no Mercado Livre"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </button>

                  {/* Editar */}
                  <button
                    onClick={() => {
                      // TODO: Abrir modal de edição
                    }}
                    className="p-1 rounded hover:bg-gray-200 text-gray-600"
                    title="Editar"
                  >
                    <Edit className="h-4 w-4" />
                  </button>

                  {/* Otimização IA */}
                  <button
                    onClick={() => {
                      setSelectedAdForAI(ad)
                      setShowAIModal(true)
                    }}
                    className="p-1 rounded hover:bg-gray-200 text-purple-600"
                    title="Otimizar com IA"
                  >
                    <TrendingUp className="h-4 w-4" />
                  </button>

                  {/* Analytics */}
                  <button
                    onClick={() => {
                      // TODO: Ver analytics
                    }}
                    className="p-1 rounded hover:bg-gray-200 text-indigo-600"
                    title="Ver Analytics"
                  >
                    <Eye className="h-4 w-4" />
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {ads.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          Nenhum anúncio encontrado
        </div>
      )}

      {/* Modal de otimização IA */}
      <AIOptimizationModal
        ad={selectedAdForAI}
        isOpen={showAIModal}
        onClose={() => {
          setShowAIModal(false)
          setSelectedAdForAI(null)
        }}
        onSave={onAction}
      />
    </div>
  )
}