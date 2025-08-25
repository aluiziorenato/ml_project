# Inventory Service - Mercado Libre Integration

## Overview

O **Inventory Service** oferece controle inteligente de estoque com previsão de demanda, alertas automatizados e integração com sistemas de vendas para otimização contínua do inventário.

## Funcionalidades

### 📦 Controle de Estoque
- **Monitoramento em tempo real** dos níveis de estoque
- **Atualizações automáticas** via API
- **Sincronização** com vendas
- **Histórico completo** de movimentações

### 🔮 Previsão Inteligente
- **Demanda futura** baseada em ML
- **Sazonalidade** e tendências
- **Recomendações de reposição**
- **Otimização de capital de giro**

### 🚨 Alertas e Notificações
- **Estoque baixo** configurável
- **Produtos em falta**
- **Reposição urgente**
- **Oportunidades de compra**

### 📊 Analytics Avançados
- **Giro de estoque** por produto
- **Análise ABC** automática
- **Performance por categoria**
- **ROI do inventário**

## Endpoints Disponíveis

### GET `/meli/inventory_service/health`
Health check do serviço.

### GET `/meli/inventory_service/inventory`
Lista itens do inventário.

**Parameters:**
- `user_id` (required): ID do vendedor
- `offset` (optional): Página (default: 0)
- `limit` (optional): Itens por página (default: 50)
- `low_stock` (optional): Apenas itens com estoque baixo
- `category_id` (optional): Filtro por categoria
- `status` (optional): Filtro por status (active, paused, etc.)

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "MLB123456789",
      "title": "Smartphone Samsung Galaxy",
      "available_quantity": 5,
      "sold_quantity": 245,
      "price": 899.99,
      "status": "active",
      "category_id": "MLB1055",
      "last_updated": "2024-01-15T10:30:00Z",
      "predictions": {
        "days_until_stockout": 7,
        "recommended_restock": 50,
        "demand_forecast": {
          "next_week": 12,
          "next_month": 48
        }
      }
    }
  ],
  "pagination": {
    "total": 150,
    "offset": 0,
    "limit": 50,
    "has_next": true
  },
  "metadata": {
    "low_stock_count": 8,
    "out_of_stock_count": 2,
    "low_stock_items": [...],
    "out_of_stock_items": [...]
  }
}
```

### GET `/meli/inventory_service/items/{item_id}`
Detalhes completos de um item do inventário.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "MLB123456789",
    "title": "Produto detalhado...",
    "available_quantity": 5,
    "sold_quantity": 245,
    "sales_velocity": 8.5,  // vendas por semana
    "demand_predictions": {
      "next_7_days": 12,
      "next_30_days": 48,
      "confidence": 0.87,
      "seasonal_trend": "high_season"
    },
    "restock_suggestions": {
      "recommended_quantity": 50,
      "optimal_timing": "2024-01-20",
      "expected_roi": 1.25,
      "risk_assessment": "low"
    },
    "analytics": {
      "turnover_rate": 12.5,  // vezes por ano
      "abc_classification": "A",
      "profit_margin": 0.35,
      "stockout_risk": "medium"
    }
  }
}
```

### PUT `/meli/inventory_service/items/{item_id}/stock`
Atualiza quantidade em estoque.

**Body:**
```json
{
  "new_quantity": 50,
  "reason": "restock",  // opcional
  "notes": "Reposição baseada em previsão de demanda"  // opcional
}
```

### GET `/meli/inventory_service/alerts`
Alertas de estoque para o vendedor.

**Parameters:**
- `user_id` (required): ID do vendedor
- `urgency` (optional): critical, high, medium, low

**Response:**
```json
{
  "success": true,
  "data": {
    "alerts": [
      {
        "item_id": "MLB123456789",
        "title": "Smartphone Samsung Galaxy",
        "current_stock": 2,
        "recommended_restock": 50,
        "urgency": "critical",
        "estimated_stockout_days": 2,
        "reason": "High sales velocity, low stock",
        "suggested_actions": [
          "Order 50 units immediately",
          "Increase price by 5% to slow demand",
          "Contact supplier for bulk discount"
        ]
      }
    ],
    "total_alerts": 8,
    "critical_alerts": 2,
    "summary": {
      "potential_lost_sales": 5200.00,
      "recommended_investment": 15000.00,
      "expected_roi": 1.35
    }
  }
}
```

### GET `/meli/inventory_service/analytics`
Analytics completos de inventário.

**Parameters:**
- `user_id` (required): ID do vendedor
- `date_from` (optional): Data inicial para análise
- `date_to` (optional): Data final para análise

**Response:**
```json
{
  "success": true,
  "data": {
    "overview": {
      "total_items": 150,
      "total_inventory_value": 125000.00,
      "avg_turnover_rate": 8.5,
      "inventory_health_score": 0.82
    },
    "abc_analysis": {
      "A": {"count": 30, "value_percentage": 70},
      "B": {"count": 45, "value_percentage": 20},
      "C": {"count": 75, "value_percentage": 10}
    },
    "performance": {
      "fast_moving": 25,
      "slow_moving": 40,
      "dead_stock": 5
    },
    "predictions": {
      "next_month_demand": 1250,
      "required_investment": 45000.00,
      "expected_revenue": 87500.00
    },
    "optimization_suggestions": [
      {
        "type": "reduce_dead_stock",
        "impact": "Free up R$ 2,500 in capital",
        "action": "Discount slow-moving items"
      }
    ]
  }
}
```

## Exemplos de Uso

### Python Client
```python
import httpx
from datetime import datetime, timedelta

class InventoryClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "http://localhost:8000/meli/inventory_service"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    async def get_low_stock_alerts(self, user_id: str):
        """Obtém alertas de estoque baixo"""
        params = {"user_id": user_id, "urgency": "critical"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/alerts",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def get_inventory_overview(self, user_id: str):
        """Visão geral do inventário"""
        params = {"user_id": user_id, "low_stock": "true"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/inventory",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def update_stock_bulk(self, updates: list):
        """Atualiza estoque de múltiplos itens"""
        results = []
        
        async with httpx.AsyncClient() as client:
            for item_id, new_quantity in updates:
                response = await client.put(
                    f"{self.base_url}/items/{item_id}/stock",
                    headers=self.headers,
                    json={"new_quantity": new_quantity}
                )
                results.append(response.json())
        
        return results
    
    async def generate_restock_report(self, user_id: str):
        """Gera relatório de reposição recomendada"""
        alerts = await self.get_low_stock_alerts(user_id)
        
        restock_plan = []
        total_investment = 0
        
        for alert in alerts['data']['alerts']:
            item_detail = await self.get_item_details(alert['item_id'])
            
            plan_item = {
                'item_id': alert['item_id'],
                'title': alert['title'],
                'current_stock': alert['current_stock'],
                'recommended_quantity': alert['recommended_restock'],
                'estimated_cost': item_detail['cost'] * alert['recommended_restock'],
                'urgency': alert['urgency']
            }
            
            restock_plan.append(plan_item)
            total_investment += plan_item['estimated_cost']
        
        return {
            'restock_plan': restock_plan,
            'total_investment': total_investment,
            'priority_items': [item for item in restock_plan if item['urgency'] == 'critical']
        }

# Uso
client = InventoryClient(access_token)
alerts = await client.get_low_stock_alerts(user_id)
restock_report = await client.generate_restock_report(user_id)

# Atualização em lote
updates = [
    ("MLB123", 50),
    ("MLB456", 25),
    ("MLB789", 100)
]
results = await client.update_stock_bulk(updates)
```

### JavaScript/React Hook
```javascript
import { useState, useEffect } from 'react';

const useInventoryManager = (userId, accessToken) => {
  const [inventory, setInventory] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  const baseURL = '/meli/inventory_service';
  const headers = {
    'Authorization': `Bearer ${accessToken}`
  };

  const fetchInventory = async (filters = {}) => {
    const params = new URLSearchParams({
      user_id: userId,
      ...filters
    });

    const response = await fetch(`${baseURL}/inventory?${params}`, { headers });
    const data = await response.json();
    
    if (data.success) {
      setInventory(data.data);
    }
    return data;
  };

  const fetchAlerts = async () => {
    const response = await fetch(
      `${baseURL}/alerts?user_id=${userId}`,
      { headers }
    );
    const data = await response.json();
    
    if (data.success) {
      setAlerts(data.data.alerts);
    }
    return data;
  };

  const updateStock = async (itemId, newQuantity) => {
    const response = await fetch(`${baseURL}/items/${itemId}/stock`, {
      method: 'PUT',
      headers: {
        ...headers,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ new_quantity: newQuantity })
    });
    
    const data = await response.json();
    
    if (data.success) {
      // Refresh inventory
      await fetchInventory();
    }
    
    return data;
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([
        fetchInventory(),
        fetchAlerts()
      ]);
      setLoading(false);
    };

    if (userId && accessToken) {
      loadData();
    }
  }, [userId, accessToken]);

  return {
    inventory,
    alerts,
    analytics,
    loading,
    fetchInventory,
    fetchAlerts,
    updateStock,
    // Utility functions
    getLowStockItems: () => inventory.filter(item => item.available_quantity < 10),
    getCriticalAlerts: () => alerts.filter(alert => alert.urgency === 'critical'),
    getTotalInventoryValue: () => inventory.reduce((sum, item) => 
      sum + (item.available_quantity * item.price), 0
    )
  };
};

export default useInventoryManager;
```

## Integrações

### Learning Service
**Previsão de demanda:**
- Análise de vendas históricas
- Sazonalidade e tendências
- Fatores externos (feriados, eventos)
- Padrões de comportamento do consumidor

