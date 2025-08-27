import React from "react";
import {
  Box,
  Card,
  CardContent,
  Typography,
  CardActions,
  Button,
} from "@mui/material";
import Grid from '@mui/material/Grid'; // Grid v2

const pedidosMock = [
  { id: 1, cliente: "João Silva", status: "Em andamento", total: "R$ 320,00" },
  { id: 2, cliente: "Maria Oliveira", status: "Concluído", total: "R$ 150,00" },
  { id: 3, cliente: "Carlos Souza", status: "Cancelado", total: "R$ 0,00" },
];

export default function Pedidos() {
  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom>
        Lista de Pedidos
      </Typography>

      <Grid container columns={12} spacing={3}>
        {pedidosMock.map((pedido) => (
          <Grid key={pedido.id} gridColumn="span 4">
            <Card variant="outlined">
              <CardContent>
                <Typography variant="h6">Pedido #{pedido.id}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Cliente: {pedido.cliente}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Status: {pedido.status}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total: {pedido.total}
                </Typography>
              </CardContent>
              <CardActions>
                <Button size="small">Detalhes</Button>
                <Button size="small" color="primary">
                  Atualizar
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}
