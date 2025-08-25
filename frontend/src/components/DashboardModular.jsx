// src/components/DashboardModular.jsx
import React, { useState, useEffect } from "react";
import GridLayout from "react-grid-layout";
import { Box, Paper, Typography, useTheme } from "@mui/material";
import "react-grid-layout/css/styles.css";
import "react-resizable/css/styles.css";

const layoutDefault = [
  { i: "conexoes", x: 0, y: 0, w: 2, h: 2 },
  { i: "requests", x: 2, y: 0, w: 2, h: 2 },
  { i: "uptime", x: 4, y: 0, w: 2, h: 2 },
  { i: "erros", x: 0, y: 2, w: 2, h: 2 },
];

export default function DashboardModular() {
  const theme = useTheme();
  const [layout, setLayout] = useState(layoutDefault);
  const [cards, setCards] = useState([]);

  useEffect(() => {
    const savedLayout = localStorage.getItem("layout");
    if (savedLayout) {
      setLayout(JSON.parse(savedLayout));
    }

    // Mock de dados — depois pode vir de API
    const mockData = [
      { key: "conexoes", label: "Conexões Ativas", value: "45" },
      { key: "requests", label: "Requests/hora", value: "1.247" },
      { key: "uptime", label: "Uptime", value: "99,8%" },
      { key: "erros", label: "Taxa de Erro", value: "2,00%" },
    ];
    setCards(mockData);
  }, []);

  const saveLayout = (newLayout) => {
    localStorage.setItem("layout", JSON.stringify(newLayout));
    setLayout(newLayout);
  };

  return (
    <GridLayout
      className="layout"
      layout={layout}
      cols={6}
      rowHeight={100}
      width={1200}
      onLayoutChange={saveLayout}
      draggableHandle=".drag-handle"
    >
      {cards.map(({ key, label, value }) => (
        <Paper
          key={key}
          sx={{
            bgcolor: theme.palette.background.paper,
            color: theme.palette.text.primary,
            p: 2,
            borderRadius: 2,
            boxShadow: theme.shadows[3],
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
            cursor: "grab",
            transition: "transform 0.2s",
            "&:hover": { transform: "translateY(-4px)" },
          }}
        >
          <Box className="drag-handle" sx={{ width: "100%", textAlign: "center" }}>
            <Typography variant="subtitle2" color="textSecondary">
              {label}
            </Typography>
            <Typography variant="h5" color="primary">
              {value}
            </Typography>
          </Box>
        </Paper>
      ))}
    </GridLayout>
  );
}
