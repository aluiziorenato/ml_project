import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

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

interface AnalyticsState {
  predictions: PredictionData[];
  optimizations: OptimizationData[];
  modelStatus: ModelStatus | null;
  loading: boolean;
  error: string | null;
  addPrediction: (prediction: PredictionData) => void;
  addOptimization: (optimization: OptimizationData) => void;
  setModelStatus: (status: ModelStatus) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  getModelStatus: () => Promise<void>;
  createPrediction: (features: number[], modelType?: string) => Promise<PredictionData>;
  createOptimization: (type: string, data: any) => Promise<OptimizationData>;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools(
    persist(
      (set, get) => ({
        predictions: [],
        optimizations: [],
        modelStatus: null,
        loading: false,
        error: null,
        addPrediction: (prediction) => {
          set((state) => ({ predictions: [...state.predictions, prediction] }));
        },
        addOptimization: (optimization) => {
          set((state) => ({ optimizations: [...state.optimizations, optimization] }));
        },
        setModelStatus: (status) => {
          set(() => ({ modelStatus: status }));
        },
        setLoading: (loading) => {
          set(() => ({ loading }));
        },
        setError: (error) => {
          set(() => ({ error }));
        },
        clearError: () => {
          set(() => ({ error: null }));
        },
        getModelStatus: async () => {
          // Implemente a chamada real aqui
          set(() => ({ loading: true }));
          // ...existing code...
          set(() => ({ loading: false }));
        },
        createPrediction: async (features, modelType) => {
          // Implemente a chamada real aqui
          return {
            predicted_value: 0,
            confidence_score: 0,
            feature_importance: {},
            timestamp: new Date().toISOString(),
            model_version: 'v1',
          };
        },
        createOptimization: async (type, data) => {
          // Implemente a chamada real aqui
          return {
            optimized_allocation: {},
            expected_improvement: 0,
            confidence_score: 0,
            optimization_method: type,
          };
        },
      }),
      { name: 'analytics-store' }
    )
  )
);
