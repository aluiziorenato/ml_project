import React from "react";
import {
  Paper,
  Typography,
  useTheme,
  Box,
  Fade,
  Container,
} from "@mui/material";
import Grid from "@mui/material/Grid"; // Grid v2

export default function DashboardModular() {
  const theme = useTheme();

  const cards = [
    { title: "Conexões Ativas", value: "45" },
    { title: "Requests/hora", value: "1.247" },
    { title: "Uptime", value: "99,8%" },
    { title: "Taxa de Erro", value: "2,00%" },
  ];

  const produtosCards = [
    {
      title: "Produtos Mais Visitados",
      items: ["Smartphone XYZ", "Fone de Ouvido ABC", "Smartwatch DEF"],
    },
    {
      title: "Produtos Mais Vendidos",
      items: ["Notebook Ultra", "Teclado Gamer", "Monitor 4K"],
    },
  ];

  return (
    <Container maxWidth="xl">
      <Box py={4}>
        <Typography variant="h5" gutterBottom textAlign="center">
          Visão Geral
        </Typography>

        <Grid container spacing={4} justifyContent="center">
          {cards.map(({ title, value }) => (
            <Grid key={title} size={{ xs: 12, sm: 6, md: 3 }}>
              <Fade in timeout={500}>
                <Paper
                  elevation={4}
                  sx={{
                    bgcolor: theme.palette.background.paper,
                    color: theme.palette.text.primary,
                    p: 3,
                    borderRadius: 3,
                    boxShadow: theme.shadows[4],
                    textAlign: "center",
                    transition: "transform 0.2s ease-in-out",
                    "&:hover": {
                      transform: "translateY(-6px)",
                    },
                  }}
                >
                  <Typography variant="subtitle2" color="textSecondary" gutterBottom>
                    {title}
                  </Typography>
                  <Typography variant="h4" color="primary">
                    {value}
                  </Typography>
                </Paper>
              </Fade>
            </Grid>
          ))}
        </Grid>

        <Box mt={6}>
          <Grid container spacing={4}>
            {produtosCards.map(({ title, items }) => (
              <Grid key={title} size={{ xs: 12, md: 6 }}>
                <Fade in timeout={500}>
                  <Paper
                    elevation={4}
                    sx={{
                      bgcolor: theme.palette.background.paper,
                      color: theme.palette.text.primary,
                      p: 3,
                      borderRadius: 3,
                      boxShadow: theme.shadows[4],
                      transition: "transform 0.2s ease-in-out",
                      "&:hover": {
                        transform: "translateY(-6px)",
                      },
                    }}
                  >
                    <Typography variant="h6" gutterBottom>
                      {title}
                    </Typography>
                    {items.map((item, idx) => (
                      <Typography key={idx} variant="body2">
                        {idx + 1}. {item}
                      </Typography>
                    ))}
                  </Paper>
                </Fade>
              </Grid>
            ))}
          </Grid>
        </Box>
      </Box>
    </Container>
  );
}
