import React from 'react';

function AlertsFeed({ alerts }) {
  return (
    <div className="alerts-feed">
      <h3>Alertas & Recomendações</h3>
      <ul>
        {alerts.map((alert, idx) => (
          <li key={idx} className={alert.severity || ''}>
            {alert.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default AlertsFeed;
