import React from 'react';

function ServiceStatus({ status }) {
  return (
    <div className="service-status">
      <h3>Status dos Serviços</h3>
      <ul>
        {Object.entries(status).map(([service, state]) => (
          <li key={service}>{service}: {state}</li>
        ))}
      </ul>
    </div>
  );
}

export default ServiceStatus;
