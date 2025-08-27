import React from "react";
import { Card, Typography, Grid } from "@mui/material";

const kpis = [
  { label: "Vendas", value: 1200 },
  { label: "ROI", value: "2.5" },
  { label: "Produtos Ativos", value: 35 },
  { label: "Alertas", value: 3 },
];

export default function Dashboard() {
  return (
    <Grid container columns={12} spacing={2}>
      {kpis.map((kpi) => (
        <Grid key={kpi.label} gridColumn="span 3">
          <Card sx={{ p: 2 }}>
            <Typography variant="h6">{kpi.label}</Typography>
            <Typography variant="h4">{kpi.value}</Typography>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}
