import { analyticsActions } from './actions';

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

export interface AnalyticsState {
  predictions: PredictionData[];
  optimizations: OptimizationData[];
  modelStatus: ModelStatus | null;
  loading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  predictions: [],
  optimizations: [],
  modelStatus: null,
  loading: false,
  error: null
};

type AnalyticsAction = 
  | { type: typeof analyticsActions.SET_MODEL_STATUS; payload: ModelStatus }
  | { type: typeof analyticsActions.ADD_PREDICTION; payload: PredictionData }
  | { type: typeof analyticsActions.ADD_OPTIMIZATION; payload: OptimizationData }
  | { type: typeof analyticsActions.SET_LOADING; payload: boolean }
  | { type: typeof analyticsActions.SET_ERROR; payload: string | null }
  | { type: typeof analyticsActions.CLEAR_ERROR };

export const analyticsReducer = (
  state = initialState,
  action: AnalyticsAction
): AnalyticsState => {
  switch (action.type) {
    case analyticsActions.SET_MODEL_STATUS:
      return {
        ...state,
        modelStatus: action.payload,
        loading: false,
        error: null
      };

    case analyticsActions.ADD_PREDICTION:
      return {
        ...state,
        predictions: [action.payload, ...state.predictions.slice(0, 99)],
        loading: false,
        error: null
      };

    case analyticsActions.ADD_OPTIMIZATION:
      return {
        ...state,
        optimizations: [action.payload, ...state.optimizations.slice(0, 99)],
        loading: false,
        error: null
      };

    case analyticsActions.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };

    case analyticsActions.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };

    case analyticsActions.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};