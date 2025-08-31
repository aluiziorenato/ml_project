import React from 'react';
import { FaPercentage, FaClock, FaChartLine, FaBullhorn } from 'react-icons/fa';

interface PromocoesCampanhasBoxProps {
  campanhas: any[];
  promocoes: any[];
}

const PromocoesCampanhasBox: React.FC<PromocoesCampanhasBoxProps> = ({ campanhas, promocoes }) => {
  // Descontos inteligentes: campanhas com desconto > 0
  const descontosInteligentes = campanhas.filter(c => c.desconto > 0).slice(0, 3);
  // Agendamentos: campanhas com horário definido
  const agendamentos = campanhas.filter(c => c.horario).map(c => ({ horario: c.horario, produto: c.produto.nome })).slice(0, 3);
  // Previsão de impacto: mock simples
  const previsao = descontosInteligentes.length > 0 ? {
    roi: descontosInteligentes.reduce((acc, c) => acc + (c.produto.roi || 1), 0) / descontosInteligentes.length,
    vendas: descontosInteligentes.reduce((acc, c) => acc + (c.produto.vendas || 0), 0),
  } : { roi: 0, vendas: 0 };
  // Campanhas ativas
  const campanhasAtivas = campanhas.filter(c => c.status === 'ativa');
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      {/* Descontos inteligentes */}
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-pink-100 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-2">
          <FaPercentage className="text-pink-500 text-2xl" />
          <span className="font-bold text-pink-700 text-lg">Descontos inteligentes</span>
        </div>
        <ul className="text-sm text-gray-700">
          {descontosInteligentes.map(c => (
            <li key={c.id} className="flex items-center gap-2 mb-1">
              <img src={c.produto.imagem} alt={c.produto.nome} className="w-6 h-6 rounded" />
              <span className="font-semibold text-pink-700">{c.produto.nome}</span>
              <span className="text-xs text-gray-500">{c.desconto}%</span>
              <span className="text-xs text-green-600">{c.produto.vendas || 0} vendas</span>
            </li>
          ))}
        </ul>
      </div>
      {/* Agendamento automático */}
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-purple-100 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-2">
          <FaClock className="text-purple-500 text-2xl" />
          <span className="font-bold text-purple-700 text-lg">Agendamento automático</span>
        </div>
        <ul className="text-sm text-gray-700">
          {agendamentos.map((a, idx) => (
            <li key={idx} className="flex items-center gap-2 mb-1">
              <FaClock className="text-purple-400" />
              <span className="font-semibold text-purple-700">{a.horario}</span>
              <span className="text-xs text-gray-500">{a.produto}</span>
            </li>
          ))}
        </ul>
      </div>
      {/* Previsão de impacto */}
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-green-100 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-2">
          <FaChartLine className="text-green-500 text-2xl" />
          <span className="font-bold text-green-700 text-lg">Previsão de impacto</span>
        </div>
        <div className="flex flex-col gap-1 text-sm text-gray-700">
          <span className="font-semibold text-green-700">ROI médio: {previsao.roi.toFixed(2)}</span>
          <span className="text-xs text-gray-500">Vendas previstas: {previsao.vendas}</span>
        </div>
      </div>
      {/* Campanhas ativas */}
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-blue-100 flex flex-col gap-2">
        <div className="flex items-center gap-2 mb-2">
          <FaBullhorn className="text-blue-500 text-2xl" />
          <span className="font-bold text-blue-700 text-lg">Campanhas ativas</span>
        </div>
        {campanhasAtivas.length === 0 ? (
          <div className="text-gray-400 text-sm p-4 text-center">Nenhuma campanha ativa configurada.<br/>Crie uma campanha para visualizar aqui.</div>
        ) : (
          <ul className="text-sm text-gray-700">
            {campanhasAtivas.map(c => (
              <li key={c.id} className="flex items-center gap-2 mb-2 p-2 rounded-xl border border-blue-50 bg-blue-50/40">
                <img src={c.produto.imagem} alt={c.produto.nome} className="w-8 h-8 rounded shadow" />
                <span className="font-semibold text-blue-700">{c.produto.nome}</span>
                <span className="text-xs px-2 py-1 rounded bg-pink-100 text-pink-700 font-bold">{c.desconto}%</span>
                <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-700 font-bold">{c.produto.vendas || 0} vendas</span>
                {c.promocaoId && (
                  <span className="text-xs px-2 py-1 rounded bg-purple-100 text-purple-700 font-bold">Promoção: {promocoes.find(p => p.id === c.promocaoId)?.nome}</span>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default PromocoesCampanhasBox as React.FC<PromocoesCampanhasBoxProps>;
