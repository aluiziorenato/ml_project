# Questions Service - Mercado Libre Integration

## Overview

O **Questions Service** gerencia o sistema de perguntas e respostas (Q&A) do Mercado Libre com inteligência artificial, base de conhecimento e analytics avançados para otimizar o atendimento e aumentar conversões.

## Funcionalidades

### ❓ Gerenciamento de Q&A
- **Listagem inteligente** de perguntas com priorização
- **Respostas automatizadas** com IA
- **Base de conhecimento** dinâmica
- **Analytics de performance**

### 🤖 Inteligência Artificial
- **Geração automática** de respostas
- **Análise de similaridade** entre perguntas
- **Detecção de intenções** do comprador
- **Sugestões contextuais**

### 📊 Analytics e Insights
- **Taxa de resposta** e tempo médio
- **Tópicos mais perguntados**
- **Impacto nas vendas**
- **Otimizações sugeridas**

### 🔗 Integrações Avançadas
- **Optimizer AI**: Sugestões de melhorias
- **Learning Service**: Aprendizado contínuo
- **Categories Service**: Contexto por categoria
- **Analytics Service**: Métricas em tempo real

## Endpoints Disponíveis

### GET `/meli/questions_service/health`
Health check do serviço.

### GET `/meli/questions_service/questions`
Lista perguntas do vendedor.

**Parameters:**
- `user_id` (required): ID do vendedor
- `offset` (optional): Página (default: 0)
- `limit` (optional): Itens por página (default: 50)
- `status` (optional): ANSWERED, UNANSWERED
- `unanswered_only` (optional): Apenas não respondidas
- `item_id` (optional): Filtro por item específico
- `date_from` (optional): Data inicial
- `date_to` (optional): Data final

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "12345678",
      "text": "Qual o prazo de entrega para o CEP 01310-100?",
      "status": "UNANSWERED",
      "date_created": "2024-01-15T10:30:00Z",
      "from": {
        "id": "123456789",
        "nickname": "COMPRADOR123"
      },
      "item_id": "MLB123456789",
      "ai_suggestion": {
        "text": "O prazo de entrega para São Paulo é de 2-3 dias úteis.",
        "confidence": 0.92,
        "source": "ai"
      }
    }
  ],
  "pagination": {
    "total": 25,
    "offset": 0,
    "limit": 50,
    "has_next": false
  },
  "metadata": {
    "urgent_questions": [
      {
        "id": "12345678",
        "reason": "unanswered_24h"
      }
    ],
    "similar_questions": [...],
    "statistics": {
      "total": 25,
      "answered": 20,
      "unanswered": 5,
      "answer_rate": 0.8,
      "avg_response_time_hours": 6.0
    }
  }
}
```

### GET `/meli/questions_service/questions/{question_id}`
Detalhes de uma pergunta específica.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "12345678",
    "text": "Pergunta do comprador...",
    "status": "UNANSWERED",
    "item_id": "MLB123456789",
    "ai_suggestion": {
      "text": "Resposta sugerida",
      "confidence": 0.88,
      "source": "knowledge_base"
    },
    "similar_questions": [
      {
        "id": "87654321",
        "text": "Pergunta similar anterior",
        "answer": "Resposta dada anteriormente"
      }
    ]
  }
}
```

### POST `/meli/questions_service/answers`
Responde uma pergunta.

**Body:**
```json
{
  "question_id": "12345678",
  "answer": "O prazo de entrega é de 2-3 dias úteis para São Paulo."
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "ANS789",
    "question_id": "12345678",
    "text": "Resposta enviada...",
    "date_created": "2024-01-15T11:00:00Z"
  }
}
```

### GET `/meli/questions_service/items/{item_id}/questions`
Todas as perguntas de um item específico.

**Response:**
```json
{
  "success": true,
  "data": {
    "questions": [...],
    "insights": {
      "total_questions": 15,
      "common_concerns": ["shipping_concerns", "size_concerns"],
      "suggestion": "Consider adding size chart to reduce questions"
    },
    "statistics": {
      "total": 15,
      "answered": 12,
      "unanswered": 3
    }
  }
}
```

