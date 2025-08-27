import Grid from '@mui/material/Unstable_Grid2';
import WidgetCard from './WidgetCard';

const widgets = [
  { titulo: 'Conexões Ativas', conteudo: '45' },
  { titulo: 'Requests/hora', conteudo: '1.247' },
  { titulo: 'Uptime', conteudo: '99,8%' },
  { titulo: 'Taxa de Erro', conteudo: '2,00%' },
];

export default function WidgetGrid({ filters }: { filters: Record<string, string | undefined> }) {
  return (
    <Grid container columns={12} spacing={2}>
      {widgets.map((widget, index) => (
        <Grid key={index} gridColumn="span 3">
          <WidgetCard widget={widget} />
        </Grid>
      ))}
    </Grid>
  );
}
