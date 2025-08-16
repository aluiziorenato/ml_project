import { schedulerActions } from './actions';

interface Task {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled' | 'scheduled';
  task_type: string;
  result_data?: any;
  error_message?: string;
  execution_time: number;
  start_time: string;
  end_time?: string;
  metadata: Record<string, any>;
}

interface TaskStatistics {
  total_tasks: number;
  completed_tasks: number;
  failed_tasks: number;
  running_tasks: number;
  scheduled_tasks: number;
  success_rate: number;
  average_execution_time: number;
}

export interface SchedulerState {
  tasks: Task[];
  statistics: TaskStatistics | null;
  loading: boolean;
  error: string | null;
}

const initialState: SchedulerState = {
  tasks: [],
  statistics: null,
  loading: false,
  error: null
};

type SchedulerAction = 
  | { type: typeof schedulerActions.ADD_TASK; payload: Task }
  | { type: typeof schedulerActions.UPDATE_TASK; payload: { taskId: string; updates: Partial<Task> } }
  | { type: typeof schedulerActions.SET_TASKS; payload: Task[] }
  | { type: typeof schedulerActions.SET_STATISTICS; payload: TaskStatistics }
  | { type: typeof schedulerActions.SET_LOADING; payload: boolean }
  | { type: typeof schedulerActions.SET_ERROR; payload: string | null }
  | { type: typeof schedulerActions.CLEAR_ERROR };

export const schedulerReducer = (
  state = initialState,
  action: SchedulerAction
): SchedulerState => {
  switch (action.type) {
    case schedulerActions.ADD_TASK:
      return {
        ...state,
        tasks: [action.payload, ...state.tasks],
        loading: false,
        error: null
      };

    case schedulerActions.UPDATE_TASK:
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.task_id === action.payload.taskId
            ? { ...task, ...action.payload.updates }
            : task
        ),
        loading: false,
        error: null
      };

    case schedulerActions.SET_TASKS:
      return {
        ...state,
        tasks: action.payload,
        loading: false,
        error: null
      };

    case schedulerActions.SET_STATISTICS:
      return {
        ...state,
        statistics: action.payload,
        loading: false,
        error: null
      };

    case schedulerActions.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };

    case schedulerActions.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false
      };

    case schedulerActions.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    default:
      return state;
  }
};