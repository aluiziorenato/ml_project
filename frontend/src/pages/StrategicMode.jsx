import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import StrategySelector from '../components/StrategySelector';
import SpecialDatesCalendar from '../components/SpecialDatesCalendar';
import KPICard from '../components/KPICard';
import DataTable from '../components/DataTable';
import { 
  ChartBarIcon, 
  CogIcon, 
  ExclamationTriangleIcon, 
  CheckCircleIcon,
  ClockIcon,
  BoltIcon
} from '@heroicons/react/24/solid';

const StrategicMode = () => {
  const [activeTab, setActiveTab] = useState('configuration');
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [selectedSpecialDate, setSelectedSpecialDate] = useState(null);
  const [isApplyingStrategy, setIsApplyingStrategy] = useState(false);
  const [dashboardData, setDashboardData] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [recentActions, setRecentActions] = useState([]);

  // Mock data - in real implementation, this would come from API
  const mockDashboardData = {
    currentStrategy: {
      id: 2,
      name: "Escalar Vendas",
      applied_at: "2024-01-15T10:30:00Z"
    },
    kpis: {
      totalSpend: 15420.50,
      totalSales: 89334.20,
      averageAcos: 17.2,
      roi: 4.8,
      activeCampaigns: 23,
      pausedCampaigns: 4
    },
    recentAlerts: [
      {
        id: 1,
        type: "acos_high",
        severity: "warning",
        title: "ACOS acima do target",
        message: "Campanha 'Produto XYZ' com ACOS de 28%",
        created_at: "2024-01-15T14:30:00Z",
        is_resolved: false
      },
      {
        id: 2,
        type: "budget_low",
        severity: "info", 
        title: "Orçamento baixo",
        message: "Restam apenas 15% do orçamento diário",
        created_at: "2024-01-15T13:15:00Z",
        is_resolved: false
      }
    ],
    recentActions: [
      {
        id: 1,
        action_type: "bid_adjustment",
        service: "acos_service",
        campaign_id: "CAM123",
        status: "executed",
        created_at: "2024-01-15T14:45:00Z",
        description: "Redução de lance em 15% devido a ACOS alto"
      },
      {
        id: 2,
        action_type: "campaign_pause",
        service: "campaign_automation",
        campaign_id: "CAM456",
        status: "executed", 
        created_at: "2024-01-15T14:30:00Z",
        description: "Pausa automática de campanha com ACOS > 30%"
      }
    ]
  };

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setDashboardData(mockDashboardData);
      setAlerts(mockDashboardData.recentAlerts);
      setRecentActions(mockDashboardData.recentActions);
    }, 1000);
  }, []);

  const handleStrategySelect = async (strategy) => {
    setSelectedStrategy(strategy);
  };

  const handleApplyStrategy = async () => {
    if (!selectedStrategy) return;
    
    setIsApplyingStrategy(true);
    
    try {
      // Simulate API call to apply strategy
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Update dashboard data
      setDashboardData(prev => ({
        ...prev,
        currentStrategy: {
          ...selectedStrategy,
          applied_at: new Date().toISOString()
        }
      }));
      
      alert(`Estratégia "${selectedStrategy.name}" aplicada com sucesso!`);
    } catch (error) {
      alert('Erro ao aplicar estratégia: ' + error.message);
    } finally {
      setIsApplyingStrategy(false);
    }
  };

  const handleSpecialDateSelect = (specialDate) => {
    setSelectedSpecialDate(specialDate);
  };

  const alertColumns = [
    { field: 'title', label: 'Título', sortable: true },
    { field: 'severity', label: 'Severidade', sortable: true, render: (value) => (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        value === 'critical' ? 'bg-red-100 text-red-800' :
        value === 'warning' ? 'bg-yellow-100 text-yellow-800' :
        'bg-blue-100 text-blue-800'
      }`}>
        {value === 'critical' ? 'Crítico' : value === 'warning' ? 'Aviso' : 'Info'}
      </span>
    )},
    { field: 'created_at', label: 'Data', sortable: true, render: (value) => 
      new Date(value).toLocaleDateString('pt-BR')
    },
    { field: 'is_resolved', label: 'Status', sortable: true, render: (value) => (
      <span className={`flex items-center ${value ? 'text-green-600' : 'text-red-600'}`}>
        {value ? <CheckCircleIcon className="h-4 w-4 mr-1" /> : <ExclamationTriangleIcon className="h-4 w-4 mr-1" />}
        {value ? 'Resolvido' : 'Pendente'}
      </span>
    )}
  ];

  const actionColumns = [
    { field: 'description', label: 'Ação', sortable: false },
    { field: 'service', label: 'Serviço', sortable: true },
    { field: 'status', label: 'Status', sortable: true, render: (value) => (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
        value === 'executed' ? 'bg-green-100 text-green-800' :
        value === 'failed' ? 'bg-red-100 text-red-800' :
        'bg-yellow-100 text-yellow-800'
      }`}>
        {value === 'executed' ? 'Executado' : value === 'failed' ? 'Falhou' : 'Pendente'}
      </span>
    )},
    { field: 'created_at', label: 'Data', sortable: true, render: (value) => 
      new Date(value).toLocaleTimeString('pt-BR')
    }
  ];

  const tabs = [
    { id: 'configuration', label: 'Configuração', icon: CogIcon },
    { id: 'monitoring', label: 'Monitoramento', icon: ChartBarIcon },
    { id: 'special-dates', label: 'Datas Especiais', icon: ClockIcon }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Modo Estratégico</h1>
        <p className="text-gray-600">Configure e monitore suas estratégias globais de campanhas</p>
      </motion.div>

      {/* Current Strategy Banner */}
      {dashboardData?.currentStrategy && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6 p-4 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <BoltIcon className="h-6 w-6 mr-3" />
              <div>
                <h3 className="font-semibold">Estratégia Ativa: {dashboardData.currentStrategy.name}</h3>
                <p className="text-blue-100 text-sm">
                  Aplicada em {new Date(dashboardData.currentStrategy.applied_at).toLocaleDateString('pt-BR')}
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <CheckCircleIcon className="h-5 w-5" />
              <span className="text-sm font-medium">Ativa</span>
            </div>
          </div>
        </motion.div>
      )}

      {/* Navigation Tabs */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Tab Content */}
      <motion.div
        key={activeTab}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        {activeTab === 'configuration' && (
          <div className="space-y-8">
            <StrategySelector
              onStrategySelect={handleStrategySelect}
              selectedStrategy={selectedStrategy}
              isLoading={isApplyingStrategy}
            />
            
            {selectedStrategy && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex justify-center"
              >
                <button
                  onClick={handleApplyStrategy}
                  disabled={isApplyingStrategy}
                  className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {isApplyingStrategy ? 'Aplicando Estratégia...' : 'Aplicar Estratégia'}
                </button>
              </motion.div>
            )}
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="space-y-8">
            {/* KPI Cards */}
            {dashboardData?.kpis && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <KPICard
                  title="Gasto Total"
                  value={`R$ ${dashboardData.kpis.totalSpend.toLocaleString('pt-BR')}`}
                  change="+12.5%"
                  changeType="neutral"
                  icon="💰"
                  color="blue"
                />
                <KPICard
                  title="Vendas Totais"
                  value={`R$ ${dashboardData.kpis.totalSales.toLocaleString('pt-BR')}`}
                  change="+23.1%"
                  changeType="positive"
                  icon="📊"
                  color="green"
                />
                <KPICard
                  title="ACOS Médio"
                  value={`${dashboardData.kpis.averageAcos}%`}
                  change="-2.3%"
                  changeType="positive"
                  icon="🎯"
                  color="purple"
                />
                <KPICard
                  title="ROI"
                  value={`${dashboardData.kpis.roi}x`}
                  change="+0.8x"
                  changeType="positive"
                  icon="📈"
                  color="yellow"
                />
                <KPICard
                  title="Campanhas Ativas"
                  value={dashboardData.kpis.activeCampaigns}
                  change="+3"
                  changeType="positive"
                  icon="🚀"
                  color="indigo"
                />
                <KPICard
                  title="Campanhas Pausadas"
                  value={dashboardData.kpis.pausedCampaigns}
                  change="+1"
                  changeType="neutral"
                  icon="⏸️"
                  color="gray"
                />
              </div>
            )}

            {/* Alerts Table */}
            <DataTable
              title="Alertas Recentes"
              columns={alertColumns}
              data={alerts}
              actions={[
                {
                  label: 'Resolver',
                  onClick: (item) => console.log('Resolver alerta:', item),
                  className: 'bg-green-100 text-green-700 hover:bg-green-200'
                }
              ]}
            />

            {/* Recent Actions Table */}
            <DataTable
              title="Ações Automáticas Recentes"
              columns={actionColumns}
              data={recentActions}
              actions={[
                {
                  label: 'Detalhes',
                  onClick: (item) => console.log('Ver detalhes:', item),
                  className: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
                }
              ]}
            />
          </div>
        )}

        {activeTab === 'special-dates' && (
          <SpecialDatesCalendar
            onDateSelect={handleSpecialDateSelect}
            selectedDate={selectedSpecialDate}
          />
        )}
      </motion.div>
    </div>
  );
};

export default StrategicMode;