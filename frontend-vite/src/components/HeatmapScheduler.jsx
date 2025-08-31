import React from 'react';

function HeatmapScheduler() {
  return (
    <div></div>
  );
}

export default HeatmapScheduler;

import React from 'react';


// Mock para 31 dias com intensidade
const dias = Array.from({ length: 31 }, (_, i) => {
  // count simula intensidade (0-5)
  const count = Math.floor(Math.abs(Math.sin(i + 1) * 5));
  let status = 'inactive';
  if (count >= 4) status = 'recommended';
  else if (count >= 2) status = 'active';
  return {
    dia: i + 1,
    count,
    status
  };
});

function HeatmapScheduler() {
  // Renderiza 7 blocos por linha
  const linhas = [];
  for (let i = 0; i < dias.length; i += 7) {
    linhas.push(dias.slice(i, i + 7));
  }

  // Função para cor de fundo baseada na intensidade
  const getColor = (count) => {
    if (count >= 4) return '#ffb300'; // recomendado
    if (count === 3) return '#90caf9'; // ativo forte
    if (count === 2) return '#b3d1ff'; // ativo médio
    if (count === 1) return '#e0e0e0'; // inativo
    return '#f7f7fa'; // vazio
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', justifyContent: 'flex-start', maxWidth: 340 }}>
      <h2 style={{ fontSize: '1em', marginBottom: 8, textAlign: 'left' }}>Calendário de Agendamento</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'flex-start', justifyContent: 'flex-start' }}>
import React from 'react';

function HeatmapScheduler() {
  return (
    <div>
      {/* Calendário removido */}
    </div>
  );
}

export default HeatmapScheduler;
                  display: 'flex',
