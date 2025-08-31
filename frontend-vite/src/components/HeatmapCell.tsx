import React from 'react';
import { FaCheck, FaRegCircle } from 'react-icons/fa';

export type ScheduleCell = {
  day: string;
  hour: string;
  active: boolean;
  intensity: number;
  lastUpdate: string;
};

interface HeatmapCellProps {
  cell: ScheduleCell;
  onToggle: () => void;
}

export const HeatmapCell: React.FC<HeatmapCellProps> = ({ cell, onToggle }) => {
  const [showTooltip, setShowTooltip] = React.useState(false);
  function getHeatColor(intensity: number) {
    if (intensity >= 80) return '#1b5e20';
    if (intensity >= 60) return '#43a047';
    if (intensity >= 40) return '#fbc02d';
    if (intensity >= 20) return '#eeeeee';
    return '#fafafa';
  }
  const bgColor = getHeatColor(cell.intensity);
  const boxShadow = '0 2px 8px #e0e0e0';
  return (
    <td
      className="relative rounded-xl transition-all duration-300 hover:scale-105"
      style={{ width: 88, height: 88, verticalAlign: 'middle', textAlign: 'center', position: 'relative', border: 'none', background: bgColor, boxShadow }}
    >
      <div
        className="flex flex-col items-center justify-center h-full w-full"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <button
          className={`flex items-center justify-center focus:outline-none rounded-full transition-all duration-200`}
          title="Ativar/desativar campanha manualmente"
          onClick={onToggle}
          style={{ width: 48, aspectRatio: '1/1', background: bgColor, boxShadow: 'none', border: 'none', outline: 'none', transition: 'box-shadow 0.2s' }}
          aria-pressed={cell.active}
          aria-label={cell.active ? 'Desativar horário' : 'Ativar horário'}
        >
          {cell.active
            ? <FaCheck className="text-green-700 text-lg" />
            : <FaRegCircle style={{ color: '#bdbdbd' }} className="text-lg" />}
        </button>
        {/* Tooltip tradicional: mostra vendas médias e conversão apenas no hover */}
        {showTooltip && (
          <div className="absolute z-10 left-1/2 -translate-x-1/2 bottom-2 flex flex-col items-center">
            <div className="bg-white/95 border border-gray-200 rounded-xl shadow-xl px-3 py-2 text-sm text-gray-900 whitespace-pre-line font-semibold backdrop-blur-md">
              Vendas médias: {Math.round(cell.intensity / 2) + 5}<br />
              Conversão: {(cell.intensity / 100 * 6.5).toFixed(1)}%
            </div>
            <div className="w-3 h-3 bg-white/95 border-l border-b border-gray-200 rotate-45 -mt-1"></div>
          </div>
        )}
      </div>
    </td>
  );
};
