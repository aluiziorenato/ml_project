import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

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

interface SchedulerState {
  // State
  tasks: Task[];
  statistics: TaskStatistics | null;
  loading: boolean;
  error: string | null;

  // Actions
  addTask: (task: Task) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  updateTaskStatus: (taskId: string, status: Task['status']) => void;
  setTasks: (tasks: Task[]) => void;
  setStatistics: (statistics: TaskStatistics) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  clearError: () => void;

  // Async actions
  createTask: (taskType: string, parameters: any) => Promise<string>;
  scheduleTask: (taskType: string, parameters: any, scheduledTime: Date) => Promise<string>;
  cancelTask: (taskId: string) => Promise<boolean>;
  getTaskStatistics: () => Promise<void>;
  loadTasks: (filters?: any) => Promise<void>;
}

export const useSchedulerStore = create<SchedulerState>()(
  devtools(
    persist(
      (set, get) => ({
        // Initial state
        tasks: [],
        statistics: null,
        loading: false,
        error: null,

        // Sync actions
        addTask: (task) =>
          set((state) => ({
            tasks: [task, ...state.tasks]
          })),

        updateTask: (taskId, updates) =>
          set((state) => ({
            tasks: state.tasks.map(task =>
              task.task_id === taskId ? { ...task, ...updates } : task
            )
          })),

        updateTaskStatus: (taskId, status) =>
          set((state) => ({
            tasks: state.tasks.map(task =>
              task.task_id === taskId ? { ...task, status } : task
            )
          })),

        setTasks: (tasks) =>
          set({ tasks }),

        setStatistics: (statistics) =>
          set({ statistics }),

        setLoading: (loading) =>
          set({ loading }),

        setError: (error) =>
          set({ error }),

        clearError: () =>
          set({ error: null }),

        // Async actions
        createTask: async (taskType, parameters) => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 800));
            
            const taskId = `task_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            const newTask: Task = {
              task_id: taskId,
              status: 'pending',
              task_type: taskType,
              execution_time: 0,
              start_time: new Date().toISOString(),
              metadata: { priority: 1, parameters }
            };
            
            get().addTask(newTask);
            
            // Simulate task execution
            setTimeout(() => {
              get().updateTaskStatus(taskId, 'running');
              
              setTimeout(() => {
                const success = Math.random() > 0.2; // 80% success rate
                get().updateTask(taskId, {
                  status: success ? 'completed' : 'failed',
                  execution_time: Math.random() * 5 + 1,
                  end_time: new Date().toISOString(),
                  result_data: success ? { result: 'Task completed successfully' } : undefined,
                  error_message: success ? undefined : 'Task execution failed'
                });
              }, Math.random() * 3000 + 1000); // 1-4 seconds execution
            }, 500);
            
            set({ loading: false });
            return taskId;
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to create task',
              loading: false 
            });
            throw error;
          }
        },

        scheduleTask: async (taskType, parameters, scheduledTime) => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 600));
            
            const taskId = `scheduled_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
            
            const newTask: Task = {
              task_id: taskId,
              status: 'scheduled',
              task_type: taskType,
              execution_time: 0,
              start_time: scheduledTime.toISOString(),
              metadata: { priority: 1, parameters, scheduled_time: scheduledTime.toISOString() }
            };
            
            get().addTask(newTask);
            
            set({ loading: false });
            return taskId;
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to schedule task',
              loading: false 
            });
            throw error;
          }
        },

        cancelTask: async (taskId) => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 400));
            
            const task = get().tasks.find(t => t.task_id === taskId);
            if (!task) {
              throw new Error('Task not found');
            }
            
            if (task.status === 'pending' || task.status === 'scheduled') {
              get().updateTaskStatus(taskId, 'cancelled');
              set({ loading: false });
              return true;
            } else {
              throw new Error('Cannot cancel task in current status');
            }
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to cancel task',
              loading: false 
            });
            return false;
          }
        },

        getTaskStatistics: async () => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 500));
            
            const tasks = get().tasks;
            const totalTasks = tasks.length;
            const completedTasks = tasks.filter(t => t.status === 'completed').length;
            const failedTasks = tasks.filter(t => t.status === 'failed').length;
            const runningTasks = tasks.filter(t => t.status === 'running').length;
            const scheduledTasks = tasks.filter(t => t.status === 'scheduled').length;
            
            const successRate = totalTasks > 0 ? completedTasks / totalTasks : 0;
            
            const completedTasksWithTime = tasks.filter(t => t.status === 'completed' && t.execution_time > 0);
            const averageExecutionTime = completedTasksWithTime.length > 0
              ? completedTasksWithTime.reduce((sum, t) => sum + t.execution_time, 0) / completedTasksWithTime.length
              : 0;
            
            const statistics: TaskStatistics = {
              total_tasks: totalTasks,
              completed_tasks: completedTasks,
              failed_tasks: failedTasks,
              running_tasks: runningTasks,
              scheduled_tasks: scheduledTasks,
              success_rate: successRate,
              average_execution_time: averageExecutionTime
            };
            
            set({ statistics, loading: false });
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to get statistics',
              loading: false 
            });
          }
        },

        loadTasks: async (filters = {}) => {
          try {
            set({ loading: true, error: null });
            
            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 700));
            
            // This would typically fetch from API
            // For now, we'll keep existing tasks and potentially add some mock data
            const existingTasks = get().tasks;
            if (existingTasks.length === 0) {
              // Add some mock tasks if none exist
              const mockTasks: Task[] = [
                {
                  task_id: 'mock_task_1',
                  status: 'completed',
                  task_type: 'analytics_prediction',
                  result_data: { prediction: 0.025 },
                  execution_time: 2.3,
                  start_time: new Date(Date.now() - 3600000).toISOString(),
                  end_time: new Date(Date.now() - 3595000).toISOString(),
                  metadata: { priority: 1 }
                },
                {
                  task_id: 'mock_task_2',
                  status: 'running',
                  task_type: 'model_training',
                  execution_time: 0,
                  start_time: new Date(Date.now() - 120000).toISOString(),
                  metadata: { priority: 2 }
                }
              ];
              
              set({ tasks: mockTasks, loading: false });
            } else {
              set({ loading: false });
            }
          } catch (error) {
            set({ 
              error: error instanceof Error ? error.message : 'Failed to load tasks',
              loading: false 
            });
          }
        }
      }),
      {
        name: 'scheduler-store',
        partialize: (state) => ({
          tasks: state.tasks.slice(0, 100), // Persist only last 100 tasks
          statistics: state.statistics
        })
      }
    ),
    {
      name: 'scheduler-store'
    }
  )
);