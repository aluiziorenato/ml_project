import React from "react";
import { Grid, Card, Typography } from "@mui/material";

const GridMuiTest: React.FC = () => {
  return (
    <Grid container spacing={2}>
      <Grid item xs={12} md={6}>
        <Card sx={{ p: 2 }}>
          <Typography variant="h6">Grid MUI Test 1</Typography>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card sx={{ p: 2 }}>
          <Typography variant="h6">Grid MUI Test 2</Typography>
        </Card>
      </Grid>
    </Grid>
  );
};

export default GridMuiTest;
