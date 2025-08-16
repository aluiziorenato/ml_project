import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import KPICard from '../components/KPICard'
import DataTable from '../components/DataTable'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [metrics, setMetrics] = useState({})

  useEffect(() => {
    // Simulate orders data
    setOrders([
      { 
        id: 'PED001', 
        customer: 'João Silva', 
        email: 'joao@email.com',
        total: 899.99, 
        status: 'Processando', 
        date: '2024-01-15',
        items: 1,
        payment: 'Cartão'
      },
      { 
        id: 'PED002', 
        customer: 'Maria Santos', 
        email: 'maria@email.com',
        total: 1299.99, 
        status: 'Enviado', 
        date: '2024-01-14',
        items: 2,
        payment: 'PIX'
      },
      { 
        id: 'PED003', 
        customer: 'Carlos Oliveira', 
        email: 'carlos@email.com',
        total: 299.99, 
        status: 'Entregue', 
        date: '2024-01-13',
        items: 1,
        payment: 'Boleto'
      },
      { 
        id: 'PED004', 
        customer: 'Ana Costa', 
        email: 'ana@email.com',
        total: 599.99, 
        status: 'Cancelado', 
        date: '2024-01-12',
        items: 3,
        payment: 'Cartão'
      },
      { 
        id: 'PED005', 
        customer: 'Pedro Lima', 
        email: 'pedro@email.com',
        total: 1899.99, 
        status: 'Processando', 
        date: '2024-01-15',
        items: 4,
        payment: 'PIX'
      }
    ])

    // Simulate metrics
    setMetrics({
      totalOrders: 1247,
      pendingOrders: 89,
      processingOrders: 156,
      shippedOrders: 203,
      deliveredOrders: 756,
      cancelledOrders: 43,
      totalRevenue: 487239.50,
      avgOrderValue: 390.85,
      todayOrders: 23,
      conversionRate: 3.2
    })
  }, [])

  const orderColumns = [
    { field: 'id', label: 'Pedido', sortable: true },
    { field: 'customer', label: 'Cliente', sortable: true },
    { field: 'email', label: 'Email', sortable: true },
    { 
      field: 'total', 
      label: 'Total', 
      sortable: true,
      render: (value) => `R$ ${value.toFixed(2)}`
    },
    { 
      field: 'status', 
      label: 'Status', 
      sortable: true,
      render: (value) => {
        const statusColors = {
          'Processando': 'bg-yellow-100 text-yellow-800',
          'Enviado': 'bg-blue-100 text-blue-800',
          'Entregue': 'bg-green-100 text-green-800',
          'Cancelado': 'bg-red-100 text-red-800'
        }
        return (
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[value]}`}>
            {value}
          </span>
        )
      }
    },
    { field: 'date', label: 'Data', sortable: true },
    { field: 'items', label: 'Itens', sortable: true },
    { field: 'payment', label: 'Pagamento', sortable: true }
  ]

  const actions = [
    {
      label: 'Ver Detalhes',
      onClick: (order) => console.log('Ver pedido:', order),
      className: 'bg-blue-100 text-blue-700 hover:bg-blue-200'
    },
    {
      label: 'Rastrear',
      onClick: (order) => console.log('Rastrear pedido:', order),
      className: 'bg-green-100 text-green-700 hover:bg-green-200'
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
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Pedidos</h1>
        <p className="text-gray-600">Gerenciamento e acompanhamento de pedidos</p>
      </motion.div>

      {/* Order Status KPIs */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <KPICard
          title="Total de Pedidos"
          value={metrics.totalOrders?.toLocaleString()}
          change="+45"
          changeType="positive"
          icon="📋"
          color="blue"
        />
        <KPICard
          title="Processando"
          value={metrics.processingOrders}
          change="+12"
          changeType="positive"
          icon="⏳"
          color="orange"
        />
        <KPICard
          title="Enviados"
          value={metrics.shippedOrders}
          change="+23"
          changeType="positive"
          icon="🚚"
          color="blue"
        />
        <KPICard
          title="Entregues"
          value={metrics.deliveredOrders}
          change="+67"
          changeType="positive"
          icon="✅"
          color="green"
        />
      </motion.div>

      {/* Revenue KPIs */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <KPICard
          title="Receita Total"
          value={`R$ ${metrics.totalRevenue?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}`}
          change="+15.2%"
          changeType="positive"
          icon="💰"
          color="green"
        />
        <KPICard
          title="Ticket Médio"
          value={`R$ ${metrics.avgOrderValue?.toFixed(2)}`}
          change="+8.7%"
          changeType="positive"
          icon="🎯"
          color="purple"
        />
        <KPICard
          title="Pedidos Hoje"
          value={metrics.todayOrders}
          change="+3"
          changeType="positive"
          icon="📅"
          color="blue"
        />
        <KPICard
          title="Taxa Conversão"
          value={`${metrics.conversionRate}%`}
          change="+0.3%"
          changeType="positive"
          icon="📈"
          color="orange"
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
            📊 Relatório de Vendas
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            📤 Exportar Pedidos
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            🔍 Busca Avançada
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            🔄 Atualizar Status
          </button>
        </div>
      </motion.div>

      {/* Status Filter Cards */}
      <motion.div 
        className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7, duration: 0.6 }}
      >
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-yellow-500">
          <div className="text-sm text-gray-600">Pendentes</div>
          <div className="text-2xl font-bold text-yellow-600">{metrics.pendingOrders}</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-blue-500">
          <div className="text-sm text-gray-600">Enviados</div>
          <div className="text-2xl font-bold text-blue-600">{metrics.shippedOrders}</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-green-500">
          <div className="text-sm text-gray-600">Entregues</div>
          <div className="text-2xl font-bold text-green-600">{metrics.deliveredOrders}</div>
        </div>
        <div className="bg-white p-4 rounded-xl shadow-md hover:shadow-lg transition-shadow cursor-pointer border-l-4 border-red-500">
          <div className="text-sm text-gray-600">Cancelados</div>
          <div className="text-2xl font-bold text-red-600">{metrics.cancelledOrders}</div>
        </div>
      </motion.div>

      {/* Orders Table */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <DataTable
          title="Lista de Pedidos"
          columns={orderColumns}
          data={orders}
          actions={actions}
        />
      </motion.div>
    </div>
  )
}