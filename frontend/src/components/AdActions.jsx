import React, { useState } from 'react'
import { 
  Play, Pause, Edit, TrendingUp, DollarSign, Package, 
  Image, FileText, Settings, Eye, BarChart3, Calendar,
  AlertTriangle, CheckCircle, X 
} from 'lucide-react'
import AIOptimizationModal from './AIOptimizationModal'

export default function AdActions({ 
  ads, 
  selectedAds, 
  onAction, 
  onBulkAction, 
  onOpenOptimization,
  onOpenEditor,
  onOpenAnalytics 
}) {
  const [showBulkActions, setShowBulkActions] = useState(false)
  const [bulkPrice, setBulkPrice] = useState('')
  const [bulkStock, setBulkStock] = useState('')
  const [bulkDiscount, setBulkDiscount] = useState('')
  const [showAIModal, setShowAIModal] = useState(false)
  const [selectedAdForAI, setSelectedAdForAI] = useState(null)

  const selectedAdsData = ads.filter(ad => selectedAds.includes(ad.id))
  const hasSelection = selectedAds.length > 0

  const handleBulkPriceUpdate = () => {
    if (bulkPrice && selectedAds.length > 0) {
      onBulkAction('update_price', parseFloat(bulkPrice))
      setBulkPrice('')
    }
  }

  const handleBulkStockUpdate = () => {
    if (bulkStock && selectedAds.length > 0) {
      onBulkAction('update_stock', parseInt(bulkStock))
      setBulkStock('')
    }
  }

  const getSelectionStats = () => {
    const totalValue = selectedAdsData.reduce((sum, ad) => sum + (ad.price * ad.available_quantity), 0)
    const totalStock = selectedAdsData.reduce((sum, ad) => sum + ad.available_quantity, 0)
    const activeCount = selectedAdsData.filter(ad => ad.status === 'active').length
    const pausedCount = selectedAdsData.filter(ad => ad.status === 'paused').length

    return { totalValue, totalStock, activeCount, pausedCount }
  }

  if (!hasSelection) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 text-center">
        <Settings className="h-8 w-8 text-gray-400 mx-auto mb-2" />
        <p className="text-gray-600 text-sm">
          Selecione um ou mais anúncios para ver as ações disponíveis
        </p>
      </div>
    )
  }

  const stats = getSelectionStats()

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header com estatísticas */}
      <div className="bg-blue-50 border-b border-blue-200 p-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-blue-900">
              {selectedAds.length} anúncio(s) selecionado(s)
            </h3>
            <div className="text-sm text-blue-700 mt-1 space-x-4">
              <span>Valor total: R$ {stats.totalValue.toFixed(2)}</span>
              <span>Estoque total: {stats.totalStock}</span>
              <span className="text-green-600">{stats.activeCount} ativos</span>
              <span className="text-yellow-600">{stats.pausedCount} pausados</span>
            </div>
          </div>
          <button
            onClick={() => setShowBulkActions(!showBulkActions)}
            className="px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            {showBulkActions ? 'Fechar' : 'Ações em Lote'}
          </button>
        </div>
      </div>

      {/* Ações rápidas */}
      <div className="p-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Pausar todos */}
          <button
            onClick={() => onBulkAction('pause')}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-yellow-50 border border-yellow-200 rounded-lg hover:bg-yellow-100 text-yellow-700"
          >
            <Pause className="h-4 w-4" />
            <span className="text-sm font-medium">Pausar</span>
          </button>

          {/* Ativar todos */}
          <button
            onClick={() => onBulkAction('activate')}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 text-green-700"
          >
            <Play className="h-4 w-4" />
            <span className="text-sm font-medium">Ativar</span>
          </button>

          {/* Otimizar com IA */}
          <button
            onClick={() => {
              if (selectedAds.length === 1) {
                // Se apenas um anúncio selecionado, abre modal
                const ad = selectedAdsData[0]
                setSelectedAdForAI(ad)
                setShowAIModal(true)
              } else {
                // Para múltiplos anúncios, processa em lote
                selectedAds.forEach(id => onOpenOptimization(id))
              }
            }}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-purple-50 border border-purple-200 rounded-lg hover:bg-purple-100 text-purple-700"
          >
            <TrendingUp className="h-4 w-4" />
            <span className="text-sm font-medium">
              {selectedAds.length === 1 ? 'Otimizar IA' : `Otimizar ${selectedAds.length} ads`}
            </span>
          </button>

          {/* Ver Analytics */}
          <button
            onClick={() => onOpenAnalytics(selectedAds)}
            className="flex items-center justify-center gap-2 px-4 py-3 bg-indigo-50 border border-indigo-200 rounded-lg hover:bg-indigo-100 text-indigo-700"
          >
            <BarChart3 className="h-4 w-4" />
            <span className="text-sm font-medium">Analytics</span>
          </button>
        </div>
      </div>

      {/* Ações em lote expandidas */}
      {showBulkActions && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="space-y-4">
            {/* Atualização de preço em lote */}
            <div className="flex items-center gap-3">
              <DollarSign className="h-5 w-5 text-gray-500" />
              <label className="text-sm font-medium text-gray-700 w-24">
                Novo preço:
              </label>
              <input
                type="number"
                value={bulkPrice}
                onChange={(e) => setBulkPrice(e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className="flex-1 max-w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleBulkPriceUpdate}
                disabled={!bulkPrice}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Aplicar
              </button>
            </div>

            {/* Atualização de estoque em lote */}
            <div className="flex items-center gap-3">
              <Package className="h-5 w-5 text-gray-500" />
              <label className="text-sm font-medium text-gray-700 w-24">
                Novo estoque:
              </label>
              <input
                type="number"
                value={bulkStock}
                onChange={(e) => setBulkStock(e.target.value)}
                placeholder="0"
                min="0"
                className="flex-1 max-w-32 px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <button
                onClick={handleBulkStockUpdate}
                disabled={!bulkStock}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              />
            </div>

            {/* Ações avançadas */}
            <div className="pt-4 border-t border-gray-300">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {/* Edição em lote */}
                <button
                  onClick={() => onOpenEditor(selectedAds)}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <Edit className="h-4 w-4" />
                  <span className="text-sm">Editar em Lote</span>
                </button>

                {/* Atualizar imagens */}
                <button
                  onClick={() => {
                    // TODO: Implementar atualização de imagens
                  }}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <Image className="h-4 w-4" />
                  <span className="text-sm">Atualizar Imagens</span>
                </button>

                {/* Agendar alterações */}
                <button
                  onClick={() => {
                    // TODO: Implementar agendamento
                  }}
                  className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
                >
                  <Calendar className="h-4 w-4" />
                  <span className="text-sm">Agendar</span>
                </button>
              </div>
            </div>

            {/* Alertas e validações */}
            <div className="pt-4 border-t border-gray-300">
              <div className="text-sm space-y-2">
                {stats.activeCount > 0 && (
                  <div className="flex items-center gap-2 text-orange-600">
                    <AlertTriangle className="h-4 w-4" />
                    <span>
                      {stats.activeCount} anúncio(s) ativo(s) será(ão) afetado(s)
                    </span>
                  </div>
                )}
                
                {stats.pausedCount > 0 && (
                  <div className="flex items-center gap-2 text-blue-600">
                    <CheckCircle className="h-4 w-4" />
                    <span>
                      {stats.pausedCount} anúncio(s) pausado(s) será(ão) afetado(s)
                    </span>
                  </div>
                )}

                <div className="text-gray-600">
                  <strong>Dica:</strong> Todas as alterações serão aplicadas imediatamente.
                  Verifique os dados antes de confirmar.
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lista de anúncios selecionados (modo compacto) */}
      <div className="border-t border-gray-200 p-4">
        <div className="text-sm font-medium text-gray-700 mb-2">
          Anúncios selecionados:
        </div>
        <div className="max-h-32 overflow-y-auto space-y-1">
          {selectedAdsData.map((ad) => (
            <div key={ad.id} className="flex items-center justify-between text-xs bg-gray-50 p-2 rounded">
              <div className="flex items-center gap-2">
                <img
                  src={ad.thumbnail}
                  alt={ad.title}
                  className="w-6 h-6 rounded object-cover"
                  onError={(e) => {
                    e.target.style.display = 'none'
                  }}
                />
                <span className="truncate max-w-48">{ad.title}</span>
              </div>
              <div className="flex items-center gap-2 text-gray-500">
                <span>R$ {ad.price}</span>
                <span className={`px-1 rounded text-xs ${
                  ad.status === 'active' ? 'bg-green-100 text-green-600' : 'bg-yellow-100 text-yellow-600'
                }`}>
                  {ad.status === 'active' ? 'Ativo' : 'Pausado'}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

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