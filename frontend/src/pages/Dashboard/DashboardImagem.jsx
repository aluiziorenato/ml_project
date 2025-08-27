import React from "react";
import { Box, Typography, Paper } from "@mui/material";

export default function DashboardImagem() {
  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>Ideia de Dashboard</Typography>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <img src={require("../../dashboard-ideia.png")} alt="Dashboard Ideia" style={{ maxWidth: "100%", height: "auto" }} />
      </Box>
    </Paper>
  );
}
