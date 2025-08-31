import React from 'react';

function StrategyPanel({ modes, selectedMode, onModeChange, onActivate }) {
  return (
    <div>
      <h2>Painel de Modos Estratégicos</h2>
      <select value={selectedMode} onChange={e => onModeChange(e.target.value)}>
        {modes.map(mode => (
          <option key={mode} value={mode}>{mode}</option>
        ))}
      </select>
      <button onClick={onActivate}>Ativar Modo</button>
    </div>
  );
}

export default StrategyPanel;
