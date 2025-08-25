import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import KPICard from "../components/KPICard";
import DataTable from "../components/DataTable";
import FiltrosInteligentes from "../components/FiltrosInteligentes";

export default function Products() {
  const [products, setProducts] = useState([]);
  const [metrics, setMetrics] = useState({});
  const [filteredProducts, setFilteredProducts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Mock de produtos
    const mockProducts = [
      { id: "ML001", name: "Smartphone Samsung Galaxy", category: "Eletrônicos", price: 899.99, stock: 45, status: "Ativo", sales: 127, views: 2340 },
      { id: "ML002", name: "Tênis Nike Air Max", category: "Calçados", price: 299.99, stock: 23, status: "Ativo", sales: 89, views: 1890 },
      { id: "ML003", name: "Notebook Dell Inspiron", category: "Eletrônicos", price: 2199.99, stock: 8, status: "Baixo Estoque", sales: 34, views: 980 },
      { id: "ML004", name: "Camiseta Adidas", category: "Roupas", price: 79.99, stock: 0, status: "Esgotado", sales: 156, views: 2100 },
      { id: "ML005", name: "Fone de Ouvido JBL", category: "Eletrônicos", price: 149.99, stock: 67, status: "Ativo", sales: 203, views: 3420 }
    ];
    setProducts(mockProducts);
    setFilteredProducts(mockProducts);

    // Mock de métricas
    setMetrics({
      totalProducts: 127,
      activeProducts: 98,
      lowStock: 15,
      outOfStock: 14,
      totalViews: 45280,
      totalSales: 609,
      avgConversion: 1.34,
      topCategory: "Eletrônicos"
    });
  }, []);

  const handleFilter = (filtros) => {
    const resultado = products.filter((p) => {
      return (
        (!filtros.categoria || p.category === filtros.categoria) &&
        (!filtros.status || p.status === filtros.status)
      );
    });
    setFilteredProducts(resultado);
  };

  const productColumns = [
    { field: "id", label: "ID", sortable: true },
    { field: "name", label: "Nome", sortable: true },
    { field: "category", label: "Categoria", sortable: true },
    { field: "price", label: "Preço", sortable: true, render: (value) => `R$ ${value.toFixed(2)}` },
    {
      field: "stock",
      label: "Estoque",
      sortable: true,
      render: (value) => (
        <span
          className={`font-semibold ${
            value === 0 ? "text-red-600" : value < 20 ? "text-orange-600" : "text-green-600"
          }`}
        >
          {value}
        </span>
      )
    },
    {
      field: "status",
      label: "Status",
      sortable: true,
      render: (value) => (
        <span
          className={`px-3 py-1 rounded-full text-xs font-medium ${
            value === "Ativo"
              ? "bg-green-100 text-green-800"
              : value === "Baixo Estoque"
              ? "bg-orange-100 text-orange-800"
              : "bg-red-100 text-red-800"
          }`}
        >
          {value}
        </span>
      )
    },
    { field: "sales", label: "Vendas", sortable: true },
    { field: "views", label: "Visualizações", sortable: true }
  ];

  const actions = [
    {
      label: "Editar",
      onClick: (product) => console.log("Editar produto:", product),
      className: "bg-blue-100 text-blue-700 hover:bg-blue-200"
    },
    {
      label: "Ver",
      onClick: (product) => navigate(`/produto/${product.id}`),
      className: "bg-gray-100 text-gray-700 hover:bg-gray-200"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="mb-8"
      >
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Produtos</h1>
        <p className="text-gray-600">Gerenciamento e visão geral dos produtos</p>
      </motion.div>

      {/* KPI Cards */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.6 }}
      >
        <KPICard title="Total de Produtos" value={metrics.totalProducts} change="+5" changeType="positive" icon="📦" color="blue" />
        <KPICard title="Produtos Ativos" value={metrics.activeProducts} change="+3" changeType="positive" icon="✅" color="green" />
        <KPICard title="Baixo Estoque" value={metrics.lowStock} change="+2" changeType="negative" icon="⚠️" color="orange" />
        <KPICard title="Esgotados" value={metrics.outOfStock} change="-1" changeType="positive" icon="❌" color="red" />
      </motion.div>

      {/* Performance KPIs */}
      <motion.div
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.4, duration: 0.6 }}
      >
        <KPICard title="Total de Visualizações" value={metrics.totalViews?.toLocaleString()} change="+12.8%" changeType="positive" icon="👁️" color="purple" />
        <KPICard title="Total de Vendas" value={metrics.totalSales} change="+8.5%" changeType="positive" icon="💰" color="green" />
        <KPICard title="Taxa de Conversão" value={`${metrics.avgConversion}%`} change="+0.2%" changeType="positive" icon="📈" color="blue" />
        <KPICard title="Categoria Top" value={metrics.topCategory} change="Eletrônicos" changeType="neutral" icon="🏆" color="orange" />
      </motion.div>

      {/* Filtros Inteligentes */}
      <motion.div
        className="mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.6 }}
      >
        <FiltrosInteligentes onFilter={handleFilter} />
      </motion.div>

      {/* Ações gerais */}
      <motion.div
        className="mb-6"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6, duration: 0.6 }}
      >
        <div className="flex flex-wrap gap-4">
          <button className="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-blue-700 transition-colors duration-300 shadow-lg">
            + Novo Produto
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            📥 Importar
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            📤 Exportar
          </button>
          <button className="bg-white text-gray-700 px-6 py-3 rounded-xl font-semibold hover:bg-gray-50 transition-colors duration-300 shadow-lg border">
            🔄 Atualizar Estoque
          </button>
        </div>
      </motion.div>

      {/* Tabela */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8, duration: 0.6 }}
      >
        <DataTable title="Lista de Produtos" columns={productColumns} data={filteredProducts} actions={actions} />
      </motion.div>
    </div>
  );
}
