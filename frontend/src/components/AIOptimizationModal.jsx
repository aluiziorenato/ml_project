import React, { useState, useEffect } from 'react'
import { X, Wand2, TrendingUp, Eye, Target, Zap, Save, RefreshCw } from 'lucide-react'
import axios from 'axios'

const api = axios.create({ 
  baseURL: import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000' 
})

export default function AIOptimizationModal({ ad, isOpen, onClose, onSave }) {
  const [loading, setLoading] = useState(false)
  const [activeTab, setActiveTab] = useState('copywriting')
  const [optimization, setOptimization] = useState({
    original_text: ad?.title || '',
    optimized_text: '',
    keywords: [],
    seo_score: 0,
    readability_score: 0,
    performance_lift: 0,
    improvements: []
  })
  const [optimizationOptions, setOptimizationOptions] = useState({
    target_audience: 'general',
    product_category: 'electronics',
    optimization_goal: 'conversions',
    keywords: [],
    segment: 'millennial',
    budget_range: 'medium',
    priority_metrics: ['seo', 'readability', 'compliance']
  })

  // Opções de configuração
  const audienceOptions = [
    { value: 'general', label: 'Público Geral' },
    { value: 'young_adults', label: 'Jovens Adultos' },
    { value: 'families', label: 'Famílias' },
    { value: 'professionals', label: 'Profissionais' },
    { value: 'seniors', label: 'Terceira Idade' }
  ]

  const goalOptions = [
    { value: 'conversions', label: 'Maximizar Conversões' },
    { value: 'clicks', label: 'Aumentar Cliques' },
    { value: 'seo', label: 'Melhorar SEO' },
    { value: 'brand_awareness', label: 'Aumentar Reconhecimento' }
  ]

  const segmentOptions = [
    { value: 'millennial', label: 'Millennials' },
    { value: 'gen_z', label: 'Geração Z' },
    { value: 'b2b', label: 'B2B' },
    { value: 'b2c_premium', label: 'B2C Premium' },
    { value: 'b2c_popular', label: 'B2C Popular' }
  ]

  // Carrega dados iniciais quando o modal abre
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
      })

      // Tenta detectar categoria automaticamente
      if (ad.category_id) {
        const categoryMapping = {
          'MLB1051': 'electronics',
          'MLB1648': 'electronics',
          'MLB1276': 'sports',
          'MLB1039': 'electronics',
          'MLB1132': 'toys'
        }
        const detectedCategory = categoryMapping[ad.category_id] || 'general'
        setOptimizationOptions(prev => ({
          ...prev,
          product_category: detectedCategory
        }))
      }
    }
  }, [isOpen, ad])

  // Gera sugestões de palavras-chave
  const generateKeywords = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await api.post('/api/anuncios/generate-keywords', {
        product_title: ad.title,
        product_category: optimizationOptions.product_category,
        target_audience: optimizationOptions.target_audience,
        budget_range: optimizationOptions.budget_range
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data.success) {
        const keywords = response.data.keywords.keywords?.map(k => k.keyword) || []
        setOptimizationOptions(prev => ({
          ...prev,
          keywords: keywords
        }))
      }
    } catch (error) {
      console.error('Erro ao gerar palavras-chave:', error)
    } finally {
      setLoading(false)
    }
  }

  // Otimiza o texto com IA
  const optimizeWithAI = async () => {
    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      const response = await api.post(`/api/anuncios/${ad.id}/optimize`, {
        original_text: optimization.original_text,
        target_audience: optimizationOptions.target_audience,
        product_category: optimizationOptions.product_category,
        optimization_goal: optimizationOptions.optimization_goal,
        keywords: optimizationOptions.keywords,
        segment: optimizationOptions.segment,
        budget_range: optimizationOptions.budget_range,
        priority_metrics: optimizationOptions.priority_metrics
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })

      if (response.data.success) {
        const optimizationData = response.data.optimization
        setOptimization(prev => ({
          ...prev,
          optimized_text: optimizationData.optimized_text,
          seo_score: optimizationData.seo_score,
          readability_score: optimizationData.readability_score,
          performance_lift: optimizationData.estimated_performance_lift,
          improvements: optimizationData.improvements || [],
          keywords: optimizationData.included_keywords || []
        }))
      }
    } catch (error) {
      console.error('Erro ao otimizar texto:', error)
    } finally {
      setLoading(false)
    }
  }

  // Aplica otimização ao anúncio
  const applyOptimization = async () => {
    if (!optimization.optimized_text) {
      alert('Execute a otimização primeiro')
      return
    }

    setLoading(true)
    try {
      const token = localStorage.getItem('access_token')
      await api.post(`/api/anuncios/${ad.id}/apply-optimization`, {
        title: optimization.optimized_text
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      // Chama callback para atualizar a lista
      await onSave(ad.id, 'update', { title: optimization.optimized_text })
      onClose()
    } catch (error) {
      console.error('Erro ao aplicar otimização:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen || !ad) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Wand2 className="h-6 w-6" />
              <div>
                <h2 className="text-xl font-bold">Otimização com IA</h2>
                <p className="text-purple-100 text-sm">Melhore seu anúncio com inteligência artificial</p>
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-2 hover:bg-white hover:bg-opacity-20 rounded-lg"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className="flex flex-col h-[calc(90vh-120px)]">
          {/* Tabs */}
          <div className="border-b border-gray-200">
            <div className="flex space-x-1 p-4">
              <button
                onClick={() => setActiveTab('copywriting')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  activeTab === 'copywriting'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                ✏️ Copywriting
              </button>
              <button
                onClick={() => setActiveTab('keywords')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  activeTab === 'keywords'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🔑 Palavras-chave
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  activeTab === 'analysis'
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                📊 Análise
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {activeTab === 'copywriting' && (
              <div className="space-y-6">
                {/* Configurações */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-gray-50 p-4 rounded-lg">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Público-alvo
                    </label>
                    <select
                      value={optimizationOptions.target_audience}
                      onChange={(e) => setOptimizationOptions(prev => ({
                        ...prev, target_audience: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      {audienceOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Objetivo
                    </label>
                    <select
                      value={optimizationOptions.optimization_goal}
                      onChange={(e) => setOptimizationOptions(prev => ({
                        ...prev, optimization_goal: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      {goalOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Segmento
                    </label>
                    <select
                      value={optimizationOptions.segment}
                      onChange={(e) => setOptimizationOptions(prev => ({
                        ...prev, segment: e.target.value
                      }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm"
                    >
                      {segmentOptions.map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Texto original vs otimizado */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Título Original
                    </label>
                    <textarea
                      value={optimization.original_text}
                      onChange={(e) => setOptimization(prev => ({
                        ...prev, original_text: e.target.value
                      }))}
                      className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md resize-none"
                      placeholder="Digite o título original..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Título Otimizado
                    </label>
                    <div className="relative">
                      <textarea
                        value={optimization.optimized_text}
                        onChange={(e) => setOptimization(prev => ({
                          ...prev, optimized_text: e.target.value
                        }))}
                        className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md resize-none"
                        placeholder="Clique em 'Otimizar com IA' para gerar..."
                        readOnly={!optimization.optimized_text}
                      />
                      {!optimization.optimized_text && (
                        <div className="absolute inset-0 bg-gray-50 bg-opacity-50 flex items-center justify-center">
                          <button
                            onClick={optimizeWithAI}
                            disabled={loading}
                            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                          >
                            {loading ? (
                              <RefreshCw className="h-4 w-4 animate-spin" />
                            ) : (
                              <Zap className="h-4 w-4" />
                            )}
                            Otimizar com IA
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Scores */}
                {optimization.optimized_text && (
                  <div className="grid grid-cols-3 gap-4">
                    <div className="bg-green-50 p-4 rounded-lg text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {optimization.seo_score}/100
                      </div>
                      <div className="text-sm text-gray-600">Score SEO</div>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {optimization.readability_score}/100
                      </div>
                      <div className="text-sm text-gray-600">Legibilidade</div>
                    </div>
                    <div className="bg-purple-50 p-4 rounded-lg text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        +{optimization.performance_lift}%
                      </div>
                      <div className="text-sm text-gray-600">Melhoria Estimada</div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'keywords' && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold">Palavras-chave Sugeridas</h3>
                  <button
                    onClick={generateKeywords}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                  >
                    {loading ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <Target className="h-4 w-4" />
                    )}
                    Gerar Sugestões
                  </button>
                </div>

                {optimizationOptions.keywords.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {optimizationOptions.keywords.map((keyword, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                )}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Adicionar palavras-chave personalizadas
                  </label>
                  <input
                    type="text"
                    placeholder="Digite palavras-chave separadas por vírgula"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md"
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && e.target.value) {
                        const newKeywords = e.target.value.split(',').map(k => k.trim())
                        setOptimizationOptions(prev => ({
                          ...prev,
                          keywords: [...prev.keywords, ...newKeywords]
                        }))
                        e.target.value = ''
                      }
                    }}
                  />
                </div>
              </div>
            )}

            {activeTab === 'analysis' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Análise e Sugestões</h3>
                
                {optimization.improvements.length > 0 ? (
                  <div className="space-y-3">
                    {optimization.improvements.map((improvement, index) => (
                      <div key={index} className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          <TrendingUp className="h-5 w-5 text-yellow-600 mt-0.5" />
                          <div>
                            <h4 className="font-medium text-yellow-800">{improvement.category}</h4>
                            <p className="text-yellow-700 text-sm">{improvement.suggestion}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <Eye className="h-12 w-12 mx-auto mb-3 text-gray-300" />
                    <p>Execute a otimização para ver análises detalhadas</p>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="border-t border-gray-200 p-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-600">
                {optimization.optimized_text ? 'Otimização concluída' : 'Configure e execute a otimização'}
              </div>
              <div className="flex gap-3">
                <button
                  onClick={onClose}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  onClick={applyOptimization}
                  disabled={!optimization.optimized_text || loading}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                >
                  <Save className="h-4 w-4" />
                  Aplicar Otimização
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}