import React, { useState, useEffect } from 'react'
import { X, Search, Filter, RefreshCw } from 'lucide-react'
import axios from 'axios'

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
})

export default function AdvancedFilters({ filters, onApplyFilters, onClearFilters }) {
  const [localFilters, setLocalFilters] = useState(filters)
  const [categories, setCategories] = useState([])
  const [loadingCategories, setLoadingCategories] = useState(false)

  // Opções estáticas baseadas na API do Mercado Livre
  const statusOptions = [
    { value: '', label: 'Todos os status' },
    { value: 'active', label: 'Ativo' },
    { value: 'paused', label: 'Pausado' },
    { value: 'closed', label: 'Finalizado' }
  ]

  const listingTypeOptions = [
    { value: '', label: 'Todos os tipos' },
    { value: 'gold_special', label: 'Clássico' },
    { value: 'gold_pro', label: 'Premium' },
    { value: 'free', label: 'Gratuito' }
  ]

  const shippingModeOptions = [
    { value: '', label: 'Todos os fretes' },
    { value: 'me2', label: 'Mercado Envios' },
    { value: 'not_specified', label: 'Não especificado' },
    { value: 'custom', label: 'Personalizado' }
  ]

  const campaignOptions = [
    { value: null, label: 'Todas' },
    { value: true, label: 'Com campanhas' },
    { value: false, label: 'Sem campanhas' }
  ]

  // Carrega categorias
  const loadCategories = async () => {
    setLoadingCategories(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await api.get('/meli/categories', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data && Array.isArray(response.data)) {
        setCategories([
          { id: '', name: 'Todas as categorias' },
          ...response.data.map(cat => ({ id: cat.id, name: cat.name }))
        ])
      }
    } catch (error) {
      console.error('Erro ao carregar categorias:', error)
      // Categorias padrão como fallback
      setCategories([
        { id: '', name: 'Todas as categorias' },
        { id: 'MLB1051', name: 'Celulares e Telefones' },
        { id: 'MLB1648', name: 'Informática' },
        { id: 'MLB1276', name: 'Esportes e Fitness' },
        { id: 'MLB1039', name: 'Câmeras e Acessórios' },
        { id: 'MLB1132', name: 'Brinquedos e Hobbies' }
      ])
    } finally {
      setLoadingCategories(false)
    }
  }

  useEffect(() => {
    loadCategories()
  }, [])

  useEffect(() => {
    setLocalFilters(filters)
  }, [filters])

  const handleFilterChange = (field, value) => {
    setLocalFilters(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleApply = () => {
    onApplyFilters(localFilters)
  }

  const handleClear = () => {
    const clearedFilters = {
      category_id: '',
      status: '',
      listing_type_id: '',
      shipping_mode: '',
      has_campaigns: null,
      min_price: '',
      max_price: '',
      min_stock: '',
      max_stock: ''
    }
    setLocalFilters(clearedFilters)
    onClearFilters(clearedFilters)
  }

  const hasActiveFilters = Object.values(localFilters).some(value => 
    value !== '' && value !== null && value !== undefined
  )

  return (
    <div className="bg-gray-50 p-4 rounded-lg border">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        
        {/* Categoria */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Categoria
          </label>
          <select
            value={localFilters.category_id}
            onChange={(e) => handleFilterChange('category_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            disabled={loadingCategories}
          >
            {loadingCategories ? (
              <option>Carregando...</option>
            ) : (
              categories.map(category => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))
            )}
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            value={localFilters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {statusOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Tipo de anúncio */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Anúncio
          </label>
          <select
            value={localFilters.listing_type_id}
            onChange={(e) => handleFilterChange('listing_type_id', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {listingTypeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Modo de frete */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tipo de Frete
          </label>
          <select
            value={localFilters.shipping_mode}
            onChange={(e) => handleFilterChange('shipping_mode', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {shippingModeOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Campanhas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Campanhas
          </label>
          <select
            value={localFilters.has_campaigns === null ? 'null' : localFilters.has_campaigns}
            onChange={(e) => {
              const value = e.target.value === 'null' ? null : e.target.value === 'true'
              handleFilterChange('has_campaigns', value)
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            {campaignOptions.map(option => (
              <option key={option.value === null ? 'null' : option.value} value={option.value === null ? 'null' : option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>

        {/* Preço mínimo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Preço Mínimo
          </label>
          <input
            type="number"
            value={localFilters.min_price}
            onChange={(e) => handleFilterChange('min_price', e.target.value)}
            placeholder="R$ 0,00"
            min="0"
            step="0.01"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Preço máximo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Preço Máximo
          </label>
          <input
            type="number"
            value={localFilters.max_price}
            onChange={(e) => handleFilterChange('max_price', e.target.value)}
            placeholder="R$ 999.999,99"
            min="0"
            step="0.01"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Estoque mínimo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estoque Mínimo
          </label>
          <input
            type="number"
            value={localFilters.min_stock}
            onChange={(e) => handleFilterChange('min_stock', e.target.value)}
            placeholder="0"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Estoque máximo */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Estoque Máximo
          </label>
          <input
            type="number"
            value={localFilters.max_stock}
            onChange={(e) => handleFilterChange('max_stock', e.target.value)}
            placeholder="999999"
            min="0"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Botões de ação */}
      <div className="mt-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <span className="text-sm text-blue-600 bg-blue-50 px-2 py-1 rounded-full">
              {Object.values(localFilters).filter(v => v !== '' && v !== null).length} filtro(s) aplicado(s)
            </span>
          )}
        </div>
        
        <div className="flex gap-2">
          <button
            onClick={handleClear}
            className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50 flex items-center gap-2"
          >
            <X className="h-4 w-4" />
            Limpar
          </button>
          
          <button
            onClick={handleApply}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Aplicar Filtros
          </button>
        </div>
      </div>

      {/* Filtros rápidos */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm font-medium text-gray-700 mb-2">Filtros Rápidos:</div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => {
              setLocalFilters(prev => ({ ...prev, status: 'active' }))
              onApplyFilters({ ...localFilters, status: 'active' })
            }}
            className="px-3 py-1 text-xs bg-green-100 text-green-700 rounded-full hover:bg-green-200"
          >
            Apenas Ativos
          </button>
          <button
            onClick={() => {
              setLocalFilters(prev => ({ ...prev, status: 'paused' }))
              onApplyFilters({ ...localFilters, status: 'paused' })
            }}
            className="px-3 py-1 text-xs bg-yellow-100 text-yellow-700 rounded-full hover:bg-yellow-200"
          >
            Apenas Pausados
          </button>
          <button
            onClick={() => {
              setLocalFilters(prev => ({ ...prev, has_campaigns: true }))
              onApplyFilters({ ...localFilters, has_campaigns: true })
            }}
            className="px-3 py-1 text-xs bg-purple-100 text-purple-700 rounded-full hover:bg-purple-200"
          >
            Com Campanhas
          </button>
          <button
            onClick={() => {
              setLocalFilters(prev => ({ ...prev, min_stock: '0', max_stock: '5' }))
              onApplyFilters({ ...localFilters, min_stock: '0', max_stock: '5' })
            }}
            className="px-3 py-1 text-xs bg-red-100 text-red-700 rounded-full hover:bg-red-200"
          >
            Estoque Baixo
          </button>
        </div>
      </div>
    </div>
  )
}