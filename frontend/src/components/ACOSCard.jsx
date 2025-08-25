/**
 * ACOSCard - Component for displaying ACOS metrics and automation controls
 */
import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Minus, AlertTriangle, Settings, Play, Pause } from 'lucide-react';

const ACOSCard = ({ campaignId, className = "" }) => {
  const [acosData, setAcosData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [automationRules, setAutomationRules] = useState([]);

  useEffect(() => {
    if (campaignId) {
      fetchACOSData();
      fetchAutomationRules();
    }
  }, [campaignId]);

  const fetchACOSData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/acos/campaigns/${campaignId}/metrics`);
      if (response.ok) {
        const data = await response.json();
        setAcosData(data);
      } else {
        throw new Error('Failed to fetch ACOS data');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchAutomationRules = async () => {
    try {
      const response = await fetch('/api/acos/rules');
      if (response.ok) {
        const rules = await response.json();
        setAutomationRules(rules.filter(rule => 
          rule.campaign_ids?.includes(campaignId) || !rule.campaign_ids
        ));
      }
    } catch (err) {
      console.error('Failed to fetch automation rules:', err);
    }
  };

  const triggerEvaluation = async () => {
    try {
      const response = await fetch('/api/acos/automation/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        // Show success message
        setTimeout(() => fetchACOSData(), 2000); // Refresh data after 2 seconds
      }
    } catch (err) {
      console.error('Failed to trigger evaluation:', err);
    }
  };

  const getACOSStatus = (acos) => {
    if (acos <= 15) return { status: 'excellent', color: 'text-green-600', bg: 'bg-green-100' };
    if (acos <= 25) return { status: 'good', color: 'text-blue-600', bg: 'bg-blue-100' };
    if (acos <= 35) return { status: 'warning', color: 'text-yellow-600', bg: 'bg-yellow-100' };
    return { status: 'critical', color: 'text-red-600', bg: 'bg-red-100' };
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing': return <TrendingUp className="w-4 h-4 text-red-500" />;
      case 'decreasing': return <TrendingDown className="w-4 h-4 text-green-500" />;
      default: return <Minus className="w-4 h-4 text-gray-500" />;
    }
  };

  if (loading) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
          <div className="h-8 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <div className="flex items-center text-red-600">
          <AlertTriangle className="w-5 h-5 mr-2" />
          <span>Error loading ACOS data: {error}</span>
        </div>
      </div>
    );
  }

  if (!acosData) {
    return (
      <div className={`bg-white rounded-lg shadow-sm border p-6 ${className}`}>
        <div className="text-gray-500 text-center">
          No ACOS data available for this campaign
        </div>
      </div>
    );
  }

  const acosStatus = getACOSStatus(acosData.current_acos);

  return (
    <div className={`bg-white rounded-lg shadow-sm border ${className}`}>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            🎯 ACOS Performance
          </h3>
          <button
            onClick={triggerEvaluation}
            className="flex items-center px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
          >
            <Play className="w-4 h-4 mr-1" />
            Evaluate Rules
          </button>
        </div>
      </div>

      {/* Main ACOS Metric */}
      <div className="px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <div className="flex items-center space-x-2">
              <span className={`text-3xl font-bold ${acosStatus.color}`}>
                {acosData.current_acos.toFixed(1)}%
              </span>
              {getTrendIcon(acosData.acos_trend)}
            </div>
            <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${acosStatus.bg} ${acosStatus.color}`}>
              {acosStatus.status.toUpperCase()}
            </div>
          </div>
          <div className="text-right text-sm text-gray-600">
            <div>Period: {acosData.period_hours}h</div>
            <div>Spend: R$ {acosData.total_spend.toLocaleString()}</div>
            <div>Revenue: R$ {acosData.total_revenue.toLocaleString()}</div>
          </div>
        </div>

        {/* Performance Indicators */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-600">Efficiency</div>
            <div className="text-lg font-semibold">
              {acosData.current_acos <= 20 ? 'High' : 
               acosData.current_acos <= 30 ? 'Medium' : 'Low'}
            </div>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-sm text-gray-600">Trend</div>
            <div className="text-lg font-semibold capitalize">
              {acosData.acos_trend}
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {acosData.recommendations && acosData.recommendations.length > 0 && (
          <div className="mb-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">💡 Recommendations</h4>
            <ul className="text-sm text-gray-600 space-y-1">
              {acosData.recommendations.slice(0, 3).map((rec, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-blue-500 mr-2">•</span>
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Automation Rules Status */}
        {automationRules.length > 0 && (
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-medium text-gray-900">🤖 Automation Rules</h4>
              <Settings className="w-4 h-4 text-gray-400" />
            </div>
            <div className="space-y-2">
              {automationRules.slice(0, 2).map((rule, index) => (
                <div key={index} className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">{rule.name}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-gray-500">{rule.threshold_value}%</span>
                    {rule.is_active ? (
                      <span className="text-green-600">Active</span>
                    ) : (
                      <span className="text-gray-400">Inactive</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ACOSCard;