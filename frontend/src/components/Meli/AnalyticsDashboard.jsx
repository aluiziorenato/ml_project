import React, { useState, useEffect } from 'react';
import { endpoints } from '../../api/endpoints';

const AnalyticsDashboard = ({ userId, accessToken }) => {
  const [loading, setLoading] = useState(true);
  const [analytics, setAnalytics] = useState({
    orders: null,
    questions: null,
    reputation: null,
    services: null
  });
  const [dateRange, setDateRange] = useState({
    from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    to: new Date().toISOString().split('T')[0]
  });

  useEffect(() => {
    if (userId && accessToken) {
      fetchAllAnalytics();
    }
  }, [userId, accessToken, dateRange]);

  const fetchAllAnalytics = async () => {
    try {
      setLoading(true);
      
      // Fetch analytics from all services
      const [ordersRes, questionsRes, reputationRes, servicesRes] = await Promise.allSettled([
        fetchOrdersAnalytics(),
        fetchQuestionsAnalytics(),
        fetchReputationAnalytics(),
        fetchServicesStatus()
      ]);

      setAnalytics({
        orders: ordersRes.status === 'fulfilled' ? ordersRes.value : null,
        questions: questionsRes.status === 'fulfilled' ? questionsRes.value : null,
        reputation: reputationRes.status === 'fulfilled' ? reputationRes.value : null,
        services: servicesRes.status === 'fulfilled' ? servicesRes.value : null
      });
    } catch (error) {
      console.error('Error fetching analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchOrdersAnalytics = async () => {
    const params = new URLSearchParams({
      user_id: userId,
      date_from: dateRange.from,
      date_to: dateRange.to
    });

    const response = await fetch(`${endpoints.meli.orders.analytics}?${params}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    const data = await response.json();
    return data.success ? data.data : null;
  };

  const fetchQuestionsAnalytics = async () => {
    const params = new URLSearchParams({
      user_id: userId,
      date_from: dateRange.from,
      date_to: dateRange.to
    });

    const response = await fetch(`${endpoints.meli.questions.analytics}?${params}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    const data = await response.json();
    return data.success ? data.data : null;
  };

  const fetchReputationAnalytics = async () => {
    const params = new URLSearchParams({
      user_id: userId,
      date_from: dateRange.from,
      date_to: dateRange.to
    });

    const response = await fetch(`${endpoints.meli.reputation.analytics}?${params}`, {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });

    const data = await response.json();
    return data.success ? data.data : null;
  };

  const fetchServicesStatus = async () => {
    const response = await fetch(endpoints.meli.status);
    const data = await response.json();
    return data.success ? data : null;
  };

  const MetricCard = ({ title, value, subtitle, color = "blue", trend = null }) => (
    <div className="bg-white p-6 rounded-lg shadow border">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className={`text-2xl font-bold text-${color}-600`}>{value}</p>
          {subtitle && <p className="text-sm text-gray-500">{subtitle}</p>}
        </div>
        {trend && (
          <div className={`text-${trend > 0 ? 'green' : 'red'}-600`}>
            <span className="text-sm font-medium">
              {trend > 0 ? '↗' : '↘'} {Math.abs(trend)}%
            </span>
          </div>
        )}
      </div>
    </div>
  );

  const ServiceStatusCard = ({ services }) => (
    <div className="bg-white p-6 rounded-lg shadow border">
      <h3 className="text-lg font-semibold mb-4">Status dos Serviços</h3>
      <div className="space-y-3">
        {Object.entries(services?.services || {}).map(([service, status]) => (
          <div key={service} className="flex items-center justify-between">
            <span className="text-sm capitalize">{service.replace('_', ' ')}</span>
            <span className={`px-2 py-1 text-xs rounded-full ${
              status.status === 'healthy' 
                ? 'bg-green-100 text-green-800' 
                : 'bg-red-100 text-red-800'
            }`}>
              {status.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  const OptimizationSuggestions = ({ suggestions }) => {
    if (!suggestions?.length) return null;

    return (
      <div className="bg-white p-6 rounded-lg shadow border">
        <h3 className="text-lg font-semibold mb-4">Sugestões de Otimização</h3>
        <div className="space-y-3">
          {suggestions.slice(0, 5).map((suggestion, index) => (
            <div key={index} className="p-3 border-l-4 border-blue-500 bg-blue-50">
              <p className="text-sm text-gray-900">{suggestion.suggestion}</p>
              <p className="text-xs text-blue-600 mt-1">
                Impacto: {suggestion.impact} | Tipo: {suggestion.type}
              </p>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          Dashboard de Analytics - Mercado Libre
        </h2>
        
        {/* Date Range Selector */}
        <div className="flex space-x-4 mb-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">Data Inicial</label>
            <input
              type="date"
              value={dateRange.from}
              onChange={(e) => setDateRange({...dateRange, from: e.target.value})}
              className="mt-1 block border rounded-md px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Data Final</label>
            <input
              type="date"
              value={dateRange.to}
              onChange={(e) => setDateRange({...dateRange, to: e.target.value})}
              className="mt-1 block border rounded-md px-3 py-2"
            />
          </div>
          <div className="flex items-end">
            <button
              onClick={fetchAllAnalytics}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              Atualizar
            </button>
          </div>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {analytics.orders?.analytics && (
          <>
            <MetricCard
              title="Total de Vendas"
              value={`R$ ${analytics.orders.analytics.total_revenue?.toLocaleString() || '0'}`}
              subtitle={`${analytics.orders.analytics.total_orders || 0} pedidos`}
              color="green"
            />
            <MetricCard
              title="Ticket Médio"
              value={`R$ ${analytics.orders.analytics.avg_order_value?.toFixed(2) || '0'}`}
              subtitle="Por pedido"
              color="blue"
            />
          </>
        )}
        
        {analytics.questions?.analytics && (
          <>
            <MetricCard
              title="Taxa de Resposta"
              value={`${Math.round(analytics.questions.analytics.answer_rate * 100) || 0}%`}
              subtitle={`${analytics.questions.analytics.answered || 0} de ${analytics.questions.analytics.total || 0}`}
              color="purple"
            />
            <MetricCard
              title="Perguntas Pendentes"
              value={analytics.questions.analytics.unanswered || 0}
              subtitle="Aguardando resposta"
              color="orange"
            />
          </>
        )}
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
        {/* Reputation Metrics */}
        {analytics.reputation?.analytics && (
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Reputação</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span>Avaliação Média</span>
                <span className="font-semibold">
                  {analytics.reputation.analytics.avg_rating?.toFixed(1) || 'N/A'} ⭐
                </span>
              </div>
              <div className="flex justify-between">
                <span>Total de Avaliações</span>
                <span>{analytics.reputation.analytics.total_reviews || 0}</span>
              </div>
              <div className="flex justify-between">
                <span>Avaliações Negativas</span>
                <span className="text-red-600">
                  {analytics.reputation.analytics.negative_reviews_count || 0}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Order Status Distribution */}
        {analytics.orders?.analytics?.status_distribution && (
          <div className="bg-white p-6 rounded-lg shadow border">
            <h3 className="text-lg font-semibold mb-4">Status dos Pedidos</h3>
            <div className="space-y-2">
              {Object.entries(analytics.orders.analytics.status_distribution).map(([status, count]) => (
                <div key={status} className="flex justify-between">
                  <span className="capitalize">{status}</span>
                  <span>{count}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Service Status */}
        <ServiceStatusCard services={analytics.services} />
      </div>

      {/* Optimization Suggestions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <OptimizationSuggestions 
          suggestions={analytics.orders?.optimization_suggestions} 
        />
        <OptimizationSuggestions 
          suggestions={analytics.questions?.optimization_suggestions} 
        />
      </div>

      {/* Learning Insights */}
      {(analytics.orders?.learning_insights || analytics.questions?.learning_insights) && (
        <div className="mt-6 bg-white p-6 rounded-lg shadow border">
          <h3 className="text-lg font-semibold mb-4">Insights de Machine Learning</h3>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {analytics.orders?.learning_insights && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Vendas</h4>
                <p className="text-sm text-gray-600">
                  {JSON.stringify(analytics.orders.learning_insights, null, 2)}
                </p>
              </div>
            )}
            {analytics.questions?.learning_insights && (
              <div>
                <h4 className="font-medium text-gray-900 mb-2">Perguntas</h4>
                <p className="text-sm text-gray-600">
                  {JSON.stringify(analytics.questions.learning_insights, null, 2)}
                </p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsDashboard;