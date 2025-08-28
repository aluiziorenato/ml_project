import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import KPICard from '../components/KPICard';
import DataTable from '../components/DataTable';

interface Campaign {
  id: string;
  name: string;
  type: string;
  status: string;
  budget: number;
  spent: number;
  clicks: number;
  conversions: number;
  startDate: string;
  endDate: string;
}

interface Metrics {
  totalCampaigns: number;
  activeCampaigns: number;
  pausedCampaigns: number;
  completedCampaigns: number;
  totalBudget: number;
  totalSpent: number;
  totalClicks: number;
  totalConversions: number;
  avgCTR: number;
  avgCPC: number;
  avgCPA: number;
  roas: number;
}

const Campaigns: React.FC = () => {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [metrics, setMetrics] = useState<Metrics>({} as Metrics);

  useEffect(() => {
    setCampaigns([
      {
        id: 'CAM001',
        name: 'Black Friday 2024',
        type: 'Desconto',
        status: 'Ativa',
        budget: 10000,
        spent: 7850.5,
        clicks: 15420,
        conversions: 234,
        startDate: '2024-01-01',
        endDate: '2024-01-31',
      },
      {
        id: 'CAM002',
        name: 'Lançamento Produto X',
        type: 'Awareness',
        status: 'Pausada',
        budget: 5000,
        spent: 3200.75,
        clicks: 8930,
        conversions: 127,
        startDate: '2024-01-10',
        endDate: '2024-02-10',
      },
      {
        id: 'CAM003',
        name: 'Retargeting Q1',
        type: 'Retargeting',
        status: 'Ativa',
        budget: 8000,
        spent: 4567.25,
        clicks: 12340,
        conversions: 189,
        startDate: '2024-01-05',
        endDate: '2024-03-05',
      },
      {
        id: 'CAM004',
        name: 'Volta às Aulas',
        type: 'Sazonal',
        status: 'Finalizada',
        budget: 6000,
        spent: 5980.0,
        clicks: 9876,
        conversions: 145,
        startDate: '2023-12-01',
        endDate: '2023-12-31',
      },
      {
        id: 'CAM005',
        name: 'Teste A/B Headlines',
        type: 'Teste',
        status: 'Ativa',
        budget: 2000,
        spent: 567.8,
        clicks: 3450,
        conversions: 67,
        startDate: '2024-01-12',
        endDate: '2024-01-26',
      },
    ]);

    setMetrics({
      totalCampaigns: 47,
      activeCampaigns: 12,
      pausedCampaigns: 8,
      completedCampaigns: 27,
      totalBudget: 125000,
      totalSpent: 89456.3,
      totalClicks: 234567,
      totalConversions: 3456,
      avgCTR: 2.3,
      avgCPC: 0.38,
      avgCPA: 25.89,
      roas: 4.2,
    });
  }, []);

  const campaignColumns = [
    { field: 'id', label: 'ID', sortable: true },
    { field: 'name', label: 'Nome da Campanha', sortable: true },
    {
      field: 'type',
      label: 'Tipo',
      sortable: true,
      render: (value: string) => {
        const typeColors: Record<string, string> = {
          Desconto: 'bg-green-100 text-green-800',
          Awareness: 'bg-blue-100 text-blue-800',
          Retargeting: 'bg-purple-100 text-purple-800',
          Sazonal: 'bg-orange-100 text-orange-800',
          Teste: 'bg-gray-100 text-gray-800',
        };
        return (
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${typeColors[value]}`}>
            {value}
          </span>
        );
      },
    },
    {
      field: 'status',
      label: 'Status',
      sortable: true,
      render: (value: string) => {
        const statusColors: Record<string, string> = {
          Ativa: 'bg-green-100 text-green-800',
          Pausada: 'bg-yellow-100 text-yellow-800',
          Finalizada: 'bg-gray-100 text-gray-800',
        };
        return (
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[value]}`}>
            {value}
          </span>
        );
      },
    },
    {
      field: 'budget',
      label: 'Orçamento',
      sortable: true,
      render: (value: number) => `R$ ${value.toLocaleString()}`,
    },
    {
      field: 'spent',
      label: 'Gasto',
      sortable: true,
      render: (value: number) => `R$ ${value.toFixed(2)}`,
    },
    { field: 'clicks', label: 'Cliques', sortable: true },
    { field: 'conversions', label: 'Conversões', sortable: true },
    {
      field: 'ctr',
      label: 'CTR',
      render: (_: any, item: Campaign) => `${((item.clicks / (item.clicks * 10)) * 100).toFixed(2)}%`,
    },
  ];

  const actions = [
    {
      label: 'Editar',
      onClick: (campaign: Campaign) => console.log('Editar campanha:', campaign),
      className: 'bg-blue-100 text-blue-700 hover:bg-blue-200',
    },
    {
      label: 'Relatório',
      onClick: (campaign: Campaign) => console.log('Ver relatório:', campaign),
      className: 'bg-green-100 text-green-700 hover:bg-green-200',
    },
    {
      label: 'Pausar',
      onClick: (campaign: Campaign) => console.log('Pausar campanha:', campaign),
      className: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200',
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Campanhas</h1>
        <p className="text-gray-600">Gerenciamento e análise de campanhas publicitárias</p>
      </motion.div>

      {/* Campaign Status KPIs */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <KPICard
          title="Total de Campanhas"
          value={metrics.totalCampaigns}
          change="+8"
          changeType="positive"
          icon="📢"
          color="blue"
        />
        <KPICard
          title="Campanhas Ativas"
          value={metrics.activeCampaigns}
          change="+3"
          changeType="positive"
          icon="🟢"
          color="green"
        />
        <KPICard
          title="Pausadas"
          value={metrics.pausedCampaigns}
          change="-2"
          changeType="positive"
          icon="⏸️"
          color="orange"
        />
        <KPICard
          title="Finalizadas"
          value={metrics.completedCampaigns}
          change="+5"
          changeType="positive"
          icon="✅"
          color="purple"
        />
      </motion.div>

      {/* Budget & Performance KPIs */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <KPICard
          title="Orçamento Total"
          value={`R$ ${metrics.totalBudget?.toLocaleString()}`}
          change="+25k"
          changeType="positive"
          icon="💰"
          color="green"
        />
        <KPICard
          title="Total Investido"
          value={`R$ ${metrics.totalSpent?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
          change="+12.5%"
          changeType="positive"
          icon="💳"
          color="blue"
        />
        <KPICard
          title="Total de Cliques"
          value={metrics.totalClicks?.toLocaleString()}
          change="+18.7%"
          changeType="positive"
          icon="👆"
          color="purple"
        />
        <KPICard
          title="Conversões"
          value={metrics.totalConversions?.toLocaleString()}
          change="+23.4%"
          changeType="positive"
          icon="🎯"
          color="orange"
        />
      </motion.div>

      {/* Performance Metrics */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5, duration: 0.6 }}
      >
        <KPICard
          title="CTR Médio"
          value={`${metrics.avgCTR}%`}
          change="+0.3%"
          changeType="positive"
          icon="📊"
          color="blue"
        />
        <KPICard
          title="CPC Médio"
          value={`R$ ${metrics.avgCPC?.toFixed(2)}`}
          change="-R$ 0.05"
          changeType="positive"
          icon="💲"
          color="green"
        />
        <KPICard
          title="CPA Médio"
          value={`R$ ${metrics.avgCPA?.toFixed(2)}`}
          change="-R$ 2.10"
          changeType="positive"
          icon="🏷️"
          color="orange"
        />
        <KPICard
          title="ROAS"
          value={`${metrics.roas?.toFixed(1)}x`}
          change="+0.5x"
          changeType="positive"
          icon="📈"
          color="purple"
        />
      </motion.div>

      {/* Quick Actions */}
      <motion.div
        className="mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        <div className="flex flex-wrap gap-4">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors duration-300 shadow-lg">
            + Nova Campanha
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            📊 Relatório Geral
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            🎯 Otimização IA
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            📤 Exportar Dados
          </button>
        </div>
      </motion.div>

      {/* Campaign Performance Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7, duration: 0.6 }}
      >
        <div className="bg-gradient-to-r from-green-500 to-green-600 text-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-semibold mb-2">🏆 Melhor Performance</h3>
          <div className="text-2xl font-bold">Black Friday 2024</div>
          <div className="text-green-100">234 conversões • R$ 18.67 CPA</div>
        </div>
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-semibold mb-2">💰 Maior ROI</h3>
          <div className="text-2xl font-bold">Retargeting Q1</div>
          <div className="text-blue-100">5.8x ROAS • R$ 21.45 CPA</div>
        </div>
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 text-white p-6 rounded-xl shadow-lg">
          <h3 className="text-lg font-semibold mb-2">🎯 Maior CTR</h3>
          <div className="text-2xl font-bold">Teste A/B Headlines</div>
          <div className="text-purple-100">4.2% CTR • R$ 0.28 CPC</div>
        </div>
      </motion.div>

      {/* Campaigns Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <DataTable
          title="Lista de Campanhas"
          columns={campaignColumns}
          data={campaigns}
          actions={actions}
        />
      </motion.div>
    </div>
  );
};

export default Campaigns;
