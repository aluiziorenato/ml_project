import { useState, useEffect } from 'react';

const defaultLayout = [
  { id: 'conexoes', titulo: 'Conexões Ativas', conteudo: '45' },
  { id: 'requests', titulo: 'Requests/hora', conteudo: '1.247' },
  { id: 'uptime', titulo: 'Uptime', conteudo: '99,8%' },
  { id: 'erro', titulo: 'Taxa de Erro', conteudo: '2,00%' },
];

export function useWidgetLayout() {
  const [layout, setLayout] = useState<typeof defaultLayout>(defaultLayout);

  useEffect(() => {
    const saved = localStorage.getItem('widgetLayout');
    if (saved) setLayout(JSON.parse(saved));
  }, []);

  useEffect(() => {
    localStorage.setItem('widgetLayout', JSON.stringify(layout));
  }, [layout]);

  return { layout, setLayout };
}
