import React, { useState, useEffect } from 'react';
import { FaRobot } from 'react-icons/fa';
import { motion } from 'framer-motion';
import { HeatmapCell, ScheduleCell } from '../components/HeatmapCell';
import { HeatmapLegend } from '../components/HeatmapLegend';
import { useSchedule } from '../hooks/useSchedule';
// Removendo import do componente antigo
import PromocoesCampanhasBox from '../components/PromocoesCampanhasBox';
import PromocaoCampanhaModal from '../components/PromocaoCampanhaModal';

const MODO_OPTIONS = [
  { value: '', label: 'Selecione...' },
  { value: 'manual', label: 'Manual' },
  { value: 'produto', label: 'Produto' }
];

const days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom'];
const hours = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00', '18:00'];

const API_GET = '/api/campaigns/1/schedule';
const API_PATCH = '/api/campaigns/1/schedule';

const DynamicOptimization: React.FC = () => {
  const { schedule, setSchedule, loading, saving, error, success, saveSchedule } = useSchedule(API_GET, API_PATCH);
  const [logs, setLogs] = useState<string[]>(['Dados carregados do backend.']);
  const [toast, setToast] = useState<string | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [modoAgendamento, setModoAgendamento] = useState('');
  const [desconto, setDesconto] = useState(0);
  const [horario, setHorario] = useState('08:00');
  const [duracao, setDuracao] = useState(7);
  const [orcamento, setOrcamento] = useState(100);
  const [campanhas, setCampanhas] = useState<any[]>([]);
  const [promocoes, setPromocoes] = useState<any[]>([]);

  useEffect(() => {
    setPromocoes([
      { id: 'a', nome: 'Promoção 10% OFF' },
      { id: 'b', nome: 'Frete Grátis' },
    ]);
  }, []);

  const handleToggleCell = (hIdx: number, dIdx: number) => {
    setSchedule((prev: ScheduleCell[][]) => {
      const updated = prev.map((row, i) =>
        row.map((cell, j) => {
          if (i === hIdx && j === dIdx) {
            return { ...cell, active: !cell.active };
          }
          return cell;
        })
      );
      return updated;
    });
  };

  const handleSave = async () => {
    await saveSchedule();
    setLogs((prev) => [...prev, 'Alterações salvas no backend.']);
    setToast('Alterações salvas!');
    setTimeout(() => setToast(null), 2500);
  };

  const handleVincularPromocao = (campanhaId: string, promocaoId: string) => {
    setCampanhas(prev => prev.map(c => c.id === campanhaId ? { ...c, promocaoId } : c));
    setLogs((prev) => [...prev, `Promoção ${promocaoId} vinculada à campanha ${campanhaId}.`]);
    setToast('Promoção vinculada com sucesso!');
    setTimeout(() => setToast(null), 2500);
  };

  const handleCriarCampanha = (campanha: any) => {
    setCampanhas(prev => [...prev, campanha]);
    setLogs((prev) => [...prev, `Campanha criada: ${campanha.produto.nome}`]);
    setToast('Campanha criada com sucesso!');
    setTimeout(() => setToast(null), 2500);
  };

  // Handlers dos campos do formulário
  const handleSelecionarModo = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setModoAgendamento(e.target.value);
  };
  const handleDesconto = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDesconto(Number(e.target.value));
  };
  const handleHorario = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setHorario(e.target.value);
  };
  const handleDuracao = (e: React.ChangeEvent<HTMLInputElement>) => {
    setDuracao(Number(e.target.value));
  };
  const handleOrcamento = (e: React.ChangeEvent<HTMLInputElement>) => {
    setOrcamento(Number(e.target.value));
  };
  const handleCriarCampanhaUX = () => {
    if (!modoAgendamento || desconto < 0 || duracao < 1 || orcamento < 1) {
      setToast('Preencha todos os campos corretamente!');
      setTimeout(() => setToast(null), 2500);
      return;
    }
    const campanha = {
      id: Date.now().toString(),
      modo: modoAgendamento,
      desconto,
      horario,
      duracao,
      orcamento,
      produto: { nome: modoAgendamento === 'produto' ? 'Produto selecionado' : 'Manual' },
      status: 'ativa'
    };
    setCampanhas(prev => [...prev, campanha]);
    setLogs((prev) => [...prev, `Campanha criada: ${campanha.produto.nome}`]);
    setToast('Campanha criada com sucesso!');
    setTimeout(() => setToast(null), 2500);
    // Resetar campos
    setModoAgendamento('');
    setDesconto(0);
    setHorario('08:00');
    setDuracao(7);
    setOrcamento(100);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-purple-50 to-yellow-50 p-8 relative font-sans">
      <style>{`
        .glass-card {
          background: rgba(255,255,255,0.7);
          box-shadow: 0 4px 16px 0 rgba(0,0,0,0.08);
          backdrop-filter: blur(12px);
          border-radius: 2rem;
          border: 1.5px solid rgba(255,255,255,0.18);
        }
      `}</style>
      {toast && (
        <div className="fixed top-6 right-6 z-50 bg-gradient-to-r from-green-500 via-green-400 to-green-600 text-white px-8 py-4 rounded-2xl shadow-2xl font-bold animate-fade-in border-4 border-green-200 flex items-center gap-3">
          <FaRobot className="text-white text-2xl animate-bounce" />
          <span>{toast}</span>
        </div>
      )}
      {/* Painel de configuração de campanhas de ads/promoção sempre visível no topo */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-8">
        <div className="glass-card p-10 mb-4 flex flex-col gap-4 border-2 border-pink-200 max-w-xl mx-auto">
          <h2 className="text-3xl font-extrabold text-pink-700 mb-4">Configurar Campanha de Ads/Promoção</h2>
          <form className="flex flex-col gap-4" onSubmit={e => {e.preventDefault(); handleCriarCampanhaUX();}}>
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-pink-700">Modo de Agendamento</label>
              <select value={modoAgendamento} onChange={handleSelecionarModo} className="p-3 rounded-lg border border-pink-200 text-lg">
                {MODO_OPTIONS.map(opt => (
                  <option key={opt.value} value={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-pink-700">Desconto (%)</label>
              <input type="number" min={0} max={100} value={desconto} onChange={handleDesconto} className="p-3 rounded-lg border border-pink-200 text-lg" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-pink-700">Horário de ativação</label>
              <select value={horario} onChange={handleHorario} className="p-3 rounded-lg border border-pink-200 text-lg">
                {hours.map(h => <option key={h} value={h}>{h}</option>)}
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-pink-700">Duração (dias)</label>
              <input type="number" min={1} max={30} value={duracao} onChange={handleDuracao} className="p-3 rounded-lg border border-pink-200 text-lg" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-semibold text-pink-700">Orçamento (R$)</label>
              <input type="number" min={1} value={orcamento} onChange={handleOrcamento} className="p-3 rounded-lg border border-pink-200 text-lg" />
            </div>
            <button type="submit" className="px-6 py-3 rounded-xl bg-pink-600 text-white font-extrabold shadow transition-all duration-200 mt-2">Criar campanha</button>
          </form>
        </div>
      </motion.div>
      {/* Box Promoções & Campanhas Ativas - sempre mostra exemplo se vazio */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className="mb-8">
        <div className="glass-card p-10 flex flex-col gap-6 border-2 border-pink-200">
          <div className="flex items-center justify-center w-28 h-28 rounded-full bg-pink-200 shadow-xl mb-4 animate-pulse relative">
            <span className="absolute bottom-2 right-2 text-xs text-pink-700 font-bold">Descontos Inteligentes</span>
          </div>
          <div className="w-full">
            <PromocoesCampanhasBox campanhas={campanhas} promocoes={promocoes} />
            <div className="mt-8 flex justify-end">
              <button
                className={`px-6 py-3 rounded-xl bg-pink-500 text-white font-extrabold shadow transition-all duration-200 ${campanhas.length === 0 ? 'opacity-50 cursor-not-allowed' : ''}`}
                onClick={() => campanhas.length > 0 && setModalOpen(true)}
                disabled={campanhas.length === 0}
                title={campanhas.length === 0 ? 'Crie uma campanha primeiro' : 'Vincular promoção à campanha'}
              >
                Vincular promoção à campanha
              </button>
            </div>
          </div>
        </div>
      </motion.div>
      {/* Modal de vinculação destacado e centralizado */}
      {modalOpen && (
        <div style={{zIndex: 9999, position: 'fixed', inset: 0}}>
          <div className="fixed inset-0 bg-black bg-opacity-60 backdrop-blur-sm flex items-center justify-center">
            <PromocaoCampanhaModal
              open={modalOpen}
              onClose={() => setModalOpen(false)}
              campanhas={campanhas}
              promocoes={promocoes}
              onVincular={handleVincularPromocao}
            />
          </div>
        </div>
      )}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }} className="mb-8">
        <h1 className="text-5xl font-extrabold text-purple-700 mb-4 flex items-center gap-4 drop-shadow-xl">
          Otimização Dinâmica
        </h1>
        <p className="text-purple-600 text-xl font-semibold">Calendário semanal interativo para agendamento de campanhas com mapa de calor.</p>
      </motion.div>
      <motion.div className="mb-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2, duration: 0.6 }}>
        <div className="glass-card p-10 mb-8 border-2 border-green-200">
          <h2 className="text-4xl font-extrabold mb-8 text-green-700 flex items-center gap-2 drop-shadow-xl">
            Calendário & Mapa de Calor
          </h2>
          <div className="flex flex-row gap-8 w-full">
            <aside className="hidden md:flex flex-col gap-8 w-80 min-w-80 sticky top-8 h-fit">
              <div className="glass-card p-6 flex flex-col gap-4 border border-green-100">
                <HeatmapLegend />
                <button
                  className={`px-6 py-3 rounded-xl bg-pink-500 text-white font-extrabold shadow transition-all duration-200 ${saving ? 'opacity-50 cursor-not-allowed' : ''}`}
                  onClick={handleSave}
                  disabled={saving}
                  data-tooltip={saving ? 'Salvando...' : 'Salvar alterações'}
                >{saving ? 'Salvando...' : 'Salvar alterações'}</button>
                {success && <span className="mt-2 text-green-700 font-bold">{success}</span>}
                {error && <span className="mt-2 text-red-700 font-bold">{error}</span>}
              </div>
              <div className="glass-card p-6 border border-green-100">
                <h3 className="text-lg font-bold text-green-700 mb-2 flex items-center gap-2">📝 Logs recentes</h3>
                <ul className="text-xs text-gray-600 list-disc pl-4">
                  {logs.map((log: string, idx: number) => (
                    <li key={idx}>{log}</li>
                  ))}
                </ul>
              </div>
            </aside>
            <main className="flex-1">
              {loading ? (
                <div className="text-center text-gray-500 text-xl font-bold animate-pulse">Carregando dados...</div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="min-w-full text-center border-separate" style={{ borderSpacing: '6px', tableLayout: 'fixed', width: '100%' }}>
                    <thead>
                      <tr>
                        <th className="p-2 bg-green-50 rounded-lg" style={{ width: 70 }}></th>
                        {days.map((day) => (
                          <th key={day} className="p-2 bg-green-50 font-bold rounded-lg text-green-700" style={{ width: 70 }}>{day}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {hours.map((hour, hIdx) => (
                        <tr key={hour}>
                          <td className="p-2 bg-green-50 font-bold rounded-lg text-green-700" style={{ width: 70 }}>{hour}</td>
                          {days.map((day, dIdx) => {
                            const cell = schedule[hIdx]?.[dIdx];
                            if (!cell) return <td key={day + hour}></td>;
                            return (
                              <HeatmapCell
                                key={day + hour}
                                cell={cell}
                                onToggle={() => handleToggleCell(hIdx, dIdx)}
                              />
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </main>
          </div>
        </div>
      </motion.div>
      <motion.div className="mb-8" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3, duration: 0.6 }}>
        <div className="glass-card p-8 border-2 border-purple-200">
          <h2 className="text-2xl font-extrabold mb-4 text-purple-700 flex items-center gap-2">🔮 Logs & Resultados IA</h2>
          <ul className="text-gray-700 text-lg font-medium">
            {logs.map((log: string, idx: number) => (
              <li key={idx} className="mb-2">{log}</li>
            ))}
          </ul>
        </div>
      </motion.div>
    </div>
  );
};

export default DynamicOptimization;
