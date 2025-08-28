import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import GamificationDashboard from '../components/GamificationDashboard';
import AlertsManager from '../components/AlertsManager';
import CompetitionAnalysis from '../components/CompetitionAnalysis';
import MarkupSafetyValidator from '../components/MarkupSafetyValidator';
import CampaignDeactivationDialog from '../components/CampaignDeactivationDialog';
import AnimatedCard from '../components/AnimatedCard';

interface DashboardStats {
  totalCampaigns: number;
  activeAlerts: number;
  achievements: number;
  competitorPosition: number;
}

interface Campaign {
  name: string;
  budget: number;
  acos: number;
  clicks: number;
  conversions: number;
}

const ComprehensiveDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [userId] = useState<string>('user_123');
  const [showDeactivationDialog, setShowDeactivationDialog] = useState<boolean>(false);
  const [selectedCampaign, setSelectedCampaign] = useState<Campaign | null>(null);
  const [dashboardStats, setDashboardStats] = useState<DashboardStats>({
    totalCampaigns: 0,
    activeAlerts: 0,
    achievements: 0,
    competitorPosition: 0,
  });

  const tabs = [
    { id: 'overview', label: '📊 Visão Geral', icon: '📊' },
    { id: 'competition', label: '🏆 Concorrência', icon: '🏆' },
    { id: 'gamification', label: '🎮 Gamificação', icon: '🎮' },
    { id: 'alerts', label: '🔔 Alertas', icon: '🔔' },
    { id: 'safety', label: '🛡️ Segurança', icon: '🛡️' },
  ];

  useEffect(() => {
    loadDashboardStats();
  }, []);

  const loadDashboardStats = async () => {
    try {
      setDashboardStats({
        totalCampaigns: 24,
        activeAlerts: 3,
        achievements: 15,
        competitorPosition: 2,
      });
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleCampaignDeactivation = (campaign: Campaign) => {
    setSelectedCampaign(campaign);
    setShowDeactivationDialog(true);
  };

  const confirmDeactivation = (deactivationData: any) => {
    console.log('Campanha desativada:', selectedCampaign, deactivationData);
    setShowDeactivationDialog(false);
    setSelectedCampaign(null);
    // Aqui você faria a chamada para a API para desativar a campanha
  };

  const renderOverviewTab = () => (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold">{dashboardStats.totalCampaigns}</div>
              <div className="text-sm opacity-90">Campanhas Ativas</div>
            </div>
            <div className="text-4xl opacity-80">📊</div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-gradient-to-r from-red-500 to-red-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold">{dashboardStats.activeAlerts}</div>
              <div className="text-sm opacity-90">Alertas Ativos</div>
            </div>
            <div className="text-4xl opacity-80">🔔</div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold">{dashboardStats.achievements}</div>
              <div className="text-sm opacity-90">Conquistas</div>
            </div>
            <div className="text-4xl opacity-80">🏆</div>
          </div>
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold">#{dashboardStats.competitorPosition}</div>
              <div className="text-sm opacity-90">Posição vs Concorrência</div>
            </div>
            <div className="text-4xl opacity-80">🥈</div>
          </div>
        </motion.div>
      </div>
      {/* Quick Actions */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">⚡ Ações Rápidas</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab('competition')}
            className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors text-left"
          >
            <div className="text-2xl mb-2">🏆</div>
            <div className="font-medium">Análise de Concorrência</div>
            <div className="text-sm text-gray-600">Ver posições e estratégias</div>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab('alerts')}
            className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors text-left"
          >
            <div className="text-2xl mb-2">🔔</div>
            <div className="font-medium">Configurar Alertas</div>
            <div className="text-sm text-gray-600">Personalizar notificações</div>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => setActiveTab('safety')}
            className="p-4 border border-gray-300 rounded-lg hover:border-indigo-500 transition-colors text-left"
          >
            <div className="text-2xl mb-2">🛡️</div>
            <div className="font-medium">Validar Margem</div>
            <div className="text-sm text-gray-600">Verificar segurança do markup</div>
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            onClick={() => handleCampaignDeactivation({
              name: 'Campanha Exemplo',
              budget: 1000,
              acos: 15.5,
              clicks: 1250,
              conversions: 45,
            })}
            className="p-4 border border-gray-300 rounded-lg hover:border-red-500 transition-colors text-left"
          >
            <div className="text-2xl mb-2">🛑</div>
            <div className="font-medium">Desativar Campanha</div>
            <div className="text-sm text-gray-600">Processo seguro de desativação</div>
          </motion.button>
        </div>
      </motion.div>
      {/* Recent Activity */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">📈 Atividade Recente</h3>
        <div className="space-y-3">
          {[
            { icon: '🏆', text: 'Nova conquista desbloqueada: "Mestre do Markup"', time: '2 min atrás' },
            { icon: '🚨', text: 'Alerta: ACOS da campanha "Smartphones" acima de 15%', time: '15 min atrás' },
            { icon: '📊', text: 'Posição melhorou para #2 na palavra-chave "notebook"', time: '1 hora atrás' },
            { icon: '✅', text: 'Margem de segurança validada para produto SKU-12345', time: '2 horas atrás' },
            { icon: '🎮', text: 'Subiu para nível 8 no sistema de gamificação', time: '1 dia atrás' },
          ].map((activity, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 + index * 0.1 }}
              className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
            >
              <div className="text-xl">{activity.icon}</div>
              <div className="flex-1">
                <div className="text-sm font-medium">{activity.text}</div>
                <div className="text-xs text-gray-500">{activity.time}</div>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.div>
      {/* System Health */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
        className="bg-white rounded-lg shadow-lg p-6"
      >
        <h3 className="text-lg font-semibold mb-4">🔧 Status do Sistema</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Serviço de IA: Online</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Alertas: Funcionando</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Gamificação: Ativo</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Concorrência: Monitorando</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Validação: Operacional</span>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-3 h-3 bg-green-500 rounded-full"></div>
            <span className="text-sm">Grafana: Conectado</span>
          </div>
        </div>
      </motion.div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                🚀 ML Project - Dashboard Completo
              </h1>
              <p className="text-gray-600 mt-1">
                Sistema integrado de gestão de campanhas com IA, gamificação e alertas
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Última atualização: {new Date().toLocaleTimeString('pt-BR')}
              </div>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => window.open('http://localhost:3001', '_blank')}
                className="bg-indigo-500 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-600"
              >
                📊 Abrir Grafana
              </motion.button>
            </div>
          </div>
        </div>
      </div>
      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <motion.button
                key={tab.id}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </motion.button>
            ))}
          </div>
        </div>
      </div>
      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'competition' && <CompetitionAnalysis userId={userId} />}
          {activeTab === 'gamification' && <GamificationDashboard userId={userId} />}
          {activeTab === 'alerts' && <AlertsManager userId={userId} />}
          {activeTab === 'safety' && (
            <MarkupSafetyValidator
              currentMarkup={15}
              productCost={100}
              productPrice={150}
              onValidation={(result: any) => console.log('Validation result:', result)}
            />
          )}
        </motion.div>
      </div>
      {/* Campaign Deactivation Dialog */}
      <CampaignDeactivationDialog
        isOpen={showDeactivationDialog}
        campaign={selectedCampaign}
        onConfirm={confirmDeactivation}
        onCancel={() => {
          setShowDeactivationDialog(false);
          setSelectedCampaign(null);
        }}
      />
    </div>
  );
};

export default ComprehensiveDashboard;
