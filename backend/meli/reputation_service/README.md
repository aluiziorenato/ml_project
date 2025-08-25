# Reputation Service - Mercado Libre Integration

## Overview

O **Reputation Service** monitora e otimiza a reputação do vendedor no Mercado Libre através de análise inteligente de avaliações, insights comportamentais e sugestões automatizadas para melhorias contínuas.

## Funcionalidades

### ⭐ Monitoramento de Reputação
- **Score em tempo real** de reputação
- **Análise de avaliações** e comentários
- **Trending de performance**
- **Comparação com concorrentes**

### 📊 Analytics Avançados
- **Análise de sentimentos** das avaliações
- **Identificação de padrões** problemáticos
- **Métricas de satisfação** do cliente
- **Impacto nas vendas**

### 🚨 Alertas Inteligentes
- **Queda na reputação**
- **Avaliações negativas**
- **Problemas recorrentes**
- **Oportunidades de melhoria**

### 🎯 Otimização Automática
- **Sugestões de melhorias**
- **Planos de ação** personalizados
- **Benchmarking** competitivo
- **ROI de reputação**

## Endpoints Disponíveis

### GET `/meli/reputation_service/health`
Health check do serviço.

### GET `/meli/reputation_service/reputation/{user_id}`
Dados completos de reputação do vendedor.

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "123456789",
    "level_id": 5,
    "power_seller_status": "platinum",
    "reputation_score": 4.8,
    "transactions": {
      "total": 1250,
      "completed": 1235,
      "canceled": 15
    },
    "ratings": {
      "positive": 1180,
      "neutral": 25,
      "negative": 30
    },
    "metrics": {
      "communication": 4.9,
      "shipping_time": 4.7,
      "description_accuracy": 4.8,
      "packaging": 4.6
    },
    "trends": {
      "last_30_days": {
        "avg_rating": 4.8,
        "change": +0.1
      },
      "last_90_days": {
        "avg_rating": 4.7,
        "change": +0.2
      }
    },
    "insights": {
      "strengths": ["Fast shipping", "Good communication"],
      "improvement_areas": ["Packaging", "Product photos"],
      "risk_factors": ["Recent negative reviews about packaging"],
      "opportunities": ["Expand to premium products"]
    },
    "improvement_suggestions": [
      {
        "type": "packaging_improvement",
        "suggestion": "Invest in better packaging materials",
        "impact": "Potential +0.2 rating increase",
        "priority": "high",
        "estimated_cost": 150.00,
        "expected_roi": 3.5
      }
    ]
  }
}
```

### GET `/meli/reputation_service/reviews`
Lista avaliações do vendedor.

**Parameters:**
- `user_id` (required): ID do vendedor
- `rating` (optional): Filtro por rating (1-5)
- `date_from` (optional): Data inicial
- `date_to` (optional): Data final
- `sentiment` (optional): positive, neutral, negative

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "REV123456",
      "rating": 5,
      "review_text": "Excelente vendedor, produto chegou rapidamente e bem embalado!",
      "date_created": "2024-01-15T10:30:00Z",
      "reviewer": {
        "id": "USER789",
        "nickname": "comprador123"
      },
      "item_id": "MLB123456789",
      "sentiment_analysis": {
        "sentiment": "positive",
        "confidence": 0.95,
        "key_aspects": {
          "shipping": "positive",
          "packaging": "positive",
          "communication": "positive"
        }
      },
      "response_suggestion": {
        "text": "Muito obrigado pela avaliação! Ficamos felizes que tenha gostado.",
        "confidence": 0.88
      }
    }
  ],
  "pagination": {
    "total": 1235,
    "offset": 0,
    "limit": 50,
    "has_next": true
  },
  "metadata": {
    "avg_rating": 4.8,
    "sentiment_distribution": {
      "positive": 0.85,
      "neutral": 0.10,
      "negative": 0.05
    },
    "common_topics": [
      {"topic": "shipping", "frequency": 245, "avg_sentiment": 0.8},
      {"topic": "packaging", "frequency": 189, "avg_sentiment": 0.6},
      {"topic": "communication", "frequency": 156, "avg_sentiment": 0.9}
    ]
  }
}
```

### GET `/meli/reputation_service/analytics`
Analytics detalhados de reputação.

**Parameters:**
- `user_id` (required): ID do vendedor
- `date_from` (optional): Data inicial
- `date_to` (optional): Data final
- `compare_period` (optional): Período de comparação

**Response:**
```json
{
  "success": true,
  "data": {
    "analytics": {
      "overview": {
        "current_score": 4.8,
        "previous_score": 4.6,
        "improvement": 0.2,
        "trend": "improving",
        "percentile_ranking": 85
      },
      "detailed_metrics": {
        "communication": {
          "score": 4.9,
          "trend": "stable",
          "benchmark": 4.5
        },
        "shipping": {
          "score": 4.7,
          "trend": "improving",
          "benchmark": 4.4
        },
        "description_accuracy": {
          "score": 4.8,
          "trend": "stable",
          "benchmark": 4.6
        },
        "packaging": {
          "score": 4.2,
          "trend": "declining",
          "benchmark": 4.5,
          "action_required": true
        }
      },
      "sentiment_analysis": {
        "overall_sentiment": 0.82,
        "positive_reviews": 85.2,
        "neutral_reviews": 9.8,
        "negative_reviews": 5.0,
        "sentiment_trends": {
          "improving_topics": ["communication", "shipping_speed"],
          "declining_topics": ["packaging_quality"],
          "stable_topics": ["product_quality", "price_value"]
        }
      },
      "competitive_analysis": {
        "category_average": 4.3,
        "position_in_category": "top_15_percent",
        "similar_sellers": [
          {
            "seller_id": "SELLER456",
            "score": 4.6,
            "relation": "below"
          }
        ]
      },
      "impact_analysis": {
        "reputation_conversion_correlation": 0.76,
        "estimated_lost_sales": 2150.00,
        "potential_revenue_increase": 8500.00
      }
    },
    "optimization_suggestions": [
      {
        "category": "packaging",
        "priority": "high",
        "suggestion": "Upgrade packaging materials and add protective padding",
        "expected_impact": "+0.3 rating points",
        "implementation_cost": 200.00,
        "expected_roi": 4.2,
        "timeline": "2-4 weeks"
      },
      {
        "category": "response_time",
        "priority": "medium",
        "suggestion": "Implement automated response templates for common questions",
        "expected_impact": "+0.1 rating points",
        "implementation_cost": 50.00,
        "expected_roi": 8.5,
        "timeline": "1 week"
      }
    ],
    "learning_insights": {
      "customer_behavior": {
        "review_patterns": "Customers tend to review within 7 days of delivery",
        "satisfaction_drivers": ["Fast shipping", "Good communication", "Product quality"],
        "dissatisfaction_causes": ["Poor packaging", "Delayed shipping", "Inaccurate descriptions"]
      },
      "predictive_analysis": {
        "reputation_forecast": {
          "next_month": 4.85,
          "confidence": 0.82
        },
        "risk_assessment": "Low risk of reputation decline",
        "growth_opportunities": ["Premium product segment", "Cross-selling"]
      }
    }
  }
}
```

### POST `/meli/reputation_service/respond_review`
Responde a uma avaliação (funcionalidade futura).

**Body:**
```json
{
  "review_id": "REV123456",
  "response_text": "Obrigado pela avaliação! Trabalhamos continuamente para melhorar."
}
```

### GET `/meli/reputation_service/competitors`
Análise competitiva (funcionalidade futura).

**Parameters:**
- `user_id` (required): ID do vendedor
- `category_id` (optional): Categoria para comparação

## Exemplos de Uso

### Python Client
```python
import httpx
from datetime import datetime, timedelta

class ReputationClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "http://localhost:8000/meli/reputation_service"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    async def get_reputation_overview(self, user_id: str):
        """Visão geral da reputação"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reputation/{user_id}",
                headers=self.headers
            )
            return response.json()
    
    async def analyze_negative_reviews(self, user_id: str, days: int = 30):
        """Analisa avaliações negativas recentes"""
        date_from = (datetime.now() - timedelta(days=days)).isoformat()
        
        params = {
            "user_id": user_id,
            "rating": "1,2",  # Ratings 1 e 2
            "date_from": date_from
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/reviews",
                headers=self.headers,
                params=params
            )
            
            data = response.json()
            if data['success']:
                negative_reviews = data['data']
                
                # Análise de padrões
                issues = {}
                for review in negative_reviews:
                    sentiment = review.get('sentiment_analysis', {})
                    aspects = sentiment.get('key_aspects', {})
                    
                    for aspect, sentiment_score in aspects.items():
                        if sentiment_score == 'negative':
                            issues[aspect] = issues.get(aspect, 0) + 1
                
                return {
                    'total_negative': len(negative_reviews),
                    'common_issues': sorted(issues.items(), key=lambda x: x[1], reverse=True),
                    'reviews': negative_reviews
                }
            
            return None
    
    async def get_improvement_plan(self, user_id: str):
        """Gera plano de melhorias personalizado"""
        analytics = await self.get_reputation_analytics(user_id)
        
        if analytics['success']:
            suggestions = analytics['data']['optimization_suggestions']
            
            # Prioriza por ROI e impacto
            prioritized = sorted(
                suggestions, 
                key=lambda x: (x['priority'] == 'high', x['expected_roi']), 
                reverse=True
            )
            
            plan = {
                'quick_wins': [s for s in prioritized if s['timeline'] == '1 week'],
                'medium_term': [s for s in prioritized if '2-4 weeks' in s['timeline']],
                'long_term': [s for s in prioritized if 'month' in s['timeline']],
                'total_investment': sum(s['implementation_cost'] for s in suggestions),
                'expected_impact': sum(s['expected_roi'] for s in suggestions)
            }
            
            return plan
        
        return None
    
    async def monitor_reputation_alerts(self, user_id: str):
        """Monitora alertas de reputação"""
        current = await self.get_reputation_overview(user_id)
        
        if current['success']:
            data = current['data']
            alerts = []
            
            # Score baixo
            if data['reputation_score'] < 4.0:
                alerts.append({
                    'type': 'low_score',
                    'severity': 'high',
                    'message': f"Reputation score is low: {data['reputation_score']}"
                })
            
            # Tendência negativa
            if data['trends']['last_30_days']['change'] < -0.1:
                alerts.append({
                    'type': 'declining_trend',
                    'severity': 'medium',
                    'message': f"Reputation declining: {data['trends']['last_30_days']['change']}"
                })
            
            # Avaliações negativas recentes
            negative_analysis = await self.analyze_negative_reviews(user_id, 7)
            if negative_analysis and negative_analysis['total_negative'] > 3:
                alerts.append({
                    'type': 'negative_reviews',
                    'severity': 'high',
                    'message': f"{negative_analysis['total_negative']} negative reviews in last 7 days"
                })
            
            return alerts
        
        return []

# Uso
client = ReputationClient(access_token)
overview = await client.get_reputation_overview(user_id)
negative_analysis = await client.analyze_negative_reviews(user_id)
improvement_plan = await client.get_improvement_plan(user_id)
alerts = await client.monitor_reputation_alerts(user_id)
```

### React Hook para Dashboard
```javascript
import { useState, useEffect } from 'react';

const useReputationDashboard = (userId, accessToken) => {
  const [reputation, setReputation] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const baseURL = '/meli/reputation_service';
  const headers = {
    'Authorization': `Bearer ${accessToken}`
  };

  const fetchReputationData = async () => {
    try {
      const [reputationRes, analyticsRes] = await Promise.all([
        fetch(`${baseURL}/reputation/${userId}`, { headers }),
        fetch(`${baseURL}/analytics?user_id=${userId}`, { headers })
      ]);

      const reputationData = await reputationRes.json();
      const analyticsData = await analyticsRes.json();

      if (reputationData.success) setReputation(reputationData.data);
      if (analyticsData.success) setAnalytics(analyticsData.data);

      // Generate alerts
      const generatedAlerts = generateAlerts(reputationData.data, analyticsData.data);
      setAlerts(generatedAlerts);

    } catch (error) {
      console.error('Error fetching reputation data:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateAlerts = (reputation, analytics) => {
    const alerts = [];

    if (reputation?.reputation_score < 4.0) {
      alerts.push({
        type: 'warning',
        title: 'Score Baixo',
        message: `Sua reputação está em ${reputation.reputation_score}. Considere implementar melhorias.`,
        priority: 'high'
      });
    }

    if (analytics?.analytics?.detailed_metrics?.packaging?.action_required) {
      alerts.push({
        type: 'action',
        title: 'Embalagem',
        message: 'Clientes estão insatisfeitos com a embalagem. Ação necessária.',
        priority: 'medium'
      });
    }

    return alerts;
  };

  const getScoreColor = (score) => {
    if (score >= 4.5) return 'green';
    if (score >= 4.0) return 'yellow';
    return 'red';
  };

  const getScoreLabel = (score) => {
    if (score >= 4.8) return 'Excelente';
    if (score >= 4.5) return 'Muito Bom';
    if (score >= 4.0) return 'Bom';
    if (score >= 3.5) return 'Regular';
    return 'Precisa Melhorar';
  };

  useEffect(() => {
    if (userId && accessToken) {
      fetchReputationData();
    }
  }, [userId, accessToken]);

  return {
    reputation,
    analytics,
    alerts,
    loading,
    refresh: fetchReputationData,
    utils: {
      getScoreColor,
      getScoreLabel
    }
  };
};

export default useReputationDashboard;
```

## Integrações

### Learning Service
**Análise preditiva:**
- Previsão de tendências de reputação
- Identificação de fatores de risco
- Otimização de estratégias de melhoria
- Análise de comportamento do cliente

**Contexto enviado:**
```json
{
  "task": "reputation_analysis",
  "context": {
    "user_id": "123456789",
    "current_metrics": {...},
    "historical_data": [...],
    "review_sentiments": [...]
  }
}
```

### Analytics Service
**Eventos automáticos:**
- `reputation_viewed`: Dashboard acessado
- `negative_review_detected`: Avaliação negativa identificada
- `improvement_implemented`: Melhoria implementada
- `score_milestone`: Meta de score atingida

### Optimizer AI
**Otimizações sugeridas:**
- Estratégias de comunicação
- Melhorias operacionais
- Timing de ações de melhoria
- Investimentos prioritários

### Notification Service
```python
notification_config = {
    "channels": ["email", "sms", "push", "dashboard"],
    "triggers": {
        "score_drop": 0.2,  # Queda de 0.2 pontos
        "negative_reviews": 3,  # 3 avaliações negativas/semana
        "competitor_overtake": True
    }
}
```

## Configuração

### Variáveis de Ambiente
```bash
# Serviços integrados
LEARNING_SERVICE_URL=http://localhost:8004
OPTIMIZER_AI_URL=http://localhost:8003
ANALYTICS_SERVICE_URL=http://localhost:8002
NOTIFICATION_SERVICE_URL=http://localhost:8006

# Thresholds
MIN_ACCEPTABLE_SCORE=4.0
ALERT_SCORE_DROP=0.2
NEGATIVE_REVIEW_THRESHOLD=3

# ML Settings
SENTIMENT_CONFIDENCE_MIN=0.7
PREDICTION_HORIZON=30  # dias
BENCHMARK_UPDATE_FREQUENCY=7  # dias

# Monitoring
REPUTATION_CHECK_INTERVAL=3600  # 1 hora
COMPETITOR_ANALYSIS_INTERVAL=86400  # 24 horas
```

### Configuração de Alertas
```python
alert_settings = {
    "score_monitoring": {
        "enabled": True,
        "check_frequency": "hourly",
        "thresholds": {
            "critical": 3.5,
            "warning": 4.0,
            "good": 4.5
        }
    },
    "review_monitoring": {
        "enabled": True,
        "negative_review_limit": 3,
        "time_window": "7_days"
    }
}
```

## Monitoramento

### KPIs Principais
- **Reputation Score**: Meta >4.5
- **Positive Review Rate**: Meta >90%
- **Response Rate to Reviews**: Meta >80%
- **Score Improvement Rate**: Meta +0.1/mês
- **Customer Satisfaction**: Meta >4.7

### Dashboard Metrics
```python
dashboard_kpis = {
    "current_score": 4.8,
    "monthly_change": +0.15,
    "positive_rate": 0.92,
    "response_rate": 0.75,
    "competitor_ranking": "top_20_percent",
    "revenue_impact": +12.5  # % aumento estimado
}
```

### Competitive Intelligence
```python
competitor_metrics = {
    "category_average": 4.3,
    "top_performer": 4.9,
    "position": 3,  # 3º lugar na categoria
    "gap_to_leader": 0.1,
    "improvement_needed": 0.1
}
```

## Funcionalidades Avançadas

### Auto-Response to Reviews
```python
auto_response_config = {
    "enabled": True,
    "positive_reviews": {
        "enabled": True,
        "template": "Muito obrigado pela avaliação! Ficamos felizes que tenha gostado.",
        "personalization": True
    },
    "negative_reviews": {
        "enabled": False,  # Requer aprovação manual
        "escalate_to_human": True
    }
}
```

### Reputation Recovery Plan
```python
recovery_plan = {
    "triggered_when": "score < 4.0",
    "actions": [
        "immediate_customer_outreach",
        "process_improvement",
        "staff_training",
        "quality_control_enhancement"
    ],
    "timeline": "30_days",
    "success_criteria": "score > 4.2"
}
```

### Predictive Reputation Management
```python
predictive_features = {
    "reputation_forecast": True,
    "risk_early_warning": True,
    "improvement_simulation": True,
    "competitor_threat_detection": True
}
```

## Troubleshooting

### Problemas Comuns

**Score não melhora**
- Verificar implementação das sugestões
- Analisar feedback dos clientes
- Revisar processos operacionais
- Avaliar treinamento da equipe

**Muitas avaliações negativas**
- Identificar causa raiz dos problemas
- Implementar controle de qualidade
- Melhorar comunicação com clientes
- Revisar processo de fulfillment

**Dados inconsistentes**
- Verificar sincronização com ML API
- Validar algoritmos de sentiment analysis
- Conferir configuração de webhooks

## Roadmap

### Próximas Funcionalidades
- [ ] **Auto-Response**: Respostas automáticas inteligentes
- [ ] **Competitor Benchmarking**: Análise competitiva detalhada
- [ ] **Reputation Insurance**: Proteção proativa da reputação
- [ ] **Customer Journey**: Mapeamento da experiência completa
- [ ] **Voice Analytics**: Análise de feedback por voz