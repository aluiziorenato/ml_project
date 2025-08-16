# 🎯 ACOS Service - Advertising Cost of Sales Automation

**Porta: 8016**

Serviço especializado para monitoramento e automação de ACOS (Advertising Cost of Sales) em campanhas de marketplace, integrado com IA para otimização inteligente.

## 📊 O que é ACOS?

**ACOS = (Gasto com Anúncios ÷ Receita de Anúncios) × 100**

- **ACOS Baixo** = Maior eficiência (gastando menos para gerar receita)
- **ACOS Alto** = Menor eficiência (gastando mais para a mesma receita)

### Exemplos:
- Gasto: R$ 100, Receita: R$ 500 → ACOS = 20% ✅ **Excelente**
- Gasto: R$ 200, Receita: R$ 500 → ACOS = 40% ⚠️ **Atenção**
- Gasto: R$ 300, Receita: R$ 500 → ACOS = 60% ❌ **Crítico**

## 🎯 Funcionalidades Principais

### 📈 Monitoramento em Tempo Real
- Cálculo automático de ACOS por campanha
- Análise de tendências (crescente, decrescente, estável)
- Alertas configuráveis por threshold
- Dashboard visual com métricas consolidadas

### 🤖 Automação Inteligente
- **Pausar Campanhas** - Automaticamente pausa campanhas com ACOS alto
- **Ajustar Lances** - Reduz/aumenta lances baseado na performance
- **Otimizar Orçamentos** - Realoca orçamento entre campanhas
- **Otimização de Palavras-chave** - Sugestões de IA para keywords
- **Alertas Inteligentes** - Notificações em tempo real

### 🧠 Integração com IA
- Sugestões automáticas baseadas em ML
- Análise preditiva de performance
- Recomendações de otimização personalizadas
- Detecção de padrões e anomalias

## 📋 Endpoints da API

### 🎯 Regras de Automação
```
POST   /api/acos/rules                   # Criar regra de automação
GET    /api/acos/rules                   # Listar regras
GET    /api/acos/rules/{id}              # Obter regra específica
PUT    /api/acos/rules/{id}              # Atualizar regra
DELETE /api/acos/rules/{id}              # Deletar regra
```

### 📊 Métricas e Análise
```
GET    /api/acos/campaigns/{id}/metrics  # Métricas ACOS da campanha
GET    /api/acos/campaigns/{id}/analysis # Análise detalhada de ACOS
```

### 🚨 Alertas
```
GET    /api/acos/alerts                  # Listar alertas ACOS
POST   /api/acos/alerts/{id}/resolve     # Resolver alerta
```

### 🤖 Automação
```
POST   /api/acos/automation/evaluate     # Executar avaliação de regras
GET    /api/acos/automation/status       # Status da automação
```

### 🏥 Monitoramento
```
GET    /api/acos/health                  # Health check do serviço
```

## 🗄️ Modelos de Dados

### ACOSRule - Regra de Automação
```python
{
    "name": "Pausar ACOS Alto",
    "description": "Pausa campanhas com ACOS > 30%",
    "threshold_type": "maximum",        # maximum, minimum
    "threshold_value": 30.0,           # Porcentagem
    "evaluation_period_hours": 24,     # Período de avaliação
    "action_type": "pause_campaign",   # Ação a executar
    "action_config": {                 # Configurações da ação
        "severity": "high"
    },
    "campaign_ids": [1, 2, 3],        # Campanhas específicas (null = todas)
    "categories": ["electronics"],     # Categorias de produtos
    "minimum_spend": 50.0             # Gasto mínimo para trigger
}
```

### ACOSAlert - Alerta
```python
{
    "campaign_id": 123,
    "alert_type": "acos_threshold_exceeded",
    "severity": "high",               # low, medium, high, critical
    "title": "ACOS Alto Detectado",
    "message": "ACOS da campanha excedeu 30%",
    "current_acos": 35.5,
    "threshold_acos": 30.0,
    "recommended_actions": [
        "Revisar performance de keywords",
        "Considerar ajuste de lances"
    ]
}
```

## 🧮 Tipos de Ações Automáticas

### 1. 🛑 Pausar Campanha
- **Quando**: ACOS excede threshold crítico
- **Ação**: Pausa automaticamente a campanha
- **Configuração**: Threshold personalizado

### 2. 💰 Ajustar Lances
- **Quando**: ACOS fora do range ideal
- **Ação**: Reduz/aumenta lances automaticamente
- **Configuração**: Porcentagem ou valor absoluto

### 3. 📊 Ajustar Orçamento
- **Quando**: Performance abaixo/acima do esperado
- **Ação**: Realoca orçamento diário
- **Configuração**: Limites mínimo e máximo

### 4. 🔧 Otimizar Keywords
- **Quando**: ACOS alto por keywords específicas
- **Ação**: Sugestões de IA para otimização
- **Configuração**: Integração com módulos de IA

### 5. 🔔 Enviar Alerta
- **Quando**: Qualquer threshold atingido
- **Ação**: Notifica equipe responsável
- **Configuração**: Severidade e canais de notificação

## 🎨 Interface Frontend

### ACOSCard - Componente de Métricas
```jsx
<ACOSCard
  campaignId={123}
  className="max-w-md"
/>
```

**Exibe:**
- ACOS atual com status visual
- Tendência (crescente/decrescente)
- Gasto e receita do período
- Recomendações de IA
- Status das regras de automação

### ACOSManagement - Página de Gerenciamento
- Dashboard com métricas consolidadas
- Lista de regras de automação
- Alertas ativos e resolvidos
- Configuração de novas regras
- Monitoramento por campanha

## 🔧 Configuração

### Variáveis de Ambiente
```bash
# Servidor
PORT=8016
HOST=0.0.0.0

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/15

# Integração
CAMPAIGN_SERVICE_URL=http://localhost:8014
AI_SERVICE_URL=http://localhost:8005

# ACOS Settings
DEFAULT_ACOS_THRESHOLD=25.0
MAX_EVALUATION_PERIOD_HOURS=168
MIN_SPEND_THRESHOLD=10.0
```

### Docker
```bash
# Build
docker build -t acos-service .

# Run
docker run -p 8016:8016 acos-service

# Docker Compose
docker-compose up acos_service
```

## 🧪 Testes

### Testes Básicos
```bash
# Executar testes
cd acos_service
python -m pytest tests/ -v

# Teste manual de cálculo ACOS
python3 -c "
cost, revenue = 100, 500
acos = (cost / revenue) * 100
print(f'ACOS: {acos}%')  # Deve ser 20%
"
```

### Endpoints de Teste
```bash
# Health check
curl http://localhost:8016/api/acos/health

# Listar regras (requer auth)
curl -H "Authorization: Bearer token" \
     http://localhost:8016/api/acos/rules

# Métricas de campanha
curl -H "Authorization: Bearer token" \
     http://localhost:8016/api/acos/campaigns/123/metrics
```

## 📊 Integração com IA

### Módulos Utilizados
- **AI Predictive** (porta 8005) - Predições e análises
- **Campaign Automation** (porta 8014) - Gestão de campanhas
- **ROI Prediction** (porta 8013) - Análise de ROI correlacionado

### Fluxo de Integração
1. **Coleta de Dados** - Métricas das campanhas
2. **Análise de IA** - Processamento com módulos ML
3. **Geração de Insights** - Recomendações automáticas
4. **Execução de Ações** - Automação baseada em regras
5. **Monitoramento** - Acompanhamento de resultados

## 🔮 Roadmap

- [ ] **Machine Learning Avançado** - Modelos preditivos para ACOS
- [ ] **Otimização Multi-objetivo** - Balance entre ACOS, ROI e volume
- [ ] **Integração Mercado Livre** - API nativa da plataforma
- [ ] **Alertas em Tempo Real** - Notificações push e email
- [ ] **Dashboard Avançado** - Visualizações interativas
- [ ] **Exportação de Relatórios** - PDF e Excel com análises

## 📝 Observações Importantes

- **Integrado**: Funciona com serviços existentes de campanha e IA
- **Escalável**: Preparado para alto volume de campanhas
- **Configurável**: Regras flexíveis e personalizáveis
- **Monitoramento**: Métricas detalhadas e alertas inteligentes
- **Automação**: Ações baseadas em IA e regras de negócio

**Desenvolvido para Marketplace Automation** 🇧🇷