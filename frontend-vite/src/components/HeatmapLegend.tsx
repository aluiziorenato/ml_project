import React from 'react';
import { FaCheck, FaRegCircle } from 'react-icons/fa';

export function HeatmapLegend() {
  return (
    <div className="mt-6 flex flex-wrap gap-6 items-center justify-center">
      <div className="flex items-center gap-2"><span className="w-7 h-7 bg-gradient-to-br from-green-700 to-green-400 rounded-xl border border-white/40 shadow" /> <span className="font-semibold text-green-700">Pico (Verde escuro)</span></div>
      <div className="flex items-center gap-2"><span className="w-7 h-7 bg-gradient-to-br from-yellow-200 to-yellow-400 rounded-xl border border-white/40 shadow" /> <span className="font-semibold text-yellow-700">Intermediário (Amarelo)</span></div>
      <div className="flex items-center gap-2"><span className="w-7 h-7 bg-gray-100 rounded-xl border border-white/40 shadow" /> <span className="font-semibold text-gray-700">Baixo/Sem dados (Cinza)</span></div>
      <div className="flex items-center gap-2"><FaCheck className="text-green-700 text-xl" /> <span className="font-semibold text-green-700">Ativo</span></div>
      <div className="flex items-center gap-2"><FaRegCircle className="text-gray-400 text-xl" /> <span className="font-semibold text-gray-500">Inativo</span></div>
    </div>
  );
}
