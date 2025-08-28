import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

interface Alert {
  // Defina os campos conforme a resposta da API
  [key: string]: any;
}

interface AlertRule {
  name: string;
  description: string;
  metric: string;
  condition: string;
  threshold: number;
  severity: string;
  notification_channels: string[];
  notification_config: Record<string, any>;
  cooldown_minutes: number;
}

interface AlertsManagerProps {
  userId: string;
}

const metrics = [
  { value: 'acos', label: 'ACOS (%)' },
  { value: 'markup_margin', label: 'Margem de Markup (%)' },
  { value: 'campaign_spend', label: 'Gasto da Campanha (R$)' },
  { value: 'roi', label: 'ROI (%)' },
  { value: 'cpc', label: 'CPC (R$)' },
  { value: 'conversion_rate', label: 'Taxa de Conversão (%)' }
];

const severityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800 border-green-300',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
  high: 'bg-orange-100 text-orange-800 border-orange-300',
  critical: 'bg-red-100 text-red-800 border-red-300'
};

const severityIcons: Record<string, string> = {
  low: '📘',
  medium: '⚠️',
  high: '🚨',
  critical: '🔥'
};

const AlertsManager: React.FC<AlertsManagerProps> = ({ userId }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertRules, setAlertRules] = useState<AlertRule[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newRule, setNewRule] = useState<AlertRule>({
    name: '',
    description: '',
    metric: 'acos',
    condition: '>',
    threshold: 15,
    severity: 'medium',
    notification_channels: ['card'],
    notification_config: {},
    cooldown_minutes: 60
  });

  useEffect(() => {
    if (userId) {
      loadAlertsData();
    }
  }, [userId]);

  const loadAlertsData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const headers = { Authorization: `Bearer ${token}` };
      const [alertsRes, rulesRes] = await Promise.all([
        axios.get(`http://localhost:8019/alert-events/${userId}?resolved=false`, { headers }),
        axios.get(`http://localhost:8019/alert-rules/${userId}`, { headers })
      ]);
      setAlerts(alertsRes.data || []);
      setAlertRules(rulesRes.data || []);
    } catch (error) {
      // Trate o erro conforme necessário
    } finally {
      setLoading(false);
    }
  };

  // ...existing code...

  return (
    <div>
      {/* Renderize o gerenciador de alertas conforme necessário */}
      {/* ...existing code... */}
    </div>
  );
};

export default AlertsManager;