### GET `/meli/questions_service/ai_suggestions`
Sugestões automáticas de resposta.

**Parameters:**
- `question_text` (required): Texto da pergunta

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "text": "O prazo de entrega é de 2-3 dias úteis.",
        "confidence": 0.95,
        "source": "knowledge_base"
      },
      {
        "text": "Para sua região, o prazo é de 3-5 dias úteis.",
        "confidence": 0.78,
        "source": "ai"
      }
    ],
    "confidence": 0.95,
    "source": "hybrid"
  }
}
```

### GET `/meli/questions_service/analytics`
Analytics detalhados de perguntas.

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
      "total": 150,
      "answered": 135,
      "unanswered": 15,
      "answer_rate": 0.9,
      "avg_response_time_hours": 4.2,
      "topics": {
        "shipping": 45,
        "product_specs": 30,
        "warranty": 15,
        "pricing": 10
      },
      "temporal_distribution": {
        "morning": 30,
        "afternoon": 75,
        "evening": 45
      },
      "most_asked_items": [
        {
          "item_id": "MLB123",
          "questions_count": 12
        }
      ]
    },
    "optimization_suggestions": [
      {
        "type": "description_improvement",
        "suggestion": "Add size chart to reduce size-related questions",
        "impact": "high"
      }
    ],
    "learning_insights": {
      "trending_topics": ["eco-friendly", "shipping_speed"],
      "response_effectiveness": 0.87
    }
  }
}
```

## Exemplos de Uso

### Python Client
```python
import httpx

class QuestionsClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "http://localhost:8000/meli/questions_service"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    async def get_unanswered_questions(self, user_id: str):
        params = {"user_id": user_id, "unanswered_only": "true"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/questions",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def get_ai_answer_suggestions(self, question_text: str):
        params = {"question_text": question_text}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ai_suggestions",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def answer_question(self, question_id: str, answer_text: str):
        data = {
            "question_id": question_id,
            "answer": answer_text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/answers",
                headers=self.headers,
                json=data
            )
            return response.json()
    
    async def bulk_answer_with_ai(self, user_id: str):
        """Responde automaticamente perguntas com alta confiança"""
        unanswered = await self.get_unanswered_questions(user_id)
        
        for question in unanswered['data']:
            if question.get('ai_suggestion', {}).get('confidence', 0) > 0.9:
                suggestion = question['ai_suggestion']
                await self.answer_question(question['id'], suggestion['text'])
                print(f"Auto-answered question {question['id']}")

# Uso
client = QuestionsClient(access_token)
questions = await client.get_unanswered_questions(user_id)
suggestions = await client.get_ai_answer_suggestions("Qual o prazo de entrega?")
await client.bulk_answer_with_ai(user_id)  # Auto-resposta
```

### JavaScript/Frontend
```javascript
class QuestionsAPI {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = '/meli/questions_service';
  }

  async getUnansweredQuestions(userId) {
    const response = await fetch(
      `${this.baseURL}/questions?user_id=${userId}&unanswered_only=true`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }

  async getAIAnswerSuggestions(questionText) {
    const response = await fetch(
      `${this.baseURL}/ai_suggestions?question_text=${encodeURIComponent(questionText)}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }

  async answerQuestion(questionId, answerText) {
    const response = await fetch(`${this.baseURL}/answers`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question_id: questionId,
        answer: answerText
      })
    });
    return await response.json();
  }

  async getQuestionAnalytics(userId, dateFrom, dateTo) {
    const params = new URLSearchParams({
      user_id: userId,
      ...(dateFrom && { date_from: dateFrom }),
      ...(dateTo && { date_to: dateTo })
    });

    const response = await fetch(
      `${this.baseURL}/analytics?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }
}
```

## Integrações

### Learning Service
**Análise de padrões:**
- Perguntas mais comuns por categoria
- Efetividade das respostas
- Previsão de perguntas futuras
- Otimização de descrições de produtos

**Contexto enviado:**
```json
{
  "task": "generate_answer",
  "context": {
    "question": "Texto da pergunta",
    "item_id": "ID do item",
    "category": "Categoria do produto",
    "seller_history": "Histórico do vendedor"
  }
}
```

### Optimizer AI
**Sugestões de otimização:**
- Melhorias na descrição do produto
- Prevenção de perguntas recorrentes
- Otimização do tempo de resposta
- Estratégias de comunicação

### Analytics Service
**Eventos automáticos:**
- `questions_listed`: Perguntas listadas
- `question_details_viewed`: Detalhes visualizados
- `question_answered`: Pergunta respondida
- `ai_suggestion_used`: Sugestão de IA utilizada

### Base de Conhecimento
**Funcionalidades:**
- Armazenamento automático de Q&As
- Busca semântica avançada
- Matching por similaridade
- Aprendizado contínuo

## Configuração

### Variáveis de Ambiente
```bash
# Serviços integrados
LEARNING_SERVICE_URL=http://localhost:8004
OPTIMIZER_AI_URL=http://localhost:8003
ANALYTICS_SERVICE_URL=http://localhost:8002

# IA Settings
AI_CONFIDENCE_THRESHOLD=0.7
SIMILARITY_THRESHOLD=0.8
AUTO_ANSWER_THRESHOLD=0.95

# Performance
QUESTION_PROCESSING_TIMEOUT=30
BATCH_SIZE=50
CACHE_TTL=3600
```

### Base de Conhecimento
```python
# Configuração da KB
knowledge_base_config = {
    "storage": "postgresql",
    "vector_search": "enabled",
    "similarity_algorithm": "cosine",
    "min_confidence": 0.7,
    "auto_learn": True
}
```

## Monitoramento

### Métricas Importantes
- Taxa de resposta (target: >95%)
- Tempo médio de resposta (target: <4h)
- Accuracy das sugestões IA (target: >85%)
- Satisfação do comprador
- Redução de perguntas recorrentes

### Dashboard Analytics
```python
# KPIs principais
kpis = {
    "response_rate": 0.96,
    "avg_response_time": 3.2,  # horas
    "ai_accuracy": 0.87,
    "question_reduction": 0.23,  # 23% redução vs mês anterior
    "customer_satisfaction": 4.6  # /5.0
}
```

### Alertas Automáticos
- Perguntas sem resposta há >24h
- Queda na taxa de resposta
- Falhas na geração de sugestões
- Picos anômalos de perguntas

## Funcionalidades Avançadas

### Auto-Resposta Inteligente
```python
# Configuração de auto-resposta
auto_response_settings = {
    "enabled": True,
    "confidence_threshold": 0.95,
    "categories": ["shipping", "availability", "technical_specs"],
    "business_hours_only": False,
    "human_review": True  # Para perguntas complexas
}
```

### Análise Preditiva
```python
# Previsão de perguntas
predictions = {
    "likely_questions": [
        "Qual o prazo de entrega?",
        "Tem garantia?",
        "Qual o tamanho?"
    ],
    "prevention_score": 0.78,
    "suggested_description_updates": [...]
}
```

### Otimização Contínua
```python
# Feedback loop
optimization_cycle = {
    "collect_questions": True,
    "analyze_patterns": True,
    "update_descriptions": True,
    "measure_impact": True,
    "adjust_strategy": True
}
```

## Troubleshooting

### Problemas Comuns

**IA não gera sugestões**
- Verificar conectividade com Learning Service
- Conferir threshold de confiança
- Validar base de conhecimento

**Taxa de resposta baixa**
- Implementar notificações push
- Configurar auto-resposta para casos simples
- Otimizar processo de triagem

**Perguntas recorrentes**
- Analisar padrões com Analytics
- Melhorar descrições dos produtos
- Implementar FAQ automático

## Roadmap

### Próximas Funcionalidades
- [ ] **FAQ Automático**: Geração baseada em perguntas comuns
- [ ] **Chatbot Integrado**: Resposta em tempo real
- [ ] **Análise de Voz**: Para perguntas por áudio
- [ ] **Multi-idioma**: Suporte automático
- [ ] **A/B Testing**: Para otimização de respostas