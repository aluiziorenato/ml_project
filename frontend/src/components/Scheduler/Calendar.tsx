import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Calendar as CalendarIcon, ChevronLeft, ChevronRight } from 'lucide-react';

interface ScheduledTask {
  id: string;
  title: string;
  task_type: string;
  scheduled_time: Date;
  status: 'scheduled' | 'running' | 'completed' | 'failed';
  priority: number;
  duration?: number;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  tasks: ScheduledTask[];
}

const Calendar: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');

  useEffect(() => {
    loadScheduledTasks();
  }, [currentDate]);

  const loadScheduledTasks = async () => {
    // In a real app, this would call the API to get scheduled tasks for the current period
    const mockTasks: ScheduledTask[] = [
      {
        id: 'task_1',
        title: 'Daily Model Training',
        task_type: 'model_training',
        scheduled_time: new Date(currentDate.getFullYear(), currentDate.getMonth(), 15, 9, 0),
        status: 'scheduled',
        priority: 2,
        duration: 30
      },
      {
        id: 'task_2',
        title: 'Analytics Report Generation',
        task_type: 'analytics_prediction',
        scheduled_time: new Date(currentDate.getFullYear(), currentDate.getMonth(), 15, 14, 30),
        status: 'scheduled',
        priority: 1,
        duration: 15
      },
      {
        id: 'task_3',
        title: 'System Health Check',
        task_type: 'health_check',
        scheduled_time: new Date(currentDate.getFullYear(), currentDate.getMonth(), 18, 8, 0),
        status: 'scheduled',
        priority: 1,
        duration: 10
      },
      {
        id: 'task_4',
        title: 'Data Backup',
        task_type: 'backup',
        scheduled_time: new Date(currentDate.getFullYear(), currentDate.getMonth(), 20, 23, 0),
        status: 'scheduled',
        priority: 3,
        duration: 60
      },
      {
        id: 'task_5',
        title: 'Optimization Analysis',
        task_type: 'optimization',
        scheduled_time: new Date(currentDate.getFullYear(), currentDate.getMonth(), 22, 10, 0),
        status: 'scheduled',
        priority: 2,
        duration: 45
      }
    ];

    setTasks(mockTasks);
  };

  const getDaysInMonth = (date: Date): CalendarDay[] => {
    const year = date.getFullYear();
    const month = date.getMonth();
    
    const firstDayOfMonth = new Date(year, month, 1);
    const lastDayOfMonth = new Date(year, month + 1, 0);
    const firstDayOfWeek = firstDayOfMonth.getDay();
    
    const days: CalendarDay[] = [];
    
    // Add previous month's days
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const date = new Date(year, month, -i);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: []
      });
    }
    
    // Add current month's days
    for (let day = 1; day <= lastDayOfMonth.getDate(); day++) {
      const date = new Date(year, month, day);
      const isToday = 
        date.getDate() === new Date().getDate() &&
        date.getMonth() === new Date().getMonth() &&
        date.getFullYear() === new Date().getFullYear();
      
      const dayTasks = tasks.filter(task => 
        task.scheduled_time.getDate() === day &&
        task.scheduled_time.getMonth() === month &&
        task.scheduled_time.getFullYear() === year
      );
      
      days.push({
        date,
        isCurrentMonth: true,
        isToday,
        tasks: dayTasks
      });
    }
    
    // Add next month's days to fill the grid
    const remainingDays = 42 - days.length; // 6 weeks * 7 days
    for (let day = 1; day <= remainingDays; day++) {
      const date = new Date(year, month + 1, day);
      days.push({
        date,
        isCurrentMonth: false,
        isToday: false,
        tasks: []
      });
    }
    
    return days;
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => {
      const newDate = new Date(prev);
      if (direction === 'prev') {
        newDate.setMonth(prev.getMonth() - 1);
      } else {
        newDate.setMonth(prev.getMonth() + 1);
      }
      return newDate;
    });
  };

  const getTaskTypeColor = (taskType: string) => {
    const colors = {
      model_training: 'bg-blue-500',
      analytics_prediction: 'bg-green-500',
      health_check: 'bg-yellow-500',
      backup: 'bg-purple-500',
      optimization: 'bg-red-500',
      data_processing: 'bg-indigo-500'
    };
    return colors[taskType as keyof typeof colors] || 'bg-gray-500';
  };

  const getPriorityIndicator = (priority: number) => {
    if (priority === 3) return '🔴'; // High
    if (priority === 2) return '🟡'; // Medium
    return '🟢'; // Low
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    });
  };

  const days = getDaysInMonth(currentDate);
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  const weekDays = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-blue-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-7xl mx-auto"
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-4">
            <CalendarIcon className="w-8 h-8 text-indigo-600" />
            <h1 className="text-4xl font-bold text-gray-900">Task Calendar</h1>
          </div>
          
          <div className="flex items-center gap-4">
            {/* View Mode Selector */}
            <div className="flex bg-white rounded-lg border border-gray-200 overflow-hidden">
              {['month', 'week', 'day'].map((mode) => (
                <button
                  key={mode}
                  onClick={() => setViewMode(mode as any)}
                  className={`px-4 py-2 text-sm font-medium transition-colors ${
                    viewMode === mode
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  {mode.charAt(0).toUpperCase() + mode.slice(1)}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Calendar Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mb-8"
        >
          <div className="flex items-center justify-between mb-6">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigateMonth('prev')}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </motion.button>
            
            <h2 className="text-2xl font-bold text-gray-900">
              {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
            </h2>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigateMonth('next')}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
            >
              <ChevronRight className="w-5 h-5" />
            </motion.button>
          </div>

          {/* Week Days Header */}
          <div className="grid grid-cols-7 gap-1 mb-2">
            {weekDays.map((day) => (
              <div key={day} className="p-3 text-center text-sm font-semibold text-gray-600">
                {day}
              </div>
            ))}
          </div>

          {/* Calendar Grid */}
          <div className="grid grid-cols-7 gap-1">
            {days.map((day, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.01 }}
                className={`
                  min-h-[120px] p-2 border border-gray-100 rounded-lg cursor-pointer
                  transition-colors hover:bg-gray-50
                  ${day.isCurrentMonth ? 'bg-white' : 'bg-gray-50'}
                  ${day.isToday ? 'ring-2 ring-indigo-500' : ''}
                  ${selectedDate?.getTime() === day.date.getTime() ? 'bg-indigo-50' : ''}
                `}
                onClick={() => setSelectedDate(day.date)}
              >
                <div className={`
                  text-sm font-medium mb-2
                  ${day.isCurrentMonth ? 'text-gray-900' : 'text-gray-400'}
                  ${day.isToday ? 'text-indigo-600 font-bold' : ''}
                `}>
                  {day.date.getDate()}
                </div>
                
                {/* Tasks for this day */}
                <div className="space-y-1">
                  {day.tasks.slice(0, 3).map((task) => (
                    <motion.div
                      key={task.id}
                      whileHover={{ scale: 1.02 }}
                      className={`
                        px-2 py-1 rounded text-xs text-white truncate
                        ${getTaskTypeColor(task.task_type)}
                      `}
                      title={`${task.title} - ${formatTime(task.scheduled_time)}`}
                    >
                      <div className="flex items-center gap-1">
                        <span>{getPriorityIndicator(task.priority)}</span>
                        <span className="truncate">{task.title}</span>
                      </div>
                      <div className="text-xs opacity-75">
                        {formatTime(task.scheduled_time)}
                      </div>
                    </motion.div>
                  ))}
                  
                  {day.tasks.length > 3 && (
                    <div className="text-xs text-gray-500 px-2">
                      +{day.tasks.length - 3} more
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Task Details Panel */}
        {selectedDate && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="bg-white rounded-xl shadow-lg border border-gray-200 p-6"
          >
            <h3 className="text-xl font-semibold text-gray-900 mb-4">
              Tasks for {selectedDate.toLocaleDateString('en-US', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}
            </h3>
            
            {(() => {
              const dayTasks = tasks.filter(task =>
                task.scheduled_time.getDate() === selectedDate.getDate() &&
                task.scheduled_time.getMonth() === selectedDate.getMonth() &&
                task.scheduled_time.getFullYear() === selectedDate.getFullYear()
              ).sort((a, b) => a.scheduled_time.getTime() - b.scheduled_time.getTime());

              if (dayTasks.length === 0) {
                return (
                  <div className="text-center py-8 text-gray-500">
                    <CalendarIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No tasks scheduled for this day</p>
                  </div>
                );
              }

              return (
                <div className="space-y-4">
                  {dayTasks.map((task) => (
                    <motion.div
                      key={task.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.3 }}
                      className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg"
                    >
                      <div className={`w-4 h-4 rounded-full ${getTaskTypeColor(task.task_type)}`} />
                      
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-semibold text-gray-900">{task.title}</h4>
                          <span>{getPriorityIndicator(task.priority)}</span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <span>{formatTime(task.scheduled_time)}</span>
                          <span className="capitalize">{task.task_type.replace('_', ' ')}</span>
                          {task.duration && <span>{task.duration} min</span>}
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2">
                        <span className={`
                          px-2 py-1 rounded-full text-xs font-medium
                          ${task.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                            task.status === 'running' ? 'bg-yellow-100 text-yellow-800' :
                            task.status === 'completed' ? 'bg-green-100 text-green-800' :
                            'bg-red-100 text-red-800'}
                        `}>
                          {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                        </span>
                      </div>
                    </motion.div>
                  ))}
                </div>
              );
            })()}
          </motion.div>
        )}

        {/* Task Type Legend */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 bg-white rounded-xl shadow-lg border border-gray-200 p-6"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Task Type Legend</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
            {[
              { type: 'model_training', label: 'Model Training' },
              { type: 'analytics_prediction', label: 'Analytics' },
              { type: 'health_check', label: 'Health Check' },
              { type: 'backup', label: 'Backup' },
              { type: 'optimization', label: 'Optimization' },
              { type: 'data_processing', label: 'Data Processing' }
            ].map(({ type, label }) => (
              <div key={type} className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getTaskTypeColor(type)}`} />
                <span className="text-sm text-gray-700">{label}</span>
              </div>
            ))}
          </div>
          
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-900 mb-2">Priority Indicators</h4>
            <div className="flex items-center gap-6">
              <div className="flex items-center gap-2">
                <span>🔴</span>
                <span className="text-sm text-gray-700">High Priority</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🟡</span>
                <span className="text-sm text-gray-700">Medium Priority</span>
              </div>
              <div className="flex items-center gap-2">
                <span>🟢</span>
                <span className="text-sm text-gray-700">Low Priority</span>
              </div>
            </div>
          </div>
        </motion.div>
      </motion.div>
    </div>
  );
};

export default Calendar;