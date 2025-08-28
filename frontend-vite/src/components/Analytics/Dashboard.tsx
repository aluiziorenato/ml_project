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
  // ...existing code...

  // Mock de dados do backend
  const [metrics, setMetrics] = useState({
    totalPredictions: 12,
    averageConfidence: 0.92,
    totalOptimizations: 5,
    averageImprovement: 0.08,
  });
  const [predictions, setPredictions] = useState([
    { predicted_value: 0.025, confidence_score: 0.95, feature_importance: { a: 0.5, b: 0.5 }, timestamp: new Date().toISOString(), model_version: 'v1' },
    { predicted_value: 0.018, confidence_score: 0.91, feature_importance: { a: 0.6, b: 0.4 }, timestamp: new Date().toISOString(), model_version: 'v1' },
  ]);
  const [optimizations, setOptimizations] = useState([
    { optimized_allocation: { a: 0.7, b: 0.3 }, expected_improvement: 0.12, confidence_score: 0.88, optimization_method: 'genetic' },
    { optimized_allocation: { a: 0.6, b: 0.4 }, expected_improvement: 0.09, confidence_score: 0.90, optimization_method: 'bayesian' },
  ]);
  const [modelStatus, setModelStatus] = useState({ models: { v1: {} }, total_models: 1, trained_models: 1, timestamp: new Date().toISOString() });

  return (
    <div style={{ padding: 32 }}>
      <h2>Dashboard Analytics</h2>
      <div style={{ display: 'flex', gap: 24, marginBottom: 32 }}>
        <div style={{ minWidth: 180 }}><strong>Previsões</strong><div style={{ fontSize: 28 }}>{metrics.totalPredictions}</div></div>
        <div style={{ minWidth: 180 }}><strong>Confiança Média</strong><div style={{ fontSize: 28 }}>{(metrics.averageConfidence * 100).toFixed(1)}%</div></div>
        <div style={{ minWidth: 180 }}><strong>Otimizações</strong><div style={{ fontSize: 28 }}>{metrics.totalOptimizations}</div></div>
        <div style={{ minWidth: 180 }}><strong>Melhoria Média</strong><div style={{ fontSize: 28 }}>{(metrics.averageImprovement * 100).toFixed(1)}%</div></div>
      </div>
      <div style={{ height: 400, background: '#f9f9f9', borderRadius: 16, padding: 24 }}>
        <p style={{ marginBottom: 16 }}>Gráficos:</p>
        <Charts predictions={predictions} optimizations={optimizations} modelStatus={modelStatus} />
      </div>
    </div>
  );
}

export default Dashboard
