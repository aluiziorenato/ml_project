import React from 'react';
import './WeeklyScheduler.css';

const WeeklyScheduler = ({ weekDays, hours, schedule, heatmap, lastUpdate, onCellToggle }) => {
  // Função para interpolar cor do mapa de calor (de amarelo claro para laranja intenso)
  // Cores para vendas: insuficiente, moderada, boa, intensa
  const getHeatColor = (intensity) => {
    // Faixas mockadas:
    // 1-2%: laranja (#ff9800)
    // 3-10%: azul (#2196f3)
    // 11-15%: verde (#4caf50)
    // 16%+: verde escuro (#1b5e20)
    if (intensity >= 0.01 && intensity <= 0.02) return '#ff9800'; // laranja
    if (intensity >= 0.03 && intensity <= 0.10) return '#2196f3'; // azul
    if (intensity >= 0.11 && intensity <= 0.15) return '#4caf50'; // verde
    if (intensity >= 0.16) return '#1b5e20'; // verde escuro
    return '#e0e0e0'; // sem aproveitamento
  };

  return (
    <div className="weekly-scheduler">
      <div className="ws-header">
        <span className="ws-title">Calendário Semanal de Ativação</span>
        <span className="ws-last-update">Última atualização: {lastUpdate}</span>
      </div>
      <div className="ws-legend">
        <span className="ws-legend-item ws-active">Ativo</span>
        <span className="ws-legend-item ws-inactive">Inativo</span>
        <span className="ws-legend-item ws-heat" style={{background: 'linear-gradient(90deg, #ffe066 40%, #ff6f00 100%)'}}>Mapa de calor</span>
      </div>
      <div className="ws-grid">
        <div className="ws-row ws-header-row">
          <div className="ws-cell ws-corner"></div>
          {weekDays.map((day, dIdx) => (
            <div key={day} className="ws-cell ws-day-header">{day}</div>
          ))}
        </div>
        {hours.map((hour, hIdx) => (
          <div className="ws-row" key={hour}>
            <div className="ws-cell ws-hour-header">{hour}</div>
            {weekDays.map((_, dIdx) => {
              const isActive = schedule[dIdx][hIdx];
              const intensity = heatmap[dIdx][hIdx];
              const cellClass = [
                'ws-cell',
                isActive ? 'ws-active' : 'ws-inactive',
                intensity > 0 ? 'ws-has-heat' : '',
                isActive ? 'ws-active-border' : '',
              ].join(' ');
              const tooltip = `${isActive ? 'Campanha ativa' : 'Campanha inativa'}\nDesempenho: ${Math.round(intensity * 100)}%`;
              // O gradiente do heatmap é sempre o fundo principal; ativo tem borda verde
              const heatColor = getHeatColor(intensity);
              const style = { background: heatColor || '#fafafa' };
              return (
                <div
                  key={dIdx}
                  className={cellClass}
                  title={tooltip}
                  onClick={() => onCellToggle(dIdx, hIdx)}
                  style={style}
                >
                  <input
                    type="checkbox"
                    checked={isActive}
                    onChange={() => onCellToggle(dIdx, hIdx)}
                    className="ws-checkbox"
                  />
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WeeklyScheduler;
