import { Card, CardContent, Typography, Chip, Box } from '@mui/material';

export default function ProductCard({ produto }: { produto: any }) {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">{produto.nome}</Typography>
        <Typography variant="body2">Vendas: {produto.vendas}</Typography>
        <Box mt={1} display="flex" gap={1}>
          {produto.demandaAlta && <Chip label="Alta Demanda" color="success" size="small" />}
          {produto.baixaConcorrencia && <Chip label="Baixa Concorrência" color="warning" size="small" />}
        </Box>
      </CardContent>
    </Card>
  );
}
