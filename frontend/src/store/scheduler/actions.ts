// Scheduler store actions
export interface SchedulerActions {
  CREATE_TASK: 'CREATE_TASK';
  ADD_TASK: 'ADD_TASK';
  UPDATE_TASK: 'UPDATE_TASK';
  CANCEL_TASK: 'CANCEL_TASK';
  LOAD_TASKS: 'LOAD_TASKS';
  SET_TASKS: 'SET_TASKS';
  GET_STATISTICS: 'GET_STATISTICS';
  SET_STATISTICS: 'SET_STATISTICS';
  SET_LOADING: 'SET_LOADING';
  SET_ERROR: 'SET_ERROR';
  CLEAR_ERROR: 'CLEAR_ERROR';
}

export const schedulerActions = {
  CREATE_TASK: 'CREATE_TASK' as const,
  ADD_TASK: 'ADD_TASK' as const,
  UPDATE_TASK: 'UPDATE_TASK' as const,
  CANCEL_TASK: 'CANCEL_TASK' as const,
  LOAD_TASKS: 'LOAD_TASKS' as const,
  SET_TASKS: 'SET_TASKS' as const,
  GET_STATISTICS: 'GET_STATISTICS' as const,
  SET_STATISTICS: 'SET_STATISTICS' as const,
  SET_LOADING: 'SET_LOADING' as const,
  SET_ERROR: 'SET_ERROR' as const,
  CLEAR_ERROR: 'CLEAR_ERROR' as const
};

// Action creators
export const createTask = (taskType: string, parameters: any) => ({
  type: schedulerActions.CREATE_TASK,
  payload: { taskType, parameters }
});

export const addTask = (task: any) => ({
  type: schedulerActions.ADD_TASK,
  payload: task
});

export const updateTask = (taskId: string, updates: any) => ({
  type: schedulerActions.UPDATE_TASK,
  payload: { taskId, updates }
});

export const cancelTask = (taskId: string) => ({
  type: schedulerActions.CANCEL_TASK,
  payload: taskId
});

export const loadTasks = (filters?: any) => ({
  type: schedulerActions.LOAD_TASKS,
  payload: filters
});

export const setTasks = (tasks: any[]) => ({
  type: schedulerActions.SET_TASKS,
  payload: tasks
});

export const getStatistics = () => ({
  type: schedulerActions.GET_STATISTICS
});

export const setStatistics = (statistics: any) => ({
  type: schedulerActions.SET_STATISTICS,
  payload: statistics
});

export const setLoading = (loading: boolean) => ({
  type: schedulerActions.SET_LOADING,
  payload: loading
});

export const setError = (error: string | null) => ({
  type: schedulerActions.SET_ERROR,
  payload: error
});

export const clearError = () => ({
  type: schedulerActions.CLEAR_ERROR
});