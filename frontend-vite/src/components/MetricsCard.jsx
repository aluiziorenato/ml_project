import React from 'react';

function MetricsCard({ metrics }) {
  return (
    <div className="metrics-card">
      <h3>Métricas</h3>
      <ul>
        {Object.entries(metrics).map(([key, value]) => (
          <li key={key}>{key}: {value}</li>
        ))}
      </ul>
    </div>
  );
}

export default MetricsCard;
