import React from "react";
import { Card, Typography, List, ListItem } from "@mui/material";

const checklist = [
  "Título otimizado",
  "Meta descrição presente",
  "Imagens com alt",
  "URLs amigáveis",
];

export default function SEOVisual() {
  return (
    <Card sx={{ p: 2 }}>
      <Typography variant="h5">Checklist de SEO Visual</Typography>
      <List>
        {checklist.map((item, i) => (
          <ListItem key={i}>{item}</ListItem>
        ))}
      </List>
    </Card>
  );
}
