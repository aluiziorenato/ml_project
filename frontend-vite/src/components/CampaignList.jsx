import React from 'react';

function CampaignList({ campaigns, onSelectCampaign }) {
  return (
    <div>
      <h2>Campanhas</h2>
      <ul>
        {campaigns.map(campaign => (
          <li key={campaign.id}>
            <span>{campaign.name}</span>
            <span>Modo: {campaign.activeMode}</span>
            <button onClick={() => onSelectCampaign(campaign.id)}>Selecionar</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CampaignList;
