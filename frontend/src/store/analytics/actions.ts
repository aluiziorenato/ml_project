// Analytics store actions
export interface AnalyticsActions {
  FETCH_MODEL_STATUS: 'FETCH_MODEL_STATUS';
  SET_MODEL_STATUS: 'SET_MODEL_STATUS';
  CREATE_PREDICTION: 'CREATE_PREDICTION';
  ADD_PREDICTION: 'ADD_PREDICTION';
  CREATE_OPTIMIZATION: 'CREATE_OPTIMIZATION';
  ADD_OPTIMIZATION: 'ADD_OPTIMIZATION';
  SET_LOADING: 'SET_LOADING';
  SET_ERROR: 'SET_ERROR';
  CLEAR_ERROR: 'CLEAR_ERROR';
}

export const analyticsActions = {
  FETCH_MODEL_STATUS: 'FETCH_MODEL_STATUS' as const,
  SET_MODEL_STATUS: 'SET_MODEL_STATUS' as const,
  CREATE_PREDICTION: 'CREATE_PREDICTION' as const,
  ADD_PREDICTION: 'ADD_PREDICTION' as const,
  CREATE_OPTIMIZATION: 'CREATE_OPTIMIZATION' as const,
  ADD_OPTIMIZATION: 'ADD_OPTIMIZATION' as const,
  SET_LOADING: 'SET_LOADING' as const,
  SET_ERROR: 'SET_ERROR' as const,
  CLEAR_ERROR: 'CLEAR_ERROR' as const
};

// Action creators
export const fetchModelStatus = () => ({
  type: analyticsActions.FETCH_MODEL_STATUS
});

export const setModelStatus = (status: any) => ({
  type: analyticsActions.SET_MODEL_STATUS,
  payload: status
});

export const createPrediction = (features: number[], modelType?: string) => ({
  type: analyticsActions.CREATE_PREDICTION,
  payload: { features, modelType }
});

export const addPrediction = (prediction: any) => ({
  type: analyticsActions.ADD_PREDICTION,
  payload: prediction
});

export const createOptimization = (type: string, data: any) => ({
  type: analyticsActions.CREATE_OPTIMIZATION,
  payload: { type, data }
});

export const addOptimization = (optimization: any) => ({
  type: analyticsActions.ADD_OPTIMIZATION,
  payload: optimization
});

export const setLoading = (loading: boolean) => ({
  type: analyticsActions.SET_LOADING,
  payload: loading
});

export const setError = (error: string | null) => ({
  type: analyticsActions.SET_ERROR,
  payload: error
});

export const clearError = () => ({
  type: analyticsActions.CLEAR_ERROR
});