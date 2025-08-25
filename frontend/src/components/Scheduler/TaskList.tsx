import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useSchedulerStore } from '../../store/scheduler/store';
import { apiClient } from '../../api/client';

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

interface TaskFilter {
  status?: string;
  task_type?: string;
}

const STATUS_COLORS = {
  pending: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  running: 'bg-blue-100 text-blue-800 border-blue-200',
  completed: 'bg-green-100 text-green-800 border-green-200',
  failed: 'bg-red-100 text-red-800 border-red-200',
  cancelled: 'bg-gray-100 text-gray-800 border-gray-200',
  scheduled: 'bg-purple-100 text-purple-800 border-purple-200'
};

const STATUS_ICONS = {
  pending: '⏳',
  running: '🔄',
  completed: '✅',
  failed: '❌',
  cancelled: '⛔',
  scheduled: '📅'
};

const TaskList: React.FC = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<TaskFilter>({});
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const { addTask, updateTaskStatus, getTaskStatistics, statistics } = useSchedulerStore();

  useEffect(() => {
    loadTasks();
    const interval = setInterval(loadTasks, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [filter]);

  const loadTasks = async () => {
    try {
      setError(null);
      
      // In a real app, this would call the API
      // const response = await apiClient.get('/scheduler/tasks', { params: filter });
      // setTasks(response.data.tasks);

      // For demo, use mock data
      const mockTasks: Task[] = [
        {
          task_id: 'task_001',
          status: 'completed',
          task_type: 'analytics_prediction',
          result_data: { prediction: 0.025, confidence: 0.85 },
          execution_time: 1.2,
          start_time: new Date(Date.now() - 3600000).toISOString(),
          end_time: new Date(Date.now() - 3595000).toISOString(),
          metadata: { priority: 1 }
        },
        {
          task_id: 'task_002',
          status: 'running',
          task_type: 'model_training',
          execution_time: 0,
          start_time: new Date(Date.now() - 120000).toISOString(),
          metadata: { priority: 2 }
        },
        {
          task_id: 'task_003',
          status: 'scheduled',
          task_type: 'optimization',
          execution_time: 0,
          start_time: new Date(Date.now() + 1800000).toISOString(),
          metadata: { priority: 1 }
        },
        {
          task_id: 'task_004',
          status: 'failed',
          task_type: 'data_processing',
          error_message: 'Connection timeout',
          execution_time: 5.0,
          start_time: new Date(Date.now() - 7200000).toISOString(),
          end_time: new Date(Date.now() - 7195000).toISOString(),
          metadata: { priority: 1 }
        }
      ];

      // Apply filters
      let filteredTasks = mockTasks;
      if (filter.status) {
        filteredTasks = filteredTasks.filter(task => task.status === filter.status);
      }
      if (filter.task_type) {
        filteredTasks = filteredTasks.filter(task => task.task_type === filter.task_type);
      }

      setTasks(filteredTasks);
      await getTaskStatistics();
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async (taskData: { task_type: string; parameters: any }) => {
    try {
      const response = await apiClient.post('/scheduler/tasks', {
        task_type: taskData.task_type,
        parameters: taskData.parameters,
        priority: 1
      });

      const newTask: Task = {
        task_id: response.data.task_id,
        status: 'pending',
        task_type: taskData.task_type,
        execution_time: 0,
        start_time: new Date().toISOString(),
        metadata: { priority: 1 }
      };

      setTasks(prev => [newTask, ...prev]);
      addTask(newTask);
      setShowCreateModal(false);
      
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleCancelTask = async (taskId: string) => {
    try {
      await apiClient.delete(`/scheduler/tasks/${taskId}`);
      
      setTasks(prev => 
        prev.map(task => 
          task.task_id === taskId 
            ? { ...task, status: 'cancelled' as const }
            : task
        )
      );
      
      updateTaskStatus(taskId, 'cancelled');
      
    } catch (err) {
      setError('Failed to cancel task');
    }
  };

  const getStatusBadge = (status: string) => {
    const colorClass = STATUS_COLORS[status as keyof typeof STATUS_COLORS] || STATUS_COLORS.pending;
    const icon = STATUS_ICONS[status as keyof typeof STATUS_ICONS] || STATUS_ICONS.pending;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${colorClass}`}>
        <span className="mr-1">{icon}</span>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    );
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 flex items-center justify-center">
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 mb-2">Task Manager</h1>
            <p className="text-gray-600">Monitor and manage scheduled tasks</p>
          </div>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
          >
            Create Task
          </motion.button>
        </div>

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg"
          >
            {error}
            <button
              onClick={() => setError(null)}
              className="ml-4 text-red-500 hover:text-red-700"
            >
              ✕
            </button>
          </motion.div>
        )}

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Total Tasks</p>
                  <p className="text-3xl font-bold text-purple-600">{statistics.total_tasks}</p>
                </div>
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">📋</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Success Rate</p>
                  <p className="text-3xl font-bold text-green-600">
                    {(statistics.success_rate * 100).toFixed(1)}%
                  </p>
                </div>
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">✅</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Running Tasks</p>
                  <p className="text-3xl font-bold text-blue-600">{statistics.running_tasks}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">🔄</span>
                </div>
              </div>
            </motion.div>

            <motion.div
              whileHover={{ scale: 1.02 }}
              className="bg-white p-6 rounded-xl shadow-lg border border-gray-200"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500">Avg Duration</p>
                  <p className="text-3xl font-bold text-orange-600">
                    {formatDuration(statistics.average_execution_time)}
                  </p>
                </div>
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                  <span className="text-2xl">⏱️</span>
                </div>
              </div>
            </motion.div>
          </div>
        )}

        {/* Filters */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-white p-6 rounded-xl shadow-lg border border-gray-200 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Status</label>
              <select
                value={filter.status || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, status: e.target.value || undefined }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Statuses</option>
                <option value="pending">Pending</option>
                <option value="running">Running</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="cancelled">Cancelled</option>
                <option value="scheduled">Scheduled</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
              <select
                value={filter.task_type || ''}
                onChange={(e) => setFilter(prev => ({ ...prev, task_type: e.target.value || undefined }))}
                className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">All Types</option>
                <option value="analytics_prediction">Analytics Prediction</option>
                <option value="model_training">Model Training</option>
                <option value="optimization">Optimization</option>
                <option value="data_processing">Data Processing</option>
                <option value="health_check">Health Check</option>
              </select>
            </div>

            <div className="flex items-end">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setFilter({})}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
              >
                Clear Filters
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Task List */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="bg-white rounded-xl shadow-lg border border-gray-200"
        >
          <div className="p-6 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Tasks ({tasks.length})</h3>
          </div>

          <div className="divide-y divide-gray-200">
            <AnimatePresence>
              {tasks.map((task, index) => (
                <motion.div
                  key={task.task_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-6 hover:bg-gray-50 transition-colors cursor-pointer"
                  onClick={() => setSelectedTask(task)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h4 className="text-lg font-semibold text-gray-900">{task.task_id}</h4>
                        {getStatusBadge(task.status)}
                        <span className="text-sm text-gray-500 capitalize">
                          {task.task_type.replace('_', ' ')}
                        </span>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm text-gray-600">
                        <span>
                          Started: {new Date(task.start_time).toLocaleString()}
                        </span>
                        {task.end_time && (
                          <span>
                            Duration: {formatDuration(task.execution_time)}
                          </span>
                        )}
                        <span className="font-medium">
                          Priority: {task.metadata.priority || 1}
                        </span>
                      </div>

                      {task.error_message && (
                        <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                          Error: {task.error_message}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center gap-2">
                      {task.status === 'pending' || task.status === 'scheduled' ? (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleCancelTask(task.task_id);
                          }}
                          className="px-3 py-1 text-sm bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
                        >
                          Cancel
                        </motion.button>
                      ) : null}
                      
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedTask(task);
                        }}
                        className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200 transition-colors"
                      >
                        Details
                      </motion.button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {tasks.length === 0 && (
              <div className="p-12 text-center text-gray-500">
                <span className="text-4xl mb-4 block">📝</span>
                <p className="text-lg">No tasks found</p>
                <p className="text-sm">Try adjusting your filters or create a new task</p>
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>

      {/* Task Detail Modal */}
      <AnimatePresence>
        {selectedTask && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
            onClick={() => setSelectedTask(null)}
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h3 className="text-xl font-semibold text-gray-900">Task Details</h3>
                  <button
                    onClick={() => setSelectedTask(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    ✕
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Task ID</label>
                  <p className="text-lg font-mono">{selectedTask.task_id}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  {getStatusBadge(selectedTask.status)}
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Type</label>
                  <p className="capitalize">{selectedTask.task_type.replace('_', ' ')}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Start Time</label>
                  <p>{new Date(selectedTask.start_time).toLocaleString()}</p>
                </div>
                
                {selectedTask.end_time && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Time</label>
                    <p>{new Date(selectedTask.end_time).toLocaleString()}</p>
                  </div>
                )}
                
                {selectedTask.execution_time > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Execution Time</label>
                    <p>{formatDuration(selectedTask.execution_time)}</p>
                  </div>
                )}
                
                {selectedTask.result_data && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Result</label>
                    <pre className="bg-gray-50 p-3 rounded-lg text-sm overflow-auto">
                      {JSON.stringify(selectedTask.result_data, null, 2)}
                    </pre>
                  </div>
                )}
                
                {selectedTask.error_message && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Error</label>
                    <p className="text-red-600 bg-red-50 p-3 rounded-lg">
                      {selectedTask.error_message}
                    </p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Metadata</label>
                  <pre className="bg-gray-50 p-3 rounded-lg text-sm overflow-auto">
                    {JSON.stringify(selectedTask.metadata, null, 2)}
                  </pre>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Create Task Modal */}
      <AnimatePresence>
        {showCreateModal && (
          <CreateTaskModal
            onClose={() => setShowCreateModal(false)}
            onSubmit={handleCreateTask}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

// Create Task Modal Component
const CreateTaskModal: React.FC<{
  onClose: () => void;
  onSubmit: (data: { task_type: string; parameters: any }) => void;
}> = ({ onClose, onSubmit }) => {
  const [taskType, setTaskType] = useState('analytics_prediction');
  const [parameters, setParameters] = useState('{}');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const parsedParams = JSON.parse(parameters);
      onSubmit({ task_type: taskType, parameters: parsedParams });
    } catch (err) {
      alert('Invalid JSON in parameters');
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
      onClick={onClose}
    >
      <motion.div
        initial={{ scale: 0.95, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.95, opacity: 0 }}
        className="bg-white rounded-xl shadow-xl max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-semibold text-gray-900">Create New Task</h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              ✕
            </button>
          </div>
        </div>
        
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Task Type</label>
            <select
              value={taskType}
              onChange={(e) => setTaskType(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="analytics_prediction">Analytics Prediction</option>
              <option value="model_training">Model Training</option>
              <option value="optimization">Optimization</option>
              <option value="data_processing">Data Processing</option>
              <option value="health_check">Health Check</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Parameters (JSON)</label>
            <textarea
              value={parameters}
              onChange={(e) => setParameters(e.target.value)}
              rows={6}
              className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-sm"
              placeholder='{"key": "value"}'
            />
          </div>
          
          <div className="flex gap-3 pt-4">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              className="flex-1 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors font-medium"
            >
              Create Task
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="button"
              onClick={onClose}
              className="flex-1 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Cancel
            </motion.button>
          </div>
        </form>
      </motion.div>
    </motion.div>
  );
};

export default TaskList;