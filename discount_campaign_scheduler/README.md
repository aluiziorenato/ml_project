# 🎯 Discount Campaign Scheduler

**Porta: 8015**

Módulo independente para agendamento estratégico de campanhas de desconto com sugestões baseadas em IA e automação completa.

## 🎯 Funcionalidades Principais

### 📊 Sugestões Estratégicas com IA
- **Top 5 Sugestões**: Recomenda os anúncios com maior potencial para campanhas de desconto
- **Score de Potencial**: Algoritmo proprietário que analisa engajamento, histórico de vendas e tendências
- **Dados Visuais**: Cards com imagem, título, cliques recentes e botão para aplicar campanha
- **Atualização Automática**: Sugestões atualizadas a cada 6 horas com base em novos dados

### ⏰ Agendamento Automático
- **Programação por Dia/Horário**: Configure ativação/pausa automática por dia da semana e horário
- **Verificação Periódica**: Sistema verifica a cada 5 minutos os agendamentos pendentes
- **Integração ML API**: Ativa/pausa via API Mercado Libre `/seller-promotions`
- **Execução Confiável**: Controle de status e logs de execução detalhados

### 📈 Métricas e Analytics
- **Coleta Automática**: Cliques, impressões, conversões, taxa de conversão
- **Histórico Detalhado**: Dados armazenados para análise de tendências
- **Performance Index**: Score proprietário de performance da campanha
- **Dashboard Integrado**: Visualização completa de métricas em tempo real

### 🔮 Previsão de Performance
- **Algoritmo Preditivo**: Machine Learning baseado em histórico de 90 dias
- **Score de Confiança**: Indica precisão da previsão (0-1)
- **Comparação Real vs Previsto**: Análise de acurácia das previsões
- **Modelos Adaptativos**: Melhora contínua com novos dados

### 🔐 Autenticação e Segurança
- **OAuth2 Mercado Libre**: Integração completa com sistema de autenticação ML
- **Acesso Restrito**: Todas operações limitadas ao vendedor autenticado
- **Tokens Seguros**: Renovação automática e gerenciamento seguro de tokens

## 📋 Endpoints da API

### 🎯 Campanhas de Desconto
```
POST   /api/campaigns/                    # Criar campanha
GET    /api/campaigns/                    # Listar campanhas
GET    /api/campaigns/{id}                # Obter campanha
PUT    /api/campaigns/{id}                # Atualizar campanha
DELETE /api/campaigns/{id}                # Deletar campanha
```

### ⏰ Agendamento
```
POST   /api/campaigns/{id}/schedules      # Criar agendamento
GET    /api/campaigns/{id}/schedules      # Listar agendamentos
PUT    /api/campaigns/{id}/schedules/{id} # Atualizar agendamento
DELETE /api/campaigns/{id}/schedules/{id} # Deletar agendamento
```

### 📊 Métricas
```
GET    /api/campaigns/{id}/metrics        # Métricas da campanha
POST   /api/campaigns/{id}/metrics/collect # Coletar métricas manualmente
```

### 🔮 Previsões
```
GET    /api/campaigns/{id}/prediction     # Obter previsão
GET    /api/campaigns/{id}/prediction/comparison # Comparar previsões
```

### 💡 Sugestões Estratégicas
```
GET    /api/suggestions/                  # Obter sugestões
POST   /api/suggestions/refresh           # Atualizar sugestões
GET    /api/suggestions/stored            # Sugestões armazenadas
POST   /api/suggestions/{item_id}/apply-campaign # Aplicar campanha
GET    /api/suggestions/analytics         # Analytics das sugestões
```

### 📊 Dashboard e Analytics
```
GET    /api/dashboard/overview            # Visão geral do dashboard
GET    /api/dashboard/performance-trends  # Tendências de performance
GET    /api/dashboard/schedule-analysis   # Análise de agendamentos
POST   /api/dashboard/trigger-schedule-check # Verificar agendamentos
POST   /api/dashboard/collect-all-metrics # Coletar todas as métricas
```

### 🏥 Health Checks
```
GET    /                                  # Informações do serviço
GET    /health                           # Health check
GET    /api/health                       # Health check da API
GET    /ui                               # Interface web
```

## 🗄️ Modelos de Dados

### DiscountCampaign
```python
{
    "id": int,
    "seller_id": str,
    "item_id": str,
    "campaign_name": str,
    "discount_percentage": float,
    "status": "draft|active|paused|scheduled|expired",
    "start_date": datetime,
    "end_date": datetime,
    "total_clicks": int,
    "total_impressions": int,
    "total_conversions": int,
    "total_sales_amount": float
}
```

### CampaignSchedule
```python
{
    "id": int,
    "campaign_id": int,
    "day_of_week": "monday|tuesday|...|sunday",
    "start_time": time,
    "end_time": time,
    "action": "activate|pause",
    "status": "pending|executed|failed",
    "last_executed": datetime,
    "next_execution": datetime
}
```

### ItemSuggestion
```python
{
    "item_id": str,
    "title": str,
    "image_url": str,
    "current_price": float,
    "recent_clicks": int,
    "potential_score": float,
    "engagement_trend": float
}
```

## 🧮 Algoritmo de Sugestões

O sistema utiliza um algoritmo proprietário que combina múltiplos fatores:

### Fatores de Score (Pesos)
- **Engajamento** (30%): Cliques e visitas recentes
- **Velocidade de Vendas** (25%): Quantidade vendida vs estoque
- **Atratividade de Preço** (15%): Faixa de preço ideal para descontos
- **Disponibilidade de Estoque** (15%): Quantidade disponível
- **Categoria** (10%): Performance histórica da categoria
- **Condição do Item** (5%): Novo vs usado

### Critérios Mínimos
- Score de potencial ≥ 0.5
- Estoque disponível > 0
- Preço > R$ 0

## 🔄 Tarefas Automáticas (Celery)

### Verificação de Agendamentos
- **Frequência**: A cada 5 minutos
- **Função**: Verifica e executa agendamentos pendentes
- **Ações**: Ativa/pausa campanhas via ML API

### Coleta de Métricas
- **Frequência**: A cada hora
- **Função**: Coleta métricas de todas as campanhas ativas
- **Dados**: Cliques, impressões, conversões, vendas

### Atualização de Sugestões
- **Frequência**: Diariamente às 6h
- **Função**: Gera novas sugestões para todos os vendedores
- **Processo**: Análise de engajamento e cálculo de scores

### Limpeza de Dados
- **Frequência**: Semanalmente (segunda-feira às 2h)
- **Função**: Remove dados antigos
- **Retenção**: Métricas (90 dias), Sugestões (30 dias), Previsões (60 dias)

## 🎨 Interface Web

### Dashboard Principal
- **Métricas de Resumo**: Campanhas ativas, cliques, conversões, vendas
- **Sugestões Estratégicas**: Top 5 anúncios recomendados
- **Campanhas Ativas**: Lista lateral com miniatura e métricas
- **Agendamento Visual**: Configuração intuitiva de horários

### Recursos da Interface
- **Responsiva**: Adapta-se a diferentes tamanhos de tela
- **Tempo Real**: Atualização automática de dados
- **Interativa**: Aplicação direta de campanhas nas sugestões
- **Visual**: Gráficos e indicadores de performance

## 🔧 Configuração

### Variáveis de Ambiente
```bash
DATABASE_URL=postgresql://usuario:senha@db:5432/nome_do_banco
REDIS_URL=redis://redis:6379/15
BACKEND_URL=http://backend:8000
ML_API_URL=https://api.mercadolibre.com
ML_CLIENT_ID=seu_client_id
ML_CLIENT_SECRET=seu_client_secret
SECRET_KEY=sua_chave_secreta
SCHEDULE_CHECK_INTERVAL_MINUTES=5
METRICS_COLLECTION_INTERVAL_HOURS=1
```

### Docker Compose
```yaml
discount_campaign_scheduler:
  build: ./discount_campaign_scheduler
  ports:
    - "8015:8015"
  environment:
    - DATABASE_URL=postgresql://usuario:senha@db:5432/nome_do_banco
    - REDIS_URL=redis://redis:6379/15
  depends_on:
    - db
    - redis
    - backend
```

## 🧪 Testes

### Executar Testes
```bash
cd discount_campaign_scheduler
pip install -r requirements.txt
python -m pytest tests/ -v
```

### Cobertura de Testes
- **Modelos**: Validação de schemas e relacionamentos
- **Serviços**: Lógica de negócio e integração ML API
- **API**: Endpoints e autenticação
- **Health Checks**: Verificação de saúde do serviço

## 📊 Integração Grafana

### Métricas Exportadas
- **Campanhas por Status**: Gauge das campanhas ativas/pausadas
- **Performance Diária**: Time series de cliques/conversões
- **Score de Engajamento**: Distribuição dos scores
- **Execução de Agendamentos**: Success rate dos agendamentos

### Alertas Configurados
- **Campanhas com Baixa Performance**: Taxa de conversão < 1%
- **Falhas de Agendamento**: > 5% de execuções falharam
- **Sugestões Desatualizadas**: Última atualização > 12h

## 🔮 Roadmap

- [ ] **Machine Learning Avançado**: Modelos TensorFlow para previsões
- [ ] **A/B Testing**: Comparação automática de campanhas
- [ ] **Notificações Push**: Alertas em tempo real
- [ ] **API Rate Limiting**: Controle de taxa de requests
- [ ] **Cache Inteligente**: Redis para otimização de performance
- [ ] **Multi-vendedor**: Suporte a múltiplos vendedores por conta

---

## 📝 Observações Importantes

- **Independente**: Módulo completamente separado do sistema de ads
- **Sem Sugestão de Preços**: Foca apenas em identificar potencial
- **OAuth2 Obrigatório**: Todas operações requerem autenticação ML
- **API-First**: Design orientado para integração
- **Escalável**: Preparado para alto volume de transações

**Desenvolvido para Mercado Libre** 🇧🇷