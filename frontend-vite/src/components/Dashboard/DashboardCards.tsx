import React, { useState, useEffect } from "react";
import { Box, Card, Typography, CircularProgress, Alert } from "@mui/material";

const mockCards = [
  { title: "Usuários", value: "1.245", subtitle: "+12 este mês" },
  { title: "Vendas", value: "R$ 32.500", subtitle: "+R$ 2.100 este mês" },
  { title: "Conversão", value: "7,2%", subtitle: "+0,3% este mês" },
  { title: "Ativos", value: "98", subtitle: "+5 este mês" },
];

const DashboardCards = () => {
  const [loading, setLoading] = useState(false); // Troque para true se for buscar dados reais
  const [error, setError] = useState<string | null>(null);
  const [cards, setCards] = useState(mockCards);

  // Exemplo de integração futura:
  // useEffect(() => {
  //   setLoading(true);
  //   fetchDashboardCards()
  //     .then(data => { setCards(data); setLoading(false); })
  //     .catch(() => { setError('Erro ao carregar cards'); setLoading(false); });
  // }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 120 }}>
        <CircularProgress />
      </Box>
    );
  }
  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return (
    <Box sx={{ display: 'flex', gap: 3, flexWrap: 'wrap' }}>
      {cards.map((card) => (
        <Box key={card.title} sx={{ flex: '1 1 220px', minWidth: 220 }}>
          <Card sx={{ p: 3, background: "#fff", boxShadow: 2 }}>
            <Typography variant="subtitle2" color="textSecondary">{card.title}</Typography>
            <Typography variant="h4" sx={{ mt: 1 }}>{card.value}</Typography>
            <Typography variant="body2" color="textSecondary">{card.subtitle}</Typography>
          </Card>
        </Box>
      ))}
    </Box>
  );
};

export default DashboardCards;
