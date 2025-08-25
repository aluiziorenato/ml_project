import React, { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import KPICard from "../components/KPICard";
import GraficoVendasDiarias from "../components/GraficoVendasDiarias";
import GraficoVisitasConversao from "../components/GraficoVisitasConversao";

export default function ProdutoDetalhe() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [produto, setProduto] = useState(null);
  const [metrics7d, setMetrics7d] = useState(null);
  const [metrics30d, setMetrics30d] = useState(null);
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState(null);

  // Séries mockadas para os gráficos (formato esperado da API)
  const vendas30dSeries = [
    { date: "2025-07-28", value: 4 },
    { date: "2025-07-29", value: 7 },
    { date: "2025-07-30", value: 5 },
    { date: "2025-07-31", value: 6 },
    { date: "2025-08-01", value: 3 }
  ];

  const visitas30dSeries = [
    { date: "2025-07-28", value: 310 },
    { date: "2025-07-29", value: 280 },
    { date: "2025-07-30", value: 295 },
    { date: "2025-07-31", value: 312 },
    { date: "2025-08-01", value: 287 }
  ];

  const conversao30dSeries = [
    { date: "2025-07-28", value: 1.2 },
    { date: "2025-07-29", value: 1.4 },
    { date: "2025-07-30", value: 1.3 },
    { date: "2025-07-31", value: 1.5 },
    { date: "2025-08-01", value: 1.35 }
  ];

  useEffect(() => {
    setLoading(true);
    setErr(null);

    // Mock de dados do produto e métricas
    const mockProduto = {
      id,
      nome: "Produto Exemplo",
      sku: "SKU-001",
      preco: 149.9,
      status: "Ativo",
      estoque_atual: 42
    };

    const mock7d = {
      sales: 28,
      revenue: 4321.5,
      visits: 2100,
      conversion: 1.4
    };

    const mock30d = {
      sales: 128,
      revenue: 17234.9,
      visits: 8421,
      conversion: 1.52
    };

    const t = setTimeout(() => {
      try {
        setProduto(mockProduto);
        setMetrics7d(mock7d);
        setMetrics30d(mock30d);
      } catch (e) {
        setErr(e);
      } finally {
        setLoading(false);
      }
    }, 300);

    return () => clearTimeout(t);
  }, [id]);

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 w-64 bg-gray-200 rounded" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-24 bg-gray-200 rounded" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (err) {
    return (
      <div className="p-6">
        <p className="text-red-600 font-medium">
          Erro ao carregar: {String(err.message || err)}
        </p>
        <button
          onClick={() => window.location.reload()}
          className="mt-4 px-4 py-2 rounded bg-gray-900 text-white"
        >
          Tentar novamente
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-6 flex flex-wrap items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{produto.nome}</h1>
          <p className="text-gray-600">
            ID: <span className="font-mono">{produto.id}</span> • SKU:{" "}
            <span className="font-mono">{produto.sku}</span>
          </p>
        </div>

        <div className="flex gap-2">
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 rounded-lg border bg-white text-gray-800 hover:bg-gray-50"
          >
            ← Voltar
          </button>
          <Link
            to="/produtos"
            className="px-4 py-2 rounded-lg border bg-white text-gray-800 hover:bg-gray-50"
          >
            Lista de produtos
          </Link>
          <button className="px-4 py-2 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700">
            Editar preço/status
          </button>
          <button className="px-4 py-2 rounded-lg bg-gray-900 text-white hover:bg-black">
            Sincronizar marketplace
          </button>
        </div>
      </motion.div>

      {/* KPIs */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        <KPICard
          title="Vendas 7d"
          value={metrics7d?.sales ?? "-"}
          change="+4"
          changeType="positive"
          icon="🛒"
          color="blue"
        />
        <KPICard
          title="Vendas 30d"
          value={metrics30d?.sales ?? "-"}
          change="+12"
          changeType="positive"
          icon="🛍️"
          color="green"
        />
        <KPICard
          title="Receita 7d"
          value={
            metrics7d?.revenue != null
              ? metrics7d.revenue.toLocaleString("pt-BR", {
                  style: "currency",
                  currency: "BRL"
                })
              : "-"
          }
          change="+6%"
          changeType="positive"
          icon="💵"
          color="purple"
        />
        <KPICard
          title="Visitas 30d"
          value={metrics30d?.visits?.toLocaleString() ?? "-"}
          change="+9%"
          changeType="positive"
          icon="👁️"
          color="orange"
        />
        <KPICard
          title="Conversão 30d"
          value={metrics30d ? `${metrics30d.conversion}%` : "-"}
          change="+0.1%"
          changeType="positive"
          icon="📈"
          color="blue"
        />
        <KPICard
          title="Estoque"
          value={produto.estoque_atual}
          change=""
          changeType="neutral"
          icon="📦"
          color="green"
        />
        <KPICard
          title="Preço"
          value={produto.preco.toLocaleString("pt-BR", {
            style: "currency",
            currency: "BRL"
          })}
          change=""
          changeType="neutral"
          icon="🏷️"
          color="purple"
        />
        <div className="rounded-xl bg-white p-4 shadow-sm border">
          <div className="text-sm text-gray-500 mb-1">Status</div>
          <div>
            <span
              className={`px-3 py-1 rounded-full text-xs font-medium ${
                produto.status === "Ativo"
                  ? "bg-green-100 text-green-800"
                  : produto.status === "Baixo Estoque"
                  ? "bg-orange-100 text-orange-800"
                  : "bg-red-100 text-red-800"
              }`}
            >
              {produto.status}
            </span>
          </div>
        </div>
      </motion.div>

      {/* Gráficos */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.4 }}
        className="grid grid-cols-1 lg:grid-cols-2 gap-6"
      >
        <div className="rounded-xl bg-white p-4 shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Vendas diárias (30 dias)
          </h3>
          <GraficoVendasDiarias data={vendas30dSeries} />
        </div>

        <div className="rounded-xl bg-white p-4 shadow-sm border">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Visitas x Conversão
          </h3>
          <GraficoVisitasConversao
            visitas={visitas30dSeries}
            conversao={conversao30dSeries}
          />
        </div>
      </motion.div>
    </div>
  );
}
