import React from 'react';
import { motion } from 'framer-motion';

interface Campanha {
  id: string;
  nome?: string;
  produto?: { nome: string };
}
interface PromocaoCampanhaModalProps {
  open: boolean;
  onClose: () => void;
  campanhas: Campanha[];
  promocoes: Array<{ id: string; nome: string }>;
  onVincular: (campanhaId: string, promocaoId: string) => void;
}

const PromocaoCampanhaModal: React.FC<PromocaoCampanhaModalProps> = ({ open, onClose, campanhas, promocoes, onVincular }) => {
  const [campanhaId, setCampanhaId] = React.useState('');
  const [promocaoId, setPromocaoId] = React.useState('');

  const handleVincular = () => {
    if (campanhaId && promocaoId) {
      onVincular(campanhaId, promocaoId);
      setCampanhaId('');
      setPromocaoId('');
      onClose();
    }
  };

  if (!open) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 backdrop-blur-sm"
    >
      <div className="bg-white rounded-3xl shadow-2xl p-8 w-full max-w-md mx-4 animate-fade-in">
        <h2 className="text-2xl font-bold mb-4 text-pink-700 text-center">Vincular Promoção à Campanha</h2>
        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Campanha</label>
          <select value={campanhaId} onChange={e => setCampanhaId(e.target.value)} className="w-full p-2 border rounded">
            <option value="">Selecione...</option>
            {campanhas.map(c => (
              <option key={c.id} value={c.id}>{c.produto?.nome || c.nome}</option>
            ))}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-bold mb-2">Promoção</label>
          <select value={promocaoId} onChange={e => setPromocaoId(e.target.value)} className="w-full p-2 border rounded">
            <option value="">Selecione...</option>
            {promocoes.map(p => (
              <option key={p.id} value={p.id}>{p.nome}</option>
            ))}
          </select>
        </div>
        <div className="flex gap-4 justify-end mt-6">
          <button onClick={onClose} className="px-4 py-2 rounded bg-gray-200 text-gray-700 font-bold hover:bg-gray-300">Cancelar</button>
          <button onClick={handleVincular} disabled={!campanhaId || !promocaoId} className="px-4 py-2 rounded bg-pink-600 text-white font-bold hover:bg-pink-700 disabled:opacity-50">Vincular</button>
        </div>
      </div>
    </motion.div>
  );
};

export default PromocaoCampanhaModal;
