import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import LineChartCard from '../components/Charts/LineChartCard'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'

export default function Dashboard() {
  const [data, setData] = useState([])
  const [systemMetrics, setSystemMetrics] = useState({})
  const [recentActivity, setRecentActivity] = useState([])

  useEffect(() => {
    // Simulate chart data
    const d = Array.from({length: 12}).map((_, i) => ({
      label: `M${i + 1}`, 
      value: Math.round(Math.random() * 200)
    }))
    setData(d)

    // Simulate system metrics
    setSystemMetrics({
      activeConnections: 45,
      requestsLastHour: 1247,
      expiringTokens: 3,
      systemLoad: 67.8,
      memoryUsage: 82.4,
      diskUsage: 34.2,
      errorRate: 0.02,
      uptime: 99.8
    })

    // Simulate recent activity
    setRecentActivity([
      { id: 1, type: 'Login', user: 'user@example.com', timestamp: '2024-01-15 14:32', status: 'Success' },
      { id: 2, type: 'API Call', user: 'system', timestamp: '2024-01-15 14:31', status: 'Success' },
      { id: 3, type: 'Export', user: 'admin@example.com', timestamp: '2024-01-15 14:29', status: 'Success' },
      { id: 4, type: 'Login', user: 'test@example.com', timestamp: '2024-01-15 14:25', status: 'Failed' },
      { id: 5, type: 'Backup', user: 'system', timestamp: '2024-01-15 14:20', status: 'Success' }
    ])
  }, [])

  const activityColumns = [
    { field: 'type', label: 'Tipo', sortable: true },
    { field: 'user', label: 'Usuário', sortable: true },
    { field: 'timestamp', label: 'Data/Hora', sortable: true },
    { 
      field: 'status', 
      label: 'Status', 
      sortable: true,
      render: (value) => (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
          value === 'Success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          {value}
        </span>
      )
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Visão geral do sistema e métricas em tempo real</p>
      </motion.div>

      {/* KPI Cards Section */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <KPICard
          title="Conexões Ativas"
          value={systemMetrics.activeConnections}
          change="+12.5%"
          changeType="positive"
          icon="🔗"
          color="blue"
        />
        <KPICard
          title="Requests/Hora"
          value={systemMetrics.requestsLastHour?.toLocaleString()}
          change="+8.2%"
          changeType="positive"
          icon="📊"
          color="green"
        />
        <KPICard
          title="Tokens Expirando"
          value={systemMetrics.expiringTokens}
          change="-2"
          changeType="positive"
          icon="🔑"
          color="orange"
        />
        <KPICard
          title="Uptime"
          value={`${systemMetrics.uptime}%`}
          change="+0.1%"
          changeType="positive"
          icon="⚡"
          color="purple"
        />
      </motion.div>

      {/* System Performance KPIs */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <KPICard
          title="Carga do Sistema"
          value={`${systemMetrics.systemLoad}%`}
          change="+2.3%"
          changeType="negative"
          icon="💻"
          color="blue"
        />
        <KPICard
          title="Uso de Memória"
          value={`${systemMetrics.memoryUsage}%`}
          change="-1.5%"
          changeType="positive"
          icon="🧠"
          color="green"
        />
        <KPICard
          title="Uso de Disco"
          value={`${systemMetrics.diskUsage}%`}
          change="+0.8%"
          changeType="negative"
          icon="💾"
          color="orange"
        />
        <KPICard
          title="Taxa de Erro"
          value={`${(systemMetrics.errorRate * 100).toFixed(2)}%`}
          change="-0.01%"
          changeType="positive"
          icon="🚨"
          color="red"
        />
      </motion.div>

      {/* Charts Section */}
      <motion.div 
        className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        <LineChartCard title="Requests por mês" data={data} />
        <LineChartCard 
          title="Erros por mês" 
          data={data.map(x => ({ 
            label: x.label, 
            value: Math.round(x.value * Math.random() * 0.1) 
          }))} 
        />
      </motion.div>

      {/* Recent Activity Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <DataTable
          title="Atividade Recente"
          columns={activityColumns}
          data={recentActivity}
          actions={[
            {
              label: 'Detalhes',
              onClick: (item) => console.log('Ver detalhes:', item),
              className: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
            }
          ]}
        />
      </motion.div>
    </div>
  )
}
