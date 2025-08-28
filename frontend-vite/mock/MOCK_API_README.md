# Endpoints Mockados do Dashboard

Este projeto utiliza o plugin `vite-plugin-mock` para simular respostas de backend durante o desenvolvimento do frontend.

## Rotas disponíveis

### GET `/api/dashboard/metrics`
Retorna dados para o gráfico do dashboard.

**Exemplo de resposta:**
```json
[
  { "name": "Jan", "uv": 400, "pv": 2400, "amt": 2400 },
  { "name": "Feb", "uv": 300, "pv": 1398, "amt": 2210 },
  { "name": "Mar", "uv": 200, "pv": 9800, "amt": 2290 },
  { "name": "Apr", "uv": 278, "pv": 3908, "amt": 2000 }
]
```

### GET `/api/dashboard/table?search=...&minValue=...&maxValue=...`
Retorna dados para a tabela do dashboard, filtrando por nome e valores.

**Exemplo de resposta:**
```json
[
  { "id": 1, "name": "Produto A", "value": 100 },
  { "id": 2, "name": "Produto B", "value": 200 }
]
```

## Como ativar os mocks
- Basta rodar `npm run dev` no diretório `frontend-vite`.
- O Vite irá ativar automaticamente os mocks definidos em `frontend-vite/mock/dashboard.mock.ts`.

## Integração futura
- Para trocar para backend real, basta alterar as URLs nos serviços em `src/services/dashboardService.js`.
- Os componentes já estão prontos para consumir dados reais sem necessidade de refatoração.

---
Dúvidas ou sugestões? Edite este arquivo ou consulte o plugin [vite-plugin-mock](https://github.com/vitejs/vite-plugin-mock).
