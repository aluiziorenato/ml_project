import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';

const AlertsManager = ({ userId }) => {
    const [alerts, setAlerts] = useState([]);
    const [alertRules, setAlertRules] = useState([]);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [loading, setLoading] = useState(true);
    const [newRule, setNewRule] = useState({
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

    const metrics = [
        { value: 'acos', label: 'ACOS (%)' },
        { value: 'markup_margin', label: 'Margem de Markup (%)' },
        { value: 'campaign_spend', label: 'Gasto da Campanha (R$)' },
        { value: 'roi', label: 'ROI (%)' },
        { value: 'cpc', label: 'CPC (R$)' },
        { value: 'conversion_rate', label: 'Taxa de Conversão (%)' }
    ];

    const severityColors = {
        low: 'bg-green-100 text-green-800 border-green-300',
        medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
        high: 'bg-orange-100 text-orange-800 border-orange-300',
        critical: 'bg-red-100 text-red-800 border-red-300'
    };

    const severityIcons = {
        low: '📘',
        medium: '⚠️',
        high: '🚨',
        critical: '🔥'
    };

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

            setAlerts(alertsRes.data);
            setAlertRules(rulesRes.data);
        } catch (error) {
            console.error('Erro ao carregar dados de alertas:', error);
        } finally {
            setLoading(false);
        }
    };

    const createAlertRule = async () => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            const ruleData = {
                ...newRule,
                user_id: userId,
                notification_config: {
                    email: { recipient: `user_${userId}@company.com` },
                    card: { severity: newRule.severity }
                }
            };

            await axios.post('http://localhost:8019/alert-rules', ruleData, { headers });
            
            setShowCreateForm(false);
            setNewRule({
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
            
            loadAlertsData();
        } catch (error) {
            console.error('Erro ao criar regra de alerta:', error);
        }
    };

    const toggleAlertRule = async (ruleId, enabled) => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            await axios.put(`http://localhost:8019/alert-rules/${ruleId}/toggle?enabled=${enabled}`, {}, { headers });
            loadAlertsData();
        } catch (error) {
            console.error('Erro ao alterar regra de alerta:', error);
        }
    };

    const acknowledgeAlert = async (alertId) => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            await axios.put(`http://localhost:8019/alert-events/${alertId}/acknowledge`, {}, { headers });
            loadAlertsData();
        } catch (error) {
            console.error('Erro ao reconhecer alerta:', error);
        }
    };

    const resolveAlert = async (alertId) => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            await axios.put(`http://localhost:8019/alert-events/${alertId}/resolve`, {}, { headers });
            loadAlertsData();
        } catch (error) {
            console.error('Erro ao resolver alerta:', error);
        }
    };

    const createTemplateAlert = async (template) => {
        try {
            const token = localStorage.getItem('access_token');
            const headers = { Authorization: `Bearer ${token}` };

            await axios.post(`http://localhost:8019/alert-rules/templates/${template}?user_id=${userId}`, {}, { headers });
            loadAlertsData();
        } catch (error) {
            console.error('Erro ao criar alerta template:', error);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center p-8">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Quick Templates */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-white rounded-lg shadow-lg p-6"
            >
                <h3 className="text-lg font-semibold mb-4">🚀 Alertas Rápidos</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => createTemplateAlert('acos-high')}
                        className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors"
                    >
                        <div className="text-2xl mb-2">📈</div>
                        <div className="font-medium">ACOS Alto</div>
                        <div className="text-sm text-gray-600">Alerta quando ACOS > 15%</div>
                    </motion.button>
                    
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => createTemplateAlert('markup-margin-low')}
                        className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors"
                    >
                        <div className="text-2xl mb-2">💰</div>
                        <div className="font-medium">Margem Baixa</div>
                        <div className="text-sm text-gray-600">Alerta quando margem < 10%</div>
                    </motion.button>
                    
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => createTemplateAlert('campaign-spend-high')}
                        className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors"
                    >
                        <div className="text-2xl mb-2">💸</div>
                        <div className="font-medium">Gasto Alto</div>
                        <div className="text-sm text-gray-600">Alerta quando gasto > R$ 1000</div>
                    </motion.button>
                </div>
            </motion.div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Active Alerts */}
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">🔔 Alertas Ativos</h3>
                        <div className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-xs font-medium">
                            {alerts.filter(a => !a.resolved).length} ativo(s)
                        </div>
                    </div>
                    
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        <AnimatePresence>
                            {alerts.filter(a => !a.resolved).map((alert) => (
                                <motion.div
                                    key={alert.id}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className={`border rounded-lg p-4 ${severityColors[alert.severity]}`}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex items-start space-x-3">
                                            <div className="text-xl">{severityIcons[alert.severity]}</div>
                                            <div className="flex-1">
                                                <div className="font-medium">{alert.message}</div>
                                                <div className="text-sm opacity-75">
                                                    {alert.metric}: {alert.actual_value} (limite: {alert.threshold})
                                                </div>
                                                <div className="text-xs opacity-60 mt-1">
                                                    {new Date(alert.created_at).toLocaleString('pt-BR')}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex space-x-2">
                                            {!alert.acknowledged && (
                                                <motion.button
                                                    whileHover={{ scale: 1.1 }}
                                                    whileTap={{ scale: 0.9 }}
                                                    onClick={() => acknowledgeAlert(alert.id)}
                                                    className="text-xs bg-white bg-opacity-50 hover:bg-opacity-75 px-2 py-1 rounded"
                                                >
                                                    ✓ Reconhecer
                                                </motion.button>
                                            )}
                                            <motion.button
                                                whileHover={{ scale: 1.1 }}
                                                whileTap={{ scale: 0.9 }}
                                                onClick={() => resolveAlert(alert.id)}
                                                className="text-xs bg-white bg-opacity-50 hover:bg-opacity-75 px-2 py-1 rounded"
                                            >
                                                ✓ Resolver
                                            </motion.button>
                                        </div>
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                        
                        {alerts.filter(a => !a.resolved).length === 0 && (
                            <div className="text-center text-gray-500 py-8">
                                <div className="text-4xl mb-2">✅</div>
                                <div>Nenhum alerta ativo</div>
                            </div>
                        )}
                    </div>
                </motion.div>

                {/* Alert Rules */}
                <motion.div
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="bg-white rounded-lg shadow-lg p-6"
                >
                    <div className="flex justify-between items-center mb-4">
                        <h3 className="text-lg font-semibold">⚙️ Regras de Alerta</h3>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => setShowCreateForm(true)}
                            className="bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-indigo-600"
                        >
                            + Nova Regra
                        </motion.button>
                    </div>
                    
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                        {alertRules.map((rule) => (
                            <motion.div
                                key={rule.id}
                                whileHover={{ scale: 1.01 }}
                                className="border border-gray-200 rounded-lg p-4"
                            >
                                <div className="flex items-center justify-between">
                                    <div className="flex-1">
                                        <div className="font-medium">{rule.name}</div>
                                        <div className="text-sm text-gray-600">{rule.description}</div>
                                        <div className="text-xs text-gray-500 mt-1">
                                            {rule.metric} {rule.condition} {rule.threshold}
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <span className={`px-2 py-1 rounded-full text-xs ${severityColors[rule.severity]}`}>
                                            {rule.severity}
                                        </span>
                                        <button
                                            onClick={() => toggleAlertRule(rule.id, !rule.enabled)}
                                            className={`w-10 h-6 rounded-full flex items-center transition-colors ${
                                                rule.enabled ? 'bg-green-500' : 'bg-gray-300'
                                            }`}
                                        >
                                            <motion.div
                                                animate={{ x: rule.enabled ? 16 : 2 }}
                                                className="w-5 h-5 bg-white rounded-full"
                                            />
                                        </button>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                        
                        {alertRules.length === 0 && (
                            <div className="text-center text-gray-500 py-8">
                                Nenhuma regra de alerta configurada
                            </div>
                        )}
                    </div>
                </motion.div>
            </div>

            {/* Create Alert Rule Modal */}
            <AnimatePresence>
                {showCreateForm && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
                        onClick={() => setShowCreateForm(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.9, opacity: 0 }}
                            className="bg-white rounded-lg p-6 w-full max-w-md mx-4"
                            onClick={(e) => e.stopPropagation()}
                        >
                            <h3 className="text-lg font-semibold mb-4">Criar Nova Regra de Alerta</h3>
                            
                            <div className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium mb-1">Nome</label>
                                    <input
                                        type="text"
                                        value={newRule.name}
                                        onChange={(e) => setNewRule(prev => ({ ...prev, name: e.target.value }))}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        placeholder="Nome da regra"
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Descrição</label>
                                    <textarea
                                        value={newRule.description}
                                        onChange={(e) => setNewRule(prev => ({ ...prev, description: e.target.value }))}
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        rows="2"
                                        placeholder="Descrição da regra"
                                    />
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Métrica</label>
                                        <select
                                            value={newRule.metric}
                                            onChange={(e) => setNewRule(prev => ({ ...prev, metric: e.target.value }))}
                                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        >
                                            {metrics.map(metric => (
                                                <option key={metric.value} value={metric.value}>
                                                    {metric.label}
                                                </option>
                                            ))}
                                        </select>
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">Condição</label>
                                        <select
                                            value={newRule.condition}
                                            onChange={(e) => setNewRule(prev => ({ ...prev, condition: e.target.value }))}
                                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        >
                                            <option value=">">Maior que</option>
                                            <option value="<">Menor que</option>
                                            <option value=">=">Maior ou igual</option>
                                            <option value="<=">Menor ou igual</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium mb-1">Limite</label>
                                        <input
                                            type="number"
                                            value={newRule.threshold}
                                            onChange={(e) => setNewRule(prev => ({ ...prev, threshold: parseFloat(e.target.value) }))}
                                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-sm font-medium mb-1">Severidade</label>
                                        <select
                                            value={newRule.severity}
                                            onChange={(e) => setNewRule(prev => ({ ...prev, severity: e.target.value }))}
                                            className="w-full border border-gray-300 rounded-lg px-3 py-2"
                                        >
                                            <option value="low">Baixa</option>
                                            <option value="medium">Média</option>
                                            <option value="high">Alta</option>
                                            <option value="critical">Crítica</option>
                                        </select>
                                    </div>
                                </div>

                                <div>
                                    <label className="block text-sm font-medium mb-1">Canais de Notificação</label>
                                    <div className="space-y-2">
                                        {['card', 'email', 'webhook'].map(channel => (
                                            <label key={channel} className="flex items-center">
                                                <input
                                                    type="checkbox"
                                                    checked={newRule.notification_channels.includes(channel)}
                                                    onChange={(e) => {
                                                        if (e.target.checked) {
                                                            setNewRule(prev => ({
                                                                ...prev,
                                                                notification_channels: [...prev.notification_channels, channel]
                                                            }));
                                                        } else {
                                                            setNewRule(prev => ({
                                                                ...prev,
                                                                notification_channels: prev.notification_channels.filter(c => c !== channel)
                                                            }));
                                                        }
                                                    }}
                                                    className="mr-2"
                                                />
                                                <span className="capitalize">{channel}</span>
                                            </label>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            <div className="flex space-x-3 mt-6">
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={createAlertRule}
                                    className="flex-1 bg-indigo-500 text-white py-2 rounded-lg font-medium hover:bg-indigo-600"
                                >
                                    Criar Regra
                                </motion.button>
                                <motion.button
                                    whileHover={{ scale: 1.02 }}
                                    whileTap={{ scale: 0.98 }}
                                    onClick={() => setShowCreateForm(false)}
                                    className="flex-1 bg-gray-300 text-gray-700 py-2 rounded-lg font-medium hover:bg-gray-400"
                                >
                                    Cancelar
                                </motion.button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

export default AlertsManager;