# Orders Service - Mercado Libre Integration

## Overview

O **Orders Service** é responsável pelo gerenciamento completo de pedidos no Mercado Libre, incluindo listagem, detalhamento, atualização de status e análise de métricas de vendas.

## Funcionalidades

### 📦 Gerenciamento de Pedidos
- **Listagem de pedidos** com filtros avançados
- **Detalhes completos** de pedidos individuais  
- **Atualização de status** de pedidos
- **Busca por período** e outros critérios

### 📊 Analytics e Métricas
- **Métricas de vendas** (receita total, ticket médio)
- **Distribuição por status** dos pedidos
- **Análise de métodos de pagamento**
- **Tendências temporais**

### 🔗 Integrações
- **Analytics Service**: Coleta automática de eventos
- **Optimizer AI**: Sugestões de otimização baseadas em dados
- **Learning Service**: Insights de machine learning

## Endpoints Disponíveis

### GET `/meli/orders_service/health`
Verifica o status do serviço.

**Response:**
```json
{
  "success": true,
  "data": {
    "service": "orders_service",
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### GET `/meli/orders_service/orders`
Lista pedidos do vendedor.

**Parameters:**
- `user_id` (required): ID do vendedor
- `offset` (optional): Página (default: 0)
- `limit` (optional): Itens por página (default: 50)
- `status` (optional): Filtro por status
- `date_from` (optional): Data inicial (ISO 8601)
- `date_to` (optional): Data final (ISO 8601)

**Response:**
```json
{
  "success": true,
  "data": [...],
  "total": 150,
  "offset": 0,
  "limit": 50,
  "has_next": true
}
```

### GET `/meli/orders_service/orders/{order_id}`
Obtém detalhes de um pedido específico.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "12345",
    "status": "paid",
    "total_amount": 299.99,
    "buyer": {...},
    "items": [...],
    "payments": [...]
  }
}
```

### PUT `/meli/orders_service/orders/{order_id}/status`
Atualiza o status de um pedido.

**Body:**
```json
{
  "status": "shipped"
}
```

### GET `/meli/orders_service/analytics`
Obtém analytics detalhados dos pedidos.

**Parameters:**
- `user_id` (required): ID do vendedor
- `date_from` (optional): Data inicial
- `date_to` (optional): Data final

**Response:**
```json
{
  "success": true,
  "data": {
    "analytics": {
      "total_orders": 150,
      "total_revenue": 45000.00,
      "avg_order_value": 300.00,
      "status_distribution": {
        "paid": 120,
        "shipped": 25,
        "delivered": 5
      }
    },
    "optimization_suggestions": [...],
    "learning_insights": {...}
  }
}
```

## Exemplos de Uso

### Python Client
```python
import httpx

async def get_orders(access_token: str, user_id: str):
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://localhost:8000/meli/orders_service/orders",
            headers=headers,
            params={"user_id": user_id, "limit": 100}
        )
        return response.json()

# Buscar pedidos dos últimos 7 dias
orders = await get_orders(token, user_id)
```

### JavaScript/Frontend
```javascript
const getOrderAnalytics = async (userId, dateFrom, dateTo) => {
  const response = await fetch(
    `/meli/orders_service/analytics?user_id=${userId}&date_from=${dateFrom}&date_to=${dateTo}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );
  return await response.json();
};
```

## Integrações com Outros Serviços

### Analytics Service
Eventos automáticos enviados:
- `orders_listed`: Quando pedidos são listados
- `order_details_viewed`: Quando detalhes são visualizados
- `order_status_updated`: Quando status é atualizado

### Optimizer AI
Contexto enviado para otimização:
- Número de pedidos
- Valor médio do pedido
- Métricas de conversão

### Learning Service
Dados enviados para análise:
- Métricas históricas
- Padrões de comportamento
- Tendências temporais

## Configuração

### Variáveis de Ambiente
```bash
# URLs dos serviços integrados
ANALYTICS_SERVICE_URL=http://localhost:8002
OPTIMIZER_AI_URL=http://localhost:8003
LEARNING_SERVICE_URL=http://localhost:8004

# Configurações da API ML
ML_API_URL=https://api.mercadolibre.com
```

### Dependências
- `httpx`: Cliente HTTP assíncrono
- `python-dateutil`: Manipulação de datas

## Testes

### Executar Testes
```bash
cd backend
pytest tests/meli/test_orders_service.py -v
```

### Testes de Cobertura
```bash
pytest tests/meli/test_orders_service.py --cov=meli.orders_service
```

## Troubleshooting

### Erro 401 (Unauthorized)
- Verificar se o token de acesso está válido
- Conferir se o token possui as permissões necessárias

### Erro 429 (Rate Limit)
- Implementar backoff exponencial
- Reduzir frequência de requisições

### Timeout
- Aumentar timeout para operações grandes
- Implementar paginação adequada

## Monitoramento

### Métricas Importantes
- Taxa de sucesso das requisições
- Tempo de resposta médio
- Volume de pedidos processados
- Erros por minuto

### Logs
```bash
# Visualizar logs do serviço
tail -f logs/meli_orders_service.log
```

## Roadmap

### Próximas Funcionalidades
- [ ] Cache Redis para consultas frequentes
- [ ] Webhooks para notificações em tempo real
- [ ] Exportação de relatórios em PDF/Excel
- [ ] Integração com sistema de estoque
- [ ] Previsão de vendas com ML

### Melhorias de Performance
- [ ] Implementação de batch operations
- [ ] Otimização de consultas
- [ ] Compressão de respostas