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
  // State
  predictions: PredictionData[];
  optimizations: OptimizationData[];
  modelStatus: ModelStatus | null;
  loading: boolean;
  error: string | null;

  // Actions
  addPrediction: (prediction: PredictionData) => void;
  addOptimization: (optimization: OptimizationData) => void;
  setModelStatus: (status: ModelStatus) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;
  
  // Async actions
  getModelStatus: () => Promise<void>;
  createPrediction: (features: number[], modelType?: string) => Promise<PredictionData>;
  createOptimization: (type: string, data: any) => Promise<OptimizationData>;
}

export const useAnalyticsStore = create<AnalyticsState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        predictions: [],
        optimizations: [],
        modelStatus: null,
        loading: false,
        error: null,

        // Sync actions
        addPrediction: (prediction) =>
          set((state) => ({
            predictions: [prediction, ...state.predictions.slice(0, 99)] // Keep last 100
          })),

        addOptimization: (optimization) =>
          set((state) => ({
            optimizations: [optimization, ...state.optimizations.slice(0, 99)] // Keep last 100
          })),

        setModelStatus: (status) =>
          set({ modelStatus: status }),

        setLoading: (loading) =>
          set({ loading }),

        setError: (error) =>
          set({ error }),

        clearError: () =>
          set({ error: null }),

        // Async actions
        getModelStatus: async () => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            const mockStatus: ModelStatus = {
              models: {
                linear: { is_trained: true, features_count: 5, type: 'linear' },
                sales_forecast: { is_trained: false, features_count: 8, type: 'forecast' },
                conversion: { is_trained: true, features_count: 6, type: 'conversion' }
              },
              total_models: 3,
              trained_models: 2,
              timestamp: new Date().toISOString()
            };
            
            set({ modelStatus: mockStatus, loading: false });
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to get model status',
              loading: false 
            });
          }
        },

        createPrediction: async (features, modelType = 'linear') => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 800));
            
            const prediction: PredictionData = {
              predicted_value: Math.random() * 0.1 + 0.02, // 0.02 to 0.12
              confidence_score: Math.random() * 0.3 + 0.7, // 0.7 to 1.0
              feature_importance: {
                budget: Math.random() * 0.5 + 0.2,
                keywords: Math.random() * 0.4 + 0.1,
                ctr: Math.random() * 0.4 + 0.1
              },
              timestamp: new Date().toISOString(),
              model_version: '1.0.0'
            };
            
            // Add to store
            get().addPrediction(prediction);
            
            set({ loading: false });
            return prediction;
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to create prediction',
              loading: false 
            });
            throw error;
          }
        },

        createOptimization: async (type, data) => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1200));
            
            const optimization: OptimizationData = {
              optimized_allocation: {
                campaign_0_budget: Math.random() * 5000 + 3000,
                campaign_1_budget: Math.random() * 5000 + 2000
              },
              expected_improvement: Math.random() * 1000 + 500,
              confidence_score: Math.random() * 0.2 + 0.75,
              optimization_method: 'greedy'
            };
            
            // Add to store
            get().addOptimization(optimization);
            
            set({ loading: false });
            return optimization;
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to create optimization',
              loading: false 
            });
            throw error;
          }
        }
      }),
      {
        name: 'analytics-store',
        partialize: (state) => ({
          predictions: state.predictions.slice(0, 50), // Persist only last 50
          optimizations: state.optimizations.slice(0, 50),
          modelStatus: state.modelStatus
        })
      }
    ),
    {
      name: 'analytics-store'
    }
  )
);