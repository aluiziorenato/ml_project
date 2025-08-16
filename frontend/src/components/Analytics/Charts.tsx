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
  // Prepare prediction trend data
  const predictionTrendData = predictions
    .slice()
    .reverse()
    .map((pred, index) => ({
      index: index + 1,
      prediction: pred.predicted_value * 100,
      confidence: pred.confidence_score * 100,
      timestamp: new Date(pred.timestamp).toLocaleTimeString()
    }));

  // Prepare optimization improvement data
  const optimizationData = optimizations
    .slice()
    .reverse()
    .map((opt, index) => ({
      index: index + 1,
      improvement: opt.expected_improvement,
      confidence: opt.confidence_score * 100,
      method: opt.optimization_method
    }));

  // Prepare feature importance data from latest prediction
  const featureImportanceData = predictions.length > 0
    ? Object.entries(predictions[0].feature_importance).map(([feature, importance]) => ({
        feature: feature.charAt(0).toUpperCase() + feature.slice(1),
        importance: importance * 100
      }))
    : [];

  // Prepare budget allocation data from latest optimization
  const budgetAllocationData = optimizations.length > 0
    ? Object.entries(optimizations[0].optimized_allocation).map(([campaign, budget], index) => ({
        campaign: campaign.replace('_', ' ').replace('budget', '').trim(),
        budget: budget,
        fill: COLORS[index % COLORS.length]
      }))
    : [];

  // Prepare model status data
  const modelStatusData = modelStatus
    ? Object.entries(modelStatus.models).map(([name, model]) => ({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        trained: model.is_trained ? 1 : 0,
        features: model.features_count
      }))
    : [];

  return (
    <div className="space-y-8">
      {/* Prediction Trends */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
      >
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Prediction Trends</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={predictionTrendData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
            <XAxis 
              dataKey="index" 
              tick={{ fill: '#6B7280', fontSize: 12 }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <YAxis 
              tick={{ fill: '#6B7280', fontSize: 12 }}
              axisLine={{ stroke: '#D1D5DB' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
              }}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="prediction"
              stroke="#3B82F6"
              strokeWidth={3}
              dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
              name="Prediction Value (%)"
            />
            <Line
              type="monotone"
              dataKey="confidence"
              stroke="#10B981"
              strokeWidth={2}
              dot={{ fill: '#10B981', strokeWidth: 2, r: 3 }}
              name="Confidence (%)"
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Feature Importance */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Feature Importance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={featureImportanceData} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                type="number" 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
              />
              <YAxis 
                type="category" 
                dataKey="feature"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
                width={80}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Importance']}
              />
              <Bar dataKey="importance" fill="#8B5CF6" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Budget Allocation */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Budget Allocation</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={budgetAllocationData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="budget"
                label={({ campaign, budget }) => `${campaign}: $${budget.toFixed(0)}`}
                labelLine={false}
              >
                {budgetAllocationData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.fill} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value: number) => [`$${value.toFixed(0)}`, 'Budget']}
              />
            </PieChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Optimization Performance */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Optimization Performance</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={optimizationData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="index"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
              />
              <YAxis 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value: number, name: string) => [
                  name === 'improvement' ? `$${value.toFixed(0)}` : `${value.toFixed(1)}%`,
                  name === 'improvement' ? 'Expected Improvement' : 'Confidence'
                ]}
              />
              <Area
                type="monotone"
                dataKey="improvement"
                stroke="#F59E0B"
                fill="#FEF3C7"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        {/* Model Status Overview */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Model Status</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={modelStatusData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                dataKey="name"
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
                angle={-45}
                textAnchor="end"
                height={60}
              />
              <YAxis 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                axisLine={{ stroke: '#D1D5DB' }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'white',
                  border: '1px solid #E5E7EB',
                  borderRadius: '8px',
                  boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)'
                }}
                formatter={(value: number, name: string) => [
                  name === 'trained' ? (value ? 'Yes' : 'No') : value,
                  name === 'trained' ? 'Is Trained' : 'Feature Count'
                ]}
              />
              <Legend />
              <Bar dataKey="trained" fill="#10B981" name="Training Status" />
              <Bar dataKey="features" fill="#3B82F6" name="Features" />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      </div>

      {/* Real-time Metrics */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.5 }}
        className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
      >
        <h3 className="text-xl font-semibold text-gray-900 mb-6">Real-time Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="text-center p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
            <div className="text-3xl font-bold text-blue-600">
              {predictions.length > 0 ? (predictions[0].predicted_value * 100).toFixed(2) : '0.00'}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Latest Prediction</div>
            <div className="text-xs text-gray-500 mt-1">
              {predictions.length > 0 ? new Date(predictions[0].timestamp).toLocaleTimeString() : 'No data'}
            </div>
          </div>

          <div className="text-center p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg">
            <div className="text-3xl font-bold text-green-600">
              {predictions.length > 0 ? (predictions[0].confidence_score * 100).toFixed(1) : '0.0'}%
            </div>
            <div className="text-sm text-gray-600 mt-1">Latest Confidence</div>
            <div className="text-xs text-gray-500 mt-1">Model Certainty</div>
          </div>

          <div className="text-center p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg">
            <div className="text-3xl font-bold text-purple-600">
              ${optimizations.length > 0 ? optimizations[0].expected_improvement.toFixed(0) : '0'}
            </div>
            <div className="text-sm text-gray-600 mt-1">Latest Improvement</div>
            <div className="text-xs text-gray-500 mt-1">Expected Value</div>
          </div>

          <div className="text-center p-4 bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg">
            <div className="text-3xl font-bold text-orange-600">
              {modelStatus ? `${modelStatus.trained_models}/${modelStatus.total_models}` : '0/0'}
            </div>
            <div className="text-sm text-gray-600 mt-1">Models Ready</div>
            <div className="text-xs text-gray-500 mt-1">Training Status</div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default Charts;