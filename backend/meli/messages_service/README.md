# Messages Service - Mercado Libre Integration

## Overview

O **Messages Service** gerencia toda a comunicação entre vendedores e compradores no Mercado Libre, incluindo respostas automatizadas com IA, análise de sentimentos e otimização do atendimento ao cliente.

## Funcionalidades

### 💬 Gerenciamento de Mensagens
- **Listagem de mensagens** com filtros avançados
- **Detalhes completos** de conversas
- **Histórico de comunicação** entre usuários
- **Marcação de lidas/não lidas**

### 🤖 Inteligência Artificial
- **Sugestões automáticas** de respostas
- **Análise de sentimento** das mensagens
- **Detecção de urgência** automática
- **Base de conhecimento** integrada

### 📊 Analytics de Comunicação
- **Tempo médio de resposta**
- **Taxa de resposta**
- **Análise de satisfação do cliente**
- **Temas mais comuns**

### 🔗 Integrações
- **Learning Service**: Aprendizado contínuo de padrões
- **Analytics Service**: Métricas em tempo real
- **Customer Service**: Escalação automática

## Endpoints Disponíveis

### GET `/meli/messages_service/health`
Verifica o status do serviço.

### GET `/meli/messages_service/messages`
Lista mensagens do usuário.

**Parameters:**
- `user_id` (required): ID do usuário
- `offset` (optional): Página (default: 0)
- `limit` (optional): Itens por página (default: 50)
- `status` (optional): Filtro por status (read, unread)
- `unread_only` (optional): Apenas não lidas (boolean)
- `date_from` (optional): Data inicial
- `date_to` (optional): Data final

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": "MSG123456",
      "from": {
        "user_id": "USER789",
        "nickname": "comprador123"
      },
      "to": {
        "user_id": "USER456"
      },
      "text": "Olá, gostaria de saber sobre o prazo de entrega.",
      "status": "unread",
      "date_created": "2024-01-15T10:30:00Z",
      "regarding": {
        "resource": "item",
        "resource_id": "MLB123456789"
      }
    }
  ],
  "pagination": {
    "total": 45,
    "offset": 0,
    "limit": 50,
    "has_next": false
  },
  "metadata": {
    "urgent_messages": [...],
    "statistics": {
      "total": 45,
      "unread": 8,
      "read": 37,
      "avg_response_time_hours": 4.5
    }
  }
}
```

### GET `/meli/messages_service/messages/{message_id}`
Obtém detalhes de uma mensagem.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "MSG123456",
    "from": {...},
    "text": "Mensagem do cliente...",
    "status": "unread",
    "ai_suggestions": [
      {
        "text": "O prazo de entrega é de 3 a 5 dias úteis.",
        "confidence": 0.95,
        "source": "knowledge_base"
      }
    ]
  }
}
```

### POST `/meli/messages_service/messages`
Envia uma mensagem.

**Body:**
```json
{
  "recipient_id": "USER789",
  "message_text": "Obrigado pelo contato! O prazo é de 3-5 dias úteis.",
  "order_id": "ORDER123" // opcional
}
```

### PUT `/meli/messages_service/messages/{message_id}/read`
Marca mensagem como lida.

### GET `/meli/messages_service/conversations/{user_id}`
Histórico de conversa com um usuário.

### GET `/meli/messages_service/ai_suggestions`
Sugestões de resposta com IA.

**Parameters:**
- `message_content` (required): Conteúdo da mensagem

**Response:**
```json
{
  "success": true,
  "data": {
    "suggestions": [
      {
        "text": "Resposta sugerida pela IA",
        "confidence": 0.85,
        "source": "ai"
      }
    ],
    "confidence": 0.85,
    "detected_intent": "shipping_inquiry"
  }
}
```

## Exemplos de Uso

### Python Client
```python
import httpx

class MessagesClient:
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "http://localhost:8000/meli/messages_service"
        self.headers = {"Authorization": f"Bearer {access_token}"}
    
    async def list_unread_messages(self, user_id: str):
        params = {"user_id": user_id, "unread_only": "true"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/messages",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def get_ai_suggestions(self, message_content: str):
        params = {"message_content": message_content}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/ai_suggestions",
                headers=self.headers,
                params=params
            )
            return response.json()
    
    async def send_message(self, recipient_id: str, text: str):
        data = {
            "recipient_id": recipient_id,
            "message_text": text
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/messages",
                headers=self.headers,
                json=data
            )
            return response.json()

# Uso
client = MessagesClient(access_token)
unread = await client.list_unread_messages(user_id)
suggestions = await client.get_ai_suggestions("Qual o prazo de entrega?")
```

### JavaScript/Frontend
```javascript
class MessagesAPI {
  constructor(accessToken) {
    this.accessToken = accessToken;
    this.baseURL = '/meli/messages_service';
  }

  async getUnreadMessages(userId) {
    const response = await fetch(
      `${this.baseURL}/messages?user_id=${userId}&unread_only=true`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }

  async getAISuggestions(messageContent) {
    const response = await fetch(
      `${this.baseURL}/ai_suggestions?message_content=${encodeURIComponent(messageContent)}`,
      {
        headers: {
          'Authorization': `Bearer ${this.accessToken}`
        }
      }
    );
    return await response.json();
  }

  async sendMessage(recipientId, messageText) {
    const response = await fetch(`${this.baseURL}/messages`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.accessToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        recipient_id: recipientId,
        message_text: messageText
      })
    });
    return await response.json();
  }
}
```

## Integrações

### Learning Service
**Eventos para aprendizado:**
- Padrões de comunicação
- Respostas mais eficazes
- Detecção de intenções do cliente
- Análise de satisfação

**Contexto enviado:**
```json
{
  "task": "generate_response_suggestions",
  "context": {
    "message_text": "Texto da mensagem",
    "from_user": "Dados do remetente",
    "regarding": "Contexto (item, pedido, etc.)"
  }
}
```

### Analytics Service
**Eventos automáticos:**
- `messages_listed`: Mensagens listadas
- `message_details_viewed`: Detalhes visualizados
- `message_sent`: Mensagem enviada
- `message_marked_read`: Mensagem marcada como lida

### Base de Conhecimento
- **Armazenamento** de perguntas/respostas comuns
- **Busca semântica** para matching
- **Aprendizado automático** de novas respostas

## Configuração

### Variáveis de Ambiente
```bash
# Serviços integrados
ANALYTICS_SERVICE_URL=http://localhost:8002
LEARNING_SERVICE_URL=http://localhost:8004

# IA e ML
AI_CONFIDENCE_THRESHOLD=0.7
RESPONSE_SUGGESTION_LIMIT=3

# Timeouts
MESSAGE_PROCESSING_TIMEOUT=30
AI_SUGGESTION_TIMEOUT=15
```

## Monitoramento

### Métricas Importantes
- Tempo médio de resposta
- Taxa de respostas automatizadas
- Satisfação do cliente
- Volume de mensagens por hora
- Accuracy das sugestões de IA

### Alertas
- Mensagens não respondidas há mais de 24h
- Queda na satisfação do cliente
- Falhas na geração de sugestões IA

## Funcionalidades Avançadas

### Auto-Resposta Inteligente
```python
# Configuração de auto-resposta
auto_response_config = {
    "enabled": True,
    "confidence_threshold": 0.9,
    "categories": ["shipping", "product_info", "availability"],
    "business_hours_only": True
}
```

### Escalação Automática
```python
# Regras de escalação
escalation_rules = {
    "urgent_keywords": ["problema", "cancelar", "reclamação"],
    "response_time_threshold": 2,  # horas
    "negative_sentiment_threshold": 0.3
}
```

### Análise de Sentimento
```python
# Análise em tempo real
sentiment_analysis = {
    "positive": 0.7,
    "neutral": 0.2,
    "negative": 0.1,
    "confidence": 0.85
}
```

## Troubleshooting

### Problemas Comuns

**Sugestões de IA não aparecem**
- Verificar conectividade com Learning Service
- Conferir threshold de confiança
- Validar conteúdo da mensagem

**Tempo de resposta alto**
- Otimizar consultas à base de conhecimento
- Implementar cache para sugestões comuns
- Revisar timeouts dos serviços

**Mensagens não sincronizando**
- Verificar webhooks do Mercado Livre
- Conferir tokens de acesso
- Validar rate limits