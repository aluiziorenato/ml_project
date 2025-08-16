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

  // Mercado Libre Services endpoints
  meli: {
    // Orders service
    orders: {
      list: '/meli/orders_service/orders',
      details: (orderId: string) => `/meli/orders_service/orders/${orderId}`,
      analytics: '/meli/orders_service/analytics',
      health: '/meli/orders_service/health'
    },
    
    // Shipments service
    shipments: {
      list: '/meli/shipments_service/shipments',
      tracking: (shipmentId: string) => `/meli/shipments_service/shipments/${shipmentId}/tracking`,
      options: '/meli/shipments_service/shipping_options',
      health: '/meli/shipments_service/health'
    },
    
    // Messages service
    messages: {
      list: '/meli/messages_service/messages',
      details: (messageId: string) => `/meli/messages_service/messages/${messageId}`,
      aiSuggestions: '/meli/messages_service/ai_suggestions',
      health: '/meli/messages_service/health'
    },
    
    // Questions service (Q&A)
    questions: {
      list: '/meli/questions_service/questions',
      details: (questionId: string) => `/meli/questions_service/questions/${questionId}`,
      answer: '/meli/questions_service/answers',
      aiSuggestions: '/meli/questions_service/ai_suggestions',
      analytics: '/meli/questions_service/analytics',
      health: '/meli/questions_service/health'
    },
    
    // Inventory service
    inventory: {
      list: '/meli/inventory_service/inventory',
      alerts: '/meli/inventory_service/alerts',
      updateStock: (itemId: string) => `/meli/inventory_service/items/${itemId}/stock`,
      health: '/meli/inventory_service/health'
    },
    
    // Reputation service
    reputation: {
      details: (userId: string) => `/meli/reputation_service/reputation/${userId}`,
      analytics: '/meli/reputation_service/analytics',
      health: '/meli/reputation_service/health'
    },
    
    // Global status
    status: '/meli/status'
  }
} as const;

export default endpoints;