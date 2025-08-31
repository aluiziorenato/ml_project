import React, { useState } from 'react';
import { mockIaData } from '../../mock/mockIaData';

const produtos = mockIaData.slice(0, 10);

interface ConfiguradorCampanhaAdsPromocaoProps {
  onCriarCampanha: (campanha: any) => void;
}

const ConfiguradorCampanhaAdsPromocao: React.FC<ConfiguradorCampanhaAdsPromocaoProps> = ({ onCriarCampanha }) => {
  // Modo de agendamento: manual, IA otimizado, híbrido
  const [modoAgendamento, setModoAgendamento] = useState<'manual'|'ia'|'hibrido'>('manual');
  // Produto elegível para campanha (API Mercado Livre: product_id)
  const [produtoId, setProdutoId] = useState('');
  // Desconto percentual (API: discount_percentage)
  const [desconto, setDesconto] = useState(0);
  // Horário de ativação (API: start_time)
  const [horario, setHorario] = useState('08:00');
  // Orçamento diário/mensal (API: budget)
  const [orcamento, setOrcamento] = useState(100);
  // Duração em dias (API: duration_days)
  const [duracao, setDuracao] = useState(7);

  function handleCriarCampanha(e: React.FormEvent) {
    e.preventDefault();
    const produto = produtos.find(p => p.id === produtoId);
    if (!produto) return;
    onCriarCampanha({
      id: Date.now().toString(),
      produto,
      desconto,
      horario,
      orcamento,
      duracao,
      status: 'ativa',
    });
  }

  return (
    <div className="bg-white rounded-2xl shadow-2xl p-8 border border-gray-200 mb-8">
      <h2 className="text-2xl font-bold text-blue-700 mb-4">Configurar Campanha de Ads/Promoção</h2>
      {/* Seleção do modo de agendamento */}
      <form className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6" onSubmit={handleCriarCampanha}>
        <div className="md:col-span-2">
          <label className="block font-semibold mb-1">Modo de Agendamento</label>
          <select value={modoAgendamento} onChange={e => setModoAgendamento(e.target.value as 'manual'|'ia'|'hibrido')} className="w-full p-2 border rounded">
            <option value="manual">Manual</option>
            <option value="ia">IA Otimizado</option>
            <option value="hibrido">Híbrido</option>
          </select>
        </div>
        {/* Produto elegível (product_id) */}
        <div>
          <label className="block font-semibold mb-1">Produto</label>
          <select value={produtoId} onChange={e => setProdutoId(e.target.value)} className="w-full p-2 border rounded">
            <option value="">Selecione...</option>
            {produtos.map(p => (
              <option key={p.id} value={p.id}>{p.nome}</option>
            ))}
          </select>
        </div>
        {/* Desconto percentual (discount_percentage) */}
        <div>
          <label className="block font-semibold mb-1">Desconto (%)</label>
          <input type="number" min={0} max={50} value={desconto} onChange={e => setDesconto(Number(e.target.value))} className="w-full p-2 border rounded" />
        </div>
        {/* Campos dinâmicos conforme modo de agendamento */}
        {modoAgendamento === 'manual' && (
          <>
            {/* Horário de ativação (start_time) */}
            <div>
              <label className="block font-semibold mb-1">Horário de ativação</label>
              <select value={horario} onChange={e => setHorario(e.target.value)} className="w-full p-2 border rounded">
                {['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'].map(h => (
                  <option key={h} value={h}>{h}</option>
                ))}
              </select>
            </div>
            {/* Duração em dias (duration_days) */}
            <div>
              <label className="block font-semibold mb-1">Duração (dias)</label>
              <input type="number" min={1} max={30} value={duracao} onChange={e => setDuracao(Number(e.target.value))} className="w-full p-2 border rounded" />
            </div>
          </>
        )}
        {modoAgendamento === 'ia' && (
          <>
            {/* IA sugere horário e duração */}
            <div className="md:col-span-2">
              <label className="block font-semibold mb-1">Sugestão IA</label>
              <div className="p-2 border rounded bg-gray-50 text-gray-700 text-sm">Horário e duração serão sugeridos automaticamente pela IA com base em dados históricos e previsão de demanda.</div>
            </div>
          </>
        )}
        {modoAgendamento === 'hibrido' && (
          <>
            {/* Usuário define preferências, IA ajusta/agiliza */}
            <div>
              <label className="block font-semibold mb-1">Horário preferencial</label>
              <select value={horario} onChange={e => setHorario(e.target.value)} className="w-full p-2 border rounded">
                {['08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00'].map(h => (
                  <option key={h} value={h}>{h}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="block font-semibold mb-1">Duração preferencial (dias)</label>
              <input type="number" min={1} max={30} value={duracao} onChange={e => setDuracao(Number(e.target.value))} className="w-full p-2 border rounded" />
            </div>
            <div className="md:col-span-2">
              <label className="block font-semibold mb-1">Ajuste IA</label>
              <div className="p-2 border rounded bg-gray-50 text-gray-700 text-sm">A IA pode ajustar o agendamento para maximizar resultados com base nas preferências informadas.</div>
            </div>
          </>
        )}
        {/* Orçamento (budget) */}
        <div>
          <label className="block font-semibold mb-1">Orçamento (R$)</label>
          <input type="number" min={10} max={10000} value={orcamento} onChange={e => setOrcamento(Number(e.target.value))} className="w-full p-2 border rounded" />
        </div>
        <div className="flex items-end">
          <button type="submit" className="px-6 py-3 rounded-xl bg-blue-600 text-white font-bold shadow-lg hover:bg-blue-700 transition w-full">Criar campanha</button>
        </div>
      </form>
      {/* Lista de campanhas agora é controlada pelo componente pai */}
    </div>
  );
};

export default ConfiguradorCampanhaAdsPromocao;
