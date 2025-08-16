// API endpoint definitions
export const endpoints = {
  // Analytics endpoints
  analytics: {
    predict: '/api/analytics/predict',
    forecastSales: '/api/analytics/forecast/sales',
    predictConversionRate: '/api/analytics/predict/conversion-rate',
    optimizeBudget: '/api/analytics/optimize/budget',
    optimizeKeywords: '/api/analytics/optimize/keywords',
    optimizeParameters: '/api/analytics/optimize/parameters',
    modelsStatus: '/api/analytics/models/status',
    trainModel: '/api/analytics/models/train',
    health: '/api/analytics/health'
  },

  // Scheduler endpoints
  scheduler: {
    tasks: '/api/scheduler/tasks',
    scheduleTask: '/api/scheduler/tasks/schedule',
    recurringTask: '/api/scheduler/tasks/recurring',
    getTask: (taskId: string) => `/api/scheduler/tasks/${taskId}`,
    cancelTask: (taskId: string) => `/api/scheduler/tasks/${taskId}`,
    statistics: '/api/scheduler/statistics',
    start: '/api/scheduler/start',
    stop: '/api/scheduler/stop',
    health: '/api/scheduler/health'
  },

  // Authentication endpoints
  auth: {
    login: '/api/auth/login',
    logout: '/api/auth/logout',
    refresh: '/api/auth/refresh',
    profile: '/api/auth/profile'
  },

  // Data management endpoints
  data: {
    campaigns: '/api/data/campaigns',
    getCampaign: (id: string) => `/api/data/campaigns/${id}`,
    predictions: '/api/data/predictions',
    optimizations: '/api/data/optimizations',
    export: '/api/data/export'
  },

  // System endpoints
  system: {
    health: '/health',
    status: '/api/system/status',
    metrics: '/api/system/metrics'
  },

  // Campaign Automation endpoints
  campaignAutomation: {
    campaigns: '/api/campaigns',
    getCampaign: (id: string) => `/api/campaigns/${id}`,
    createRule: (campaignId: string) => `/api/campaigns/${campaignId}/rules`,
    createSchedule: (campaignId: string) => `/api/campaigns/${campaignId}/schedule`,
    metrics: (campaignId: string) => `/api/monitoring/metrics/${campaignId}`,
    competitors: '/api/monitoring/competitors',
    updateMetrics: '/api/monitoring/update-metrics',
    predictAcos: (campaignId: string) => `/api/predictions/acos/${campaignId}`,
    pendingApprovals: '/api/approvals/pending',
    approveAction: (actionId: string) => `/api/approvals/${actionId}/approve`,
    rejectAction: (actionId: string) => `/api/approvals/${actionId}/reject`,
    dashboardOverview: '/api/dashboard/overview',
    campaignCharts: (campaignId: string) => `/api/dashboard/charts/${campaignId}`,
    calendar: (campaignId: string) => `/api/calendar/${campaignId}`,
    calendarEvents: (campaignId: string) => `/api/calendar/${campaignId}/events`,
    health: '/health'
  }
} as const;

export default endpoints;