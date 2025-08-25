# Shipments Service - Mercado Libre Integration

## Overview

O **Shipments Service** gerencia todos os aspectos relacionados a envios no Mercado Libre, incluindo rastreamento, otimização de custos, criação de etiquetas e análise de performance logística.

## Funcionalidades

### 📦 Gerenciamento de Envios
- **Listagem de envios** com filtros avançados
- **Detalhes completos** de cada envio
- **Rastreamento em tempo real**
- **Atualização de status**

### 🏷️ Etiquetas e Labels
- **Criação automática** de etiquetas
- **Múltiplos métodos** de envio
- **Integração com transportadoras**

### 📊 Analytics de Logística
- **Custos de envio** e otimização
- **Tempo médio de entrega**
- **Distribuição por transportadora**
- **Performance por região**

### 🔗 Integrações
- **Orders Service**: Sincronização com pedidos
- **Inventory Service**: Controle de estoque
- **Optimizer AI**: Otimização de custos e rotas

## Endpoints Disponíveis

### GET `/meli/shipments_service/health`
Verifica o status do serviço.

### GET `/meli/shipments_service/shipments`
Lista envios do vendedor.

**Parameters:**
- `user_id` (required): ID do vendedor
- `offset` (optional): Página (default: 0)
- `limit` (optional): Itens por página (default: 50)
- `status` (optional): Filtro por status (pending, shipped, delivered, etc.)
- `shipping_method` (optional): Filtro por método de envio
- `date_from` (optional): Data inicial (ISO 8601)
- `date_to` (optional): Data final (ISO 8601)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "40814001056",
      "status": "shipped",
      "tracking_number": "SW123456789BR",
      "shipping_method": {
        "id": "182",
        "name": "Mercado Envios Flex"
      },
      "shipping_cost": {
        "list_cost": 15.90,
        "seller_cost": 15.90
      },
      "date_created": "2024-01-15T10:00:00Z",
      "estimated_delivery": "2024-01-18T17:00:00Z"
    }
  ],
  "total": 45,
  "offset": 0,
  "limit": 50,
  "has_next": false
}
```

### GET `/meli/shipments_service/shipments/{shipment_id}`
Obtém detalhes de um envio específico.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "40814001056",
    "status": "shipped",
    "tracking_number": "SW123456789BR",
    "order_id": "2000012345",
    "receiver_address": {
      "zip_code": "01310-100",
      "city": "São Paulo",
      "state": "SP"
    },
    "shipping_method": {...},
    "tracking_events": [...]
  }
}
```

### GET `/meli/shipments_service/shipments/{shipment_id}/tracking`
Obtém informações de rastreamento.

**Response:**
```json
{
  "success": true,
  "data": {
    "tracking_number": "SW123456789BR",
    "status": "in_transit",
    "events": [
      {
        "date": "2024-01-15T14:30:00Z",
        "description": "Objeto postado",
        "location": "São Paulo - SP"
      },
      {
        "date": "2024-01-16T09:15:00Z", 
        "description": "Objeto em trânsito",
        "location": "Centro de Distribuição"
      }
    ],
    "estimated_delivery": "2024-01-18T17:00:00Z"
  }
}
```

### PUT `/meli/shipments_service/shipments/{shipment_id}`
Atualiza status de um envio.

**Body:**
```json
{
  "status": "delivered"
}
```

### GET `/meli/shipments_service/shipping_options`
Obtém opções de envio para um item.

**Parameters:**
- `item_id` (required): ID do item
- `zip_code` (required): CEP de destino

**Response:**
```json
{
  "success": true,
  "data": {
    "options": [
      {
        "id": "182",
        "name": "Mercado Envios Flex",
        "cost": 15.90,
        "delivery_time": "3-5 dias úteis",
        "speed": "standard"
      },
      {
        "id": "100009",
        "name": "Mercado Envios Full",
        "cost": 0.00,
        "delivery_time": "1-2 dias úteis",
        "speed": "express"
      }
    ],
    "optimization_suggestions": [
      {
        "type": "cost_optimization",
        "suggestion": "Use Mercado Envios Flex para reduzir custos em 25%",
        "impact": "Economia de R$ 4.00 por envio"
      }
    ]
  }
}
```

### POST `/meli/shipments_service/labels`
Cria etiqueta de envio.

**Body:**
```json
{
  "shipment_id": "40814001056",
  "service_type": "standard",
  "dimensions": {
    "height": 10,
    "width": 20,
    "length": 30,
    "weight": 500
  }
}
```

### GET `/meli/shipments_service/analytics`
Analytics detalhados de envios.

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
      "total_shipments": 125,
      "total_shipping_cost": 1987.50,
      "avg_shipping_cost": 15.90,
      "status_distribution": {
        "pending": 5,
        "shipped": 85,
        "delivered": 35
      },
      "method_distribution": {
        "Mercado Envios Flex": 95,
        "Mercado Envios Full": 30
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

class ShipmentsClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "http://localhost:8000/meli/shipments_service"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    async def list_shipments(self, user_id: str, status: str = None):
        params = {"user_id": user_id}
        if status:
            params["status"] = status
            
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/shipments",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def track_shipment(self, shipment_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/shipments/{shipment_id}/tracking",
                headers=self.headers
            )
            return response.json()

# Uso
client = ShipmentsClient(access_token)
shipments = await client.list_shipments(user_id, status="shipped")
tracking = await client.track_shipment("40814001056")
```

### JavaScript/Frontend
```javascript
class ShipmentsAPI {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = '/meli/shipments_service';
  }

  async getShippingOptions(itemId, zipCode) {
    const response = await fetch(
      `${this.baseURL}/shipping_options?item_id=${itemId}&zip_code=${zipCode}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }

  async createShippingLabel(shipmentData) {
    const response = await fetch(`${this.baseURL}/labels`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(shipmentData)
    });
    return await response.json();
  }
}
```

### React Component
```jsx
import { useState, useEffect } from 'react';

const ShipmentTracker = ({ shipmentId }) => {
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTracking = async () => {
      try {
        const response = await fetch(
          `/meli/shipments_service/shipments/${shipmentId}/tracking`,
          {
            headers: {
              'Authorization': `Bearer ${accessToken}`
            }
          }
        );
        const data = await response.json();
        setTracking(data.data);
      } catch (error) {
        console.error('Error fetching tracking:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTracking();
  }, [shipmentId]);

  if (loading) return <div>Carregando rastreamento...</div>;

  return (
    <div className="shipment-tracker">
      <h3>Rastreamento: {tracking?.tracking_number}</h3>
      <div className="tracking-events">
        {tracking?.events?.map((event, index) => (
          <div key={index} className="tracking-event">
            <span className="date">{event.date}</span>
            <span className="description">{event.description}</span>
            <span className="location">{event.location}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
```

## Integrações

### Analytics Service
Eventos enviados automaticamente:
- `shipments_listed`: Lista de envios consultada
- `shipment_details_viewed`: Detalhes de envio visualizados
- `tracking_viewed`: Rastreamento consultado
- `shipment_status_updated`: Status atualizado
- `shipping_label_created`: Etiqueta criada

### Optimizer AI
Contextos de otimização:
- **Custo de envio**: Sugestões para reduzir custos
- **Método de envio**: Melhor opção por item/região
- **Rotas**: Otimização de rotas de entrega

### Learning Service
Dados para machine learning:
- Padrões de entrega por região
- Previsão de tempo de entrega
- Otimização de custos logísticos

## Configuração

### Variáveis de Ambiente
```bash
# URLs dos serviços
ANALYTICS_SERVICE_URL=http://localhost:8002
OPTIMIZER_AI_URL=http://localhost:8003
LEARNING_SERVICE_URL=http://localhost:8004

# Mercado Libre API
ML_API_URL=https://api.mercadolibre.com
```

## Monitoramento

### Métricas Importantes
- Taxa de entrega no prazo
- Custo médio de envio
- Volume de envios por dia
- Problemas de rastreamento

### Alertas
- Envios atrasados
- Custos acima do esperado
- Falhas na criação de etiquetas

## Troubleshooting

### Problemas Comuns

**Rastreamento não atualiza**
- Verificar se tracking_number está correto
- Confirmar integração com transportadora

**Custo de envio incorreto**
- Validar dimensões do produto
- Verificar configuração de origem

**Etiqueta não gerada**
- Conferir dados obrigatórios
- Verificar saldo em conta ML