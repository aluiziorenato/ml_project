import React, { useState, useEffect } from 'react'
import axios from 'axios'
import AnimatedCard from '../components/AnimatedCard'
import AdCard from '../components/AdCard'
import AdTable from '../components/AdTable'
import AdvancedFilters from '../components/AdvancedFilters'
import AdActions from '../components/AdActions'
import { Search, Grid, List, Filter, RefreshCw, Plus, TrendingUp } from 'lucide-react'

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
})

export default function AnunciosPage() {
  const [ads, setAds] = useState([])
  const [loading, setLoading] = useState(false)
  const [viewMode, setViewMode] = useState('grid') // 'grid' ou 'table'
  const [showFilters, setShowFilters] = useState(false)
  const [selectedAds, setSelectedAds] = useState([])
  const [summary, setSummary] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [totalAds, setTotalAds] = useState(0)
  const [filters, setFilters] = useState({
    category_id: '',
    status: '',
    listing_type_id: '',
    shipping_mode: '',
    has_campaigns: null,
    min_price: '',
    max_price: '',
    min_stock: '',
    max_stock: ''
  })

  const itemsPerPage = 20

  // Carrega anúncios
  const loadAds = async (page = 1, appliedFilters = null) => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const offset = (page - 1) * itemsPerPage
      
      let endpoint = `/api/anuncios/list?offset=${offset}&limit=${itemsPerPage}`
      let response

      // Se há filtros aplicados, usa endpoint de filtro
      if (appliedFilters && Object.values(appliedFilters).some(v => v !== '' && v !== null)) {
        const filterData = { ...appliedFilters }
        if (searchTerm) {
          filterData.search = searchTerm
        }
        
        response = await api.post(`/api/anuncios/filter?offset=${offset}&limit=${itemsPerPage}`, 
          filterData, {
            headers: { Authorization: `Bearer ${token}` }
          }
        )
      } else {
        // Lista normal
        response = await api.get(endpoint, {
          headers: { Authorization: `Bearer ${token}` }
        })
      }

      if (response.data.success) {
        setAds(response.data.ads)
        setTotalAds(response.data.total)
        setCurrentPage(page)
      }
    } catch (error) {
      console.error('Erro ao carregar anúncios:', error)
      // TODO: Mostrar notificação de erro
    } finally {
      setLoading(false)
    }
  }

  // Carrega resumo estatístico
  const loadSummary = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await api.get('/api/anuncios/stats/summary', {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data.success) {
        setSummary(response.data.summary)
      }
    } catch (error) {
      console.error('Erro ao carregar resumo:', error)
    }
  }

  // Executa ação em anúncio
  const performAdAction = async (itemId, action, value = null) => {
    try {
      const token = localStorage.getItem('access_token')
      const response = await api.post(
        `/api/anuncios/${itemId}/action`,
        { action, value },
        { headers: { Authorization: `Bearer ${token}` } }
      )

      if (response.data.success) {
        // Recarrega a lista para mostrar mudanças
        loadAds(currentPage, filters)
        loadSummary()
        // TODO: Mostrar notificação de sucesso
        return true
      }
    } catch (error) {
      console.error(`Erro ao executar ação ${action}:`, error)
      // TODO: Mostrar notificação de erro
      return false
    }
  }

  // Aplica filtros
  const applyFilters = (newFilters) => {
    setFilters(newFilters)
    setCurrentPage(1)
    loadAds(1, newFilters)
  }

  // Busca por texto
  const handleSearch = (term) => {
    setSearchTerm(term)
    const searchFilters = { ...filters, search: term }
    setCurrentPage(1)
    loadAds(1, searchFilters)
  }

  // Seleciona/deseleciona anúncio
  const toggleAdSelection = (adId) => {
    setSelectedAds(prev => 
      prev.includes(adId) 
        ? prev.filter(id => id !== adId)
        : [...prev, adId]
    )
  }

  // Seleciona todos os anúncios visíveis
  const toggleSelectAll = () => {
    if (selectedAds.length === ads.length) {
      setSelectedAds([])
    } else {
      setSelectedAds(ads.map(ad => ad.id))
    }
  }

  // Abre otimização IA para um anúncio
  const openAIOptimization = (adId) => {
    // Esta função é chamada pelo AdActions, mas o modal
    // é gerenciado individualmente por cada componente
    console.log(`Abrindo otimização IA para anúncio ${adId}`)
  }

  // Abre editor para múltiplos anúncios
  const openEditor = (adIds) => {
    // TODO: Implementar editor em lote
    console.log(`Abrindo editor para ${adIds.length} anúncios`)
  }

  // Abre analytics para anúncios
  const openAnalytics = (adIds) => {
    // TODO: Implementar analytics
    console.log(`Abrindo analytics para ${adIds.length} anúncios`)
  }

  // Executa ação em lote
  const performBulkAction = async (action, value = null) => {
    const promises = selectedAds.map(adId => performAdAction(adId, action, value))
    const results = await Promise.all(promises)
    
    // Limpa seleção se todas as ações foram bem-sucedidas
    if (results.every(result => result)) {
      setSelectedAds([])
    }
  }

  // Carregamento inicial
  useEffect(() => {
    loadAds()
    loadSummary()
  }, [])

  const totalPages = Math.ceil(totalAds / itemsPerPage)

  return (
    <div className="space-y-6">
      {/* Header com resumo estatístico */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <AnimatedCard>
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {summary?.total_ads || 0}
            </div>
            <div className="text-sm text-gray-600">Total de Anúncios</div>
          </div>
        </AnimatedCard>
        
        <AnimatedCard>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {summary?.active_ads || 0}
            </div>
            <div className="text-sm text-gray-600">Ativos</div>
          </div>
        </AnimatedCard>
        
        <AnimatedCard>
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">
              {summary?.paused_ads || 0}
            </div>
            <div className="text-sm text-gray-600">Pausados</div>
          </div>
        </AnimatedCard>
        
        <AnimatedCard>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              R$ {summary?.avg_price?.toFixed(2) || '0.00'}
            </div>
            <div className="text-sm text-gray-600">Preço Médio</div>
          </div>
        </AnimatedCard>
      </div>

      {/* Barra de ferramentas */}
      <AnimatedCard>
        <div className="flex flex-col lg:flex-row gap-4 items-center justify-between">
          {/* Busca */}
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Buscar anúncios..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>
          </div>

          {/* Controles */}
          <div className="flex items-center gap-2">
            {/* Filtros */}
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`px-3 py-2 rounded-lg border flex items-center gap-2 ${
                showFilters ? 'bg-blue-50 border-blue-300' : 'border-gray-300'
              }`}
            >
              <Filter className="h-4 w-4" />
              Filtros
            </button>

            {/* Modo de visualização */}
            <div className="flex border rounded-lg">
              <button
                onClick={() => setViewMode('grid')}
                className={`px-3 py-2 ${viewMode === 'grid' ? 'bg-blue-500 text-white' : 'text-gray-600'}`}
              >
                <Grid className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('table')}
                className={`px-3 py-2 ${viewMode === 'table' ? 'bg-blue-500 text-white' : 'text-gray-600'}`}
              >
                <List className="h-4 w-4" />
              </button>
            </div>

            {/* Refresh */}
            <button
              onClick={() => loadAds(currentPage)}
              disabled={loading}
              className="px-3 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Ações em lote */}
        {selectedAds.length > 0 && (
          <AdActions
            ads={ads}
            selectedAds={selectedAds}
            onAction={performAdAction}
            onBulkAction={performBulkAction}
            onOpenOptimization={openAIOptimization}
            onOpenEditor={openEditor}
            onOpenAnalytics={openAnalytics}
          />
        )}
      </AnimatedCard>

      {/* Filtros avançados */}
      {showFilters && (
        <AnimatedCard title="Filtros Avançados">
          <AdvancedFilters
            filters={filters}
            onApplyFilters={applyFilters}
            onClearFilters={() => {
              setFilters({
                category_id: '',
                status: '',
                listing_type_id: '',
                shipping_mode: '',
                has_campaigns: null,
                min_price: '',
                max_price: '',
                min_stock: '',
                max_stock: ''
              })
              loadAds(1)
            }}
          />
        </AnimatedCard>
      )}

      {/* Lista de anúncios */}
      <AnimatedCard>
        {loading ? (
          <div className="flex justify-center items-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-blue-500" />
            <span className="ml-2 text-gray-600">Carregando anúncios...</span>
          </div>
        ) : ads.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-gray-400 mb-4">
              <Grid className="h-16 w-16 mx-auto" />
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              Nenhum anúncio encontrado
            </h3>
            <p className="text-gray-600">
              Tente ajustar os filtros ou verificar sua conexão com o Mercado Livre.
            </p>
          </div>
        ) : (
          <>
            {/* Seleção em massa */}
            <div className="mb-4 flex items-center gap-2">
              <input
                type="checkbox"
                checked={selectedAds.length === ads.length && ads.length > 0}
                onChange={toggleSelectAll}
                className="rounded"
              />
              <span className="text-sm text-gray-600">
                Selecionar todos ({ads.length} anúncios)
              </span>
            </div>

            {/* Grid ou Tabela */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {ads.map((ad) => (
                  <AdCard
                    key={ad.id}
                    ad={ad}
                    selected={selectedAds.includes(ad.id)}
                    onSelect={() => toggleAdSelection(ad.id)}
                    onAction={performAdAction}
                  />
                ))}
              </div>
            ) : (
              <AdTable
                ads={ads}
                selectedAds={selectedAds}
                onSelect={toggleAdSelection}
                onSelectAll={toggleSelectAll}
                onAction={performAdAction}
              />
            )}

            {/* Paginação */}
            {totalPages > 1 && (
              <div className="mt-6 flex justify-center items-center gap-2">
                <button
                  onClick={() => loadAds(currentPage - 1, filters)}
                  disabled={currentPage === 1}
                  className="px-3 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Anterior
                </button>
                
                <span className="px-4 py-2 text-sm text-gray-600">
                  Página {currentPage} de {totalPages} ({totalAds} anúncios)
                </span>
                
                <button
                  onClick={() => loadAds(currentPage + 1, filters)}
                  disabled={currentPage === totalPages}
                  className="px-3 py-2 border rounded-lg disabled:opacity-50 hover:bg-gray-50"
                >
                  Próxima
                </button>
              </div>
            )}
          </>
        )}
      </AnimatedCard>
    </div>
  )
}