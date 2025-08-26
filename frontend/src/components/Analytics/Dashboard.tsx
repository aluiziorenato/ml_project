import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Charts from './Charts'
import { useAnalyticsStore } from '../../store/analytics/store'
import { apiClient } from '../../api/client'
import MetricCard from '../../components/MetricCard'

interface PredictionData {
  predicted_value: number
  confidence_score: number
  feature_importance: Record<string, number>
  timestamp: string
  model_version: string
}

interface OptimizationData {
  optimized_allocation: Record<string, number>
  expected_improvement: number
  confidence_score: number
  optimization_method: string
}

interface DashboardMetrics {
  totalPredictions: number
  averageConfidence: number
  totalOptimizations: number
  averageImprovement: number
}

const Dashboard: React.FC = () => {
  const [predictions, setPredictions] = useState<PredictionData[]>([])
  const [optimizations, setOptimizations] = useState<OptimizationData[]>([])
  const [metrics, setMetrics] = useState<DashboardMetrics>({
    totalPredictions: 0,
    averageConfidence: 0,
    totalOptimizations: 0,
    averageImprovement: 0,
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const { addPrediction, addOptimization, getModelStatus, modelStatus } =
    useAnalyticsStore()

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      setError(null)

      // Load model status
      await getModelStatus()

      // Sample data (substitua pela sua chamada real)
      const samplePredictions: PredictionData[] = [
        {
          predicted_value: 0.025,
          confidence_score: 0.85,
          feature_importance: { budget: 0.4, keywords: 0.3, ctr: 0.3 },
          timestamp: new Date().toISOString(),
          model_version: '1.0.0',
        },
        {
          predicted_value: 0.032,
          confidence_score: 0.78,
          feature_importance: { budget: 0.5, keywords: 0.2, ctr: 0.3 },
          timestamp: new Date(Date.now() - 3600000).toISOString(),
          model_version: '1.0.0',
        },
      ]

      const sampleOptimizations: OptimizationData[] = [
        {
          optimized_allocation: { campaign_0_budget: 6000, campaign_1_budget: 4000 },
          expected_improvement: 850,
          confidence_score: 0.82,
          optimization_method: 'greedy',
        },
        {
          optimized_allocation: { campaign_0_budget: 5500, campaign_1_budget: 4500 },
          expected_improvement: 720,
          confidence_score: 0.75,
          optimization_method: 'greedy',
        },
      ]

      setPredictions(samplePredictions)
      setOptimizations(sampleOptimizations)

      // Calcula métricas
      const totalPredictions = samplePredictions.length
      const averageConfidence =
        samplePredictions.reduce((sum, p) => sum + p.confidence_score, 0) /
        totalPredictions
      const totalOptimizations = sampleOptimizations.length
      const averageImprovement =
        sampleOptimizations.reduce((sum, o) => sum + o.expected_improvement, 0) /
        totalOptimizations

      setMetrics({
        totalPredictions,
        averageConfidence,
        totalOptimizations,
        averageImprovement,
      })
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load dashboard data'
      )
    } finally {
      setLoading(false)
    }
  }

  const handleNewPrediction = async () => {
    try {
      const features = [
        Math.random() * 1000,
        Math.random() * 100,
        Math.random() * 20,
      ]
      const response = await apiClient.post('/analytics/predict', {
        features,
        model_type: 'linear',
      })

      const newPrediction: PredictionData = {
        predicted_value: response.data.predicted_value,
        confidence_score: response.data.confidence_score,
        feature_importance: response.data.feature_importance,
        timestamp: response.data.timestamp,
        model_version: response.data.model_version,
      }

      setPredictions((prev) => [newPrediction, ...prev.slice(0, 9)])
      addPrediction(newPrediction)

      // Atualiza métricas
      setMetrics((prev) => ({
        ...prev,
        totalPredictions: prev.totalPredictions + 1,
        averageConfidence:
          (prev.averageConfidence * prev.totalPredictions +
            newPrediction.confidence_score) /
          (prev.totalPredictions + 1),
      }))
    } catch {
      setError('Failed to create new prediction')
    }
  }

  const handleNewOptimization = async () => {
    try {
      const campaigns = [
        { historical_roi: 2.0 + Math.random(), historical_conversion_rate: 0.02 + Math.random() * 0.02 },
        { historical_roi: 1.8 + Math.random(), historical_conversion_rate: 0.025 + Math.random() * 0.015 },
      ]
      const response = await apiClient.post('/analytics/optimize/budget', {
        campaigns,
        total_budget: 10000,
        objective: 'maximize_roi',
      })

      const newOptimization: OptimizationData = {
        optimized_allocation: response.data.optimized_allocation,
        expected_improvement: response.data.expected_improvement,
        confidence_score: response.data.confidence_score,
        optimization_method: response.data.optimization_method,
      }

      setOptimizations((prev) => [newOptimization, ...prev.slice(0, 9)])
      addOptimization(newOptimization)

      setMetrics((prev) => ({
        ...prev,
        totalOptimizations: prev.totalOptimizations + 1,
        averageImprovement:
          (prev.averageImprovement * prev.totalOptimizations +
            newOptimization.expected_improvement) /
          (prev.totalOptimizations + 1),
      }))
    } catch {
      setError('Failed to create new optimization')
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full"
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Analytics Dashboard
          </h1>
          <p className="text-gray-600">
            Monitor ML predictions and optimizations in real-time
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg"
          >
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </motion.div>
        )}

        {/* Metrics Cards (refatorado) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Predictions"
            value={metrics.totalPredictions}
            icon="🔮"
            color="blue"
          />
          <MetricCard
            title="Avg Confidence"
            value={`${(metrics.averageConfidence * 100).toFixed(1)}%`}
            icon="📊"
            color="green"
          />
          <MetricCard
            title="Optimizations"
            value={metrics.totalOptimizations}
            icon="⚡"
            color="purple"
          />
          <MetricCard
            title="Avg Improvement"
            value={`$${metrics.averageImprovement.toFixed(0)}`}
            icon="📈"
            color="orange"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 mb-8">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleNewPrediction}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
          >
            Generate Prediction
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={handleNewOptimization}
            className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium"
          >
            Run Optimization
          </motion.button>
        </div>

        {/* Charts Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mb-8"
        >
          <Charts
            predictions={predictions}
            optimizations={optimizations}
            modelStatus={modelStatus}
          />
        </motion.div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Recent Predictions */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="bg-white rounded-xl shadow-lg border border-gray-200 p-6"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Recent Predictions
            </h3>
            <div className="space-y-4">
              {predictions.slice(0, 5).map((prediction, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      {(prediction.predicted_value * 100).toFixed(2)}%
                    </p>
                    <p className="text-sm text-gray-500">
                      Confidence: {(prediction.confidence_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400">
                      {new Date(prediction.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Recent Optimizations */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="bg-white rounded-xl shadow-lg border border-gray-200 p-6"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Recent Optimizations
            </h3>
            <div className="space-y-4">
              {optimizations.slice(0, 5).map((optimization, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div>
                    <p className="font-medium text-gray-900">
                      +${optimization.expected_improvement.toFixed(0)}
                    </p>
                    <p className="text-sm text-gray-500">
                      Confidence: {(optimization.confidence_score * 100).toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-xs text-gray-400 capitalize">
                      {optimization.optimization_method}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Model Status */}
        {modelStatus && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.5 }}
            className="mt-8 bg-white rounded-xl shadow-lg border border-gray-200 p-6"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Model Status
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">
                  {modelStatus.total_models}
                </p>
                <p className="text-sm text-gray-600">Total Models</p>
              </div>
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">
                  {modelStatus.trained_models}
                </p>
                <p className="text-sm text-gray-600">Trained Models</p>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">
                  {((modelStatus.trained_models / modelStatus.total_models) * 100).toFixed(0)}%
                </p>
                <p className="text-sm text-gray-600">Training Progress</p>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  )
}

export default Dashboard
