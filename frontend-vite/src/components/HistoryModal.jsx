import React from 'react';

function HistoryModal({ history, onClose }) {
  return (
    <div className="history-modal">
      <h3>Histórico de Ações</h3>
      <button onClick={onClose}>Fechar</button>
      <ul>
        {history.map((item, idx) => (
          <li key={idx}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default HistoryModal;