**Contexto enviado:**
```json
{
  "task": "demand_forecast",
  "context": {
    "item_id": "MLB123456789",
    "sales_history": [...],
    "seasonal_data": {...},
    "market_trends": {...}
  }
}
```

### Optimizer AI
**Otimizações sugeridas:**
- Quantidade ideal de reposição
- Timing otimizado para compras
- Estratégias de pricing dinâmico
- Gestão de capital de giro

### Analytics Service
**Eventos automáticos:**
- `inventory_listed`: Inventário consultado
- `stock_updated`: Estoque atualizado
- `alert_generated`: Alerta gerado
- `restock_recommended`: Reposição recomendada

### ERP Integration
```python
# Configuração de integração com ERP
erp_config = {
    "system": "SAP",  # ou "Oracle", "Odoo", etc.
    "sync_frequency": "hourly",
    "webhook_url": "https://api.erp.com/webhook",
    "auth": {"api_key": "xxx"}
}
```

## Configuração

### Variáveis de Ambiente
```bash
# Serviços integrados
LEARNING_SERVICE_URL=http://localhost:8004
OPTIMIZER_AI_URL=http://localhost:8003
ANALYTICS_SERVICE_URL=http://localhost:8002

# Limites e thresholds
LOW_STOCK_THRESHOLD=10
CRITICAL_STOCK_THRESHOLD=5
STOCKOUT_ALERT_DAYS=7

# ML Settings
DEMAND_FORECAST_HORIZON=30  # dias
PREDICTION_CONFIDENCE_MIN=0.7
RESTOCK_SAFETY_FACTOR=1.2

# Performance
BATCH_UPDATE_SIZE=100
CACHE_TTL=1800  # 30 minutos
SYNC_INTERVAL=3600  # 1 hora
```

### Configuração de Alertas
```python
alert_config = {
    "channels": ["email", "webhook", "dashboard"],
    "business_hours": "08:00-18:00",
    "escalation": {
        "critical": "immediate",
        "high": "1h",
        "medium": "4h",
        "low": "24h"
    }
}
```

## Monitoramento

### KPIs Principais
- **Inventory Turnover**: Meta >8x/ano
- **Stockout Rate**: Meta <2%
- **Fill Rate**: Meta >98%
- **Forecast Accuracy**: Meta >85%
- **Capital Efficiency**: ROI >15%

### Dashboard Metrics
```python
metrics = {
    "inventory_health": 0.85,  # Score geral
    "turnover_rate": 9.2,
    "stockout_incidents": 3,  # último mês
    "forecast_accuracy": 0.87,
    "avg_days_in_stock": 42,
    "dead_stock_percentage": 0.08
}
```

### Alertas Automáticos
- Stockout iminente (< 3 dias)
- Excesso de estoque (> 90 dias)
- Queda na accuracy de previsão
- Anomalias nas vendas

## Funcionalidades Avançadas

### Automatic Reordering
```python
auto_reorder_config = {
    "enabled": True,
    "min_confidence": 0.9,
    "max_order_value": 10000.00,
    "supplier_integration": True,
    "approval_required": False  # Para pedidos < max_order_value
}
```

### Dynamic Pricing Integration
```python
# Ajuste de preços baseado em estoque
pricing_strategy = {
    "low_stock_markup": 0.05,  # +5% quando estoque baixo
    "excess_stock_discount": 0.10,  # -10% quando excesso
    "competitor_tracking": True,
    "profit_margin_protection": 0.15  # Margem mínima
}
```

### Seasonal Planning
```python
seasonal_config = {
    "black_friday": {
        "stock_multiplier": 3.0,
        "advance_days": 45
    },
    "christmas": {
        "stock_multiplier": 2.5,
        "advance_days": 60
    },
    "valentines": {
        "categories": ["gifts", "jewelry"],
        "stock_multiplier": 2.0
    }
}
```

## Troubleshooting

### Problemas Comuns

**Previsões imprecisas**
- Verificar qualidade dos dados históricos
- Ajustar parâmetros do modelo ML
- Incluir fatores externos (promoções, sazonalidade)

**Alertas frequentes**
- Revisar thresholds de estoque baixo
- Otimizar frequência de reposição
- Implementar safety stock dinâmico

**Sincronização com ERP lenta**
- Otimizar consultas SQL
- Implementar cache inteligente
- Usar processamento em batch

**ROI baixo do inventário**
- Analisar itens de baixo giro
- Implementar estratégias de liquidação
- Revisar mix de produtos

## Roadmap

### Próximas Funcionalidades
- [ ] **Supplier Integration**: Pedidos automáticos
- [ ] **Multi-warehouse**: Gestão multi-locação
- [ ] **Demand Sensing**: Previsão em tempo real
- [ ] **Sustainability Metrics**: Pegada ambiental
- [ ] **Mobile App**: Gestão mobile completa