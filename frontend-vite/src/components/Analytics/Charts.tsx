import React from 'react';
import { motion } from 'framer-motion';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';

interface PredictionData {
  predicted_value: number;
  confidence_score: number;
  feature_importance: Record<string, number>;
  timestamp: string;
  model_version: string;
}

interface OptimizationData {
  optimized_allocation: Record<string, number>;
  expected_improvement: number;
  confidence_score: number;
  optimization_method: string;
}

interface ModelStatus {
  models: Record<string, any>;
  total_models: number;
  trained_models: number;
  timestamp: string;
}

interface ChartsProps {
  predictions: PredictionData[];
  optimizations: OptimizationData[];
  modelStatus: ModelStatus | null;
}

const COLORS = ['#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444', '#06B6D4'];

const Charts: React.FC<ChartsProps> = ({ predictions, optimizations, modelStatus }) => {
  // Dados para gráfico de tendência de previsões
  const predictionTrendData = predictions.map((pred, index) => ({
    index: index + 1,
    prediction: pred.predicted_value * 100,
    confidence: pred.confidence_score * 100,
    timestamp: new Date(pred.timestamp).toLocaleTimeString(),
  }));

  // Dados para gráfico de otimizações
  const optimizationData = optimizations.map((opt, index) => ({
    index: index + 1,
    improvement: opt.expected_improvement * 100,
    confidence: opt.confidence_score * 100,
    method: opt.optimization_method,
  }));

  // Dados para gráfico de status dos modelos
  const modelStatusData = modelStatus ? [
    {
      name: 'Total',
      value: modelStatus.total_models,
    },
    {
      name: 'Treinados',
      value: modelStatus.trained_models,
    },
  ] : [];

  return (
    <div style={{ display: 'flex', gap: 32, flexWrap: 'wrap' }}>
      {/* Gráfico de tendência de previsões */}
      <div style={{ flex: 1, minWidth: 320, height: 250 }}>
        <h4>Tendência de Previsões</h4>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={predictionTrendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" label={{ value: 'Previsão', position: 'insideBottomRight', offset: 0 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="prediction" stroke="#3B82F6" name="Previsão (%)" />
            <Line type="monotone" dataKey="confidence" stroke="#10B981" name="Confiança (%)" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico de otimizações */}
      <div style={{ flex: 1, minWidth: 320, height: 250 }}>
        <h4>Otimizações</h4>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={optimizationData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="method" label={{ value: 'Método', position: 'insideBottomRight', offset: 0 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="improvement" fill="#8B5CF6" name="Melhoria (%)" />
            <Bar dataKey="confidence" fill="#F59E0B" name="Confiança (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Gráfico de status dos modelos */}
      <div style={{ flex: 1, minWidth: 220, height: 250 }}>
        <h4>Status dos Modelos</h4>
        <ResponsiveContainer width="100%" height={200}>
          <PieChart>
            <Pie data={modelStatusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={60} label>
              {modelStatusData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default Charts;
