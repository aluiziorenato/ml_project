# 📊 Dashboard e Monitoramento - Guia de Integração

Este guia explica como configurar e usar o sistema de dashboard, páginas internas e monitoramento (Grafana, Prometheus, Loki) do ML Project.

## 🎯 Visão Geral

O sistema implementa:
- **Dashboard React** com cards animados, KPIs e visualizações
- **Páginas internas** de produtos, pedidos e campanhas
- **Integração Prometheus** para coleta de métricas
- **Logging Loki** para centralização de logs
- **Dashboards Grafana** para visualização

## 🛠️ Estrutura de Arquivos

### Frontend (React)

```
frontend/src/
├── components/
│   ├── KPICard.jsx           # Cards KPI reutilizáveis com animações
│   ├── DataTable.jsx         # Tabela de dados com sorting/paginação
│   ├── AnimatedCard.jsx      # Card base com animações Framer Motion
│   └── Charts/
│       └── LineChartCard.jsx # Gráficos de linha com Recharts
├── pages/
│   ├── Dashboard.jsx         # Dashboard principal melhorado
│   ├── Products.jsx          # Página de gerenciamento de produtos
│   ├── Orders.jsx            # Página de gerenciamento de pedidos
│   └── Campaigns.jsx         # Página de campanhas publicitárias
```

### Backend (FastAPI)

```
backend/app/
├── monitoring/
│   ├── prometheus_metrics.py # Configuração e coleta de métricas
│   ├── loki_config.py        # Configuração de logging Loki
│   └── middleware.py         # Middleware automático de monitoramento
├── routers/
│   └── metrics.py            # Endpoints de métricas e health check
```

## 🚀 Configuração e Deploy

### 1. Configuração do Backend

```bash
# Instalar dependências
cd backend
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
```

Variáveis de ambiente necessárias:
```env
# Loki Configuration
LOKI_URL=http://localhost:3100

# Prometheus Configuration  
PROMETHEUS_PORT=8000

# Monitoring Security (PRODUÇÃO)
METRICS_API_KEY=your-secure-random-key-here
ENABLE_METRICS_AUTH=true
```

**⚠️ IMPORTANTE - SEGURANÇA EM PRODUÇÃO:**
- Altere `METRICS_API_KEY` para uma chave segura e única
- Mantenha `ENABLE_METRICS_AUTH=true` em produção
- Configure firewall para restringir acesso às portas de monitoramento
- Use HTTPS em produção com certificados SSL válidos

### 2. Configuração do Frontend

```bash
# Instalar dependências
cd frontend
npm install

# Build para produção
npm run build

# Desenvolvimento
npm run dev
```

### 3. Deploy com Docker Compose

```bash
# Deploy completo com monitoramento
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Verificar serviços
docker-compose ps
```

## 📊 Endpoints de Monitoramento

### Prometheus Metrics
- **URL**: `http://localhost:8000/api/metrics/prometheus`
- **Formato**: Prometheus metrics format
- **Métricas disponíveis**:
  - `http_requests_total` - Total de requests HTTP
  - `http_request_duration_seconds` - Duração de requests
  - `system_cpu_usage_percent` - Uso de CPU
  - `system_memory_usage_percent` - Uso de memória
  - `active_connections_total` - Conexões ativas
  - `campaigns_active_total` - Campanhas ativas
  - `ml_model_accuracy` - Precisão dos modelos ML

### Health Check
- **URL**: `http://localhost:8000/api/metrics/health`
- **Formato**: JSON
- **Informações**: Status do sistema, uptime, recursos

### Métricas Detalhadas do Sistema
- **URL**: `http://localhost:8000/api/metrics/system`
- **Formato**: JSON detalhado
- **Informações**: CPU, memória, disco, rede, processos

## 🔒 Configuração de Segurança

### Autenticação de Métricas
O endpoint `/api/metrics/prometheus` está protegido por autenticação Bearer token:

```bash
# Acessar métricas com autenticação
curl -H "Authorization: Bearer your-metrics-key" http://localhost:8000/api/metrics/prometheus

# Configurar Prometheus com autenticação
# Edite monitoring/prometheus.yml:
authorization:
  type: Bearer
  credentials: 'your-metrics-key'
```

### Configurações de Produção
```env
# .env para produção
METRICS_API_KEY=generate-secure-random-key-256-bits
ENABLE_METRICS_AUTH=true
SENTRY_DSN=your-sentry-dsn
LOKI_URL=https://loki.your-domain.com
```

### Rede e Firewall
- Prometheus: Porta 9090 (somente rede interna)
- Grafana: Porta 3001 (acesso restrito por IP)
- Métricas API: Porta 8000/api/metrics/* (autenticação obrigatória)

## 🚨 Alertas e Monitoramento

### Alertas Configurados
O sistema inclui alertas automáticos para:

- **Sistema**: CPU > 85%, Memória > 90%, Disco > 85%
- **API**: Taxa de erro > 5%, Tempo resposta > 2s
- **Aplicação**: Serviços offline, Baixa precisão ML
- **Segurança**: Tentativas de login falhadas
- **Infraestrutura**: Conexões excessivas, DB offline

### Configuração de Notificações
Edite `monitoring/alert_rules.yml` para personalizar alertas ou adicione webhook/email:

```yaml
# Exemplo de webhook para Slack/Discord
- alert: CriticalError
  expr: rate(application_errors_total[5m]) > 1
  annotations:
    webhook: "https://hooks.slack.com/your-webhook"
```

### 1. Acesso ao Grafana
- **URL**: `http://localhost:3001`
- **Usuário**: `admin`
- **Senha**: `admin123`

### 2. Configurar Data Sources

#### Prometheus Data Source
1. Vá em **Configuration > Data Sources**
2. Clique em **Add data source**
3. Selecione **Prometheus**
4. Configure:
   - **URL**: `http://prometheus:9090`
   - **Access**: Server (default)
5. Clique em **Save & Test**

#### Loki Data Source
1. Adicione novo data source
2. Selecione **Loki**
3. Configure:
   - **URL**: `http://loki:3100`
   - **Access**: Server (default)
4. Clique em **Save & Test**

### 3. Importar Dashboards

#### Dashboard Principal do Sistema
```json
{
  "dashboard": {
    "title": "ML Project - Sistema",
    "panels": [
      {
        "title": "Requests por Minuto",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Uso de CPU",
        "type": "singlestat", 
        "targets": [
          {
            "expr": "system_cpu_usage_percent",
            "legendFormat": "CPU %"
          }
        ]
      }
    ]
  }
}
```

#### Dashboard de Campanhas
```json
{
  "dashboard": {
    "title": "ML Project - Campanhas",
    "panels": [
      {
        "title": "Campanhas Ativas",
        "type": "singlestat",
        "targets": [
          {
            "expr": "campaigns_active_total",
            "legendFormat": "Ativas"
          }
        ]
      },
      {
        "title": "Cliques por Campanha",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(campaigns_clicks_total[5m])",
            "legendFormat": "{{campaign_id}}"
          }
        ]
      }
    ]
  }
}
```

## 📋 Configuração do Prometheus

O arquivo `monitoring/prometheus.yml` já está configurado com:

```yaml
scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/metrics/prometheus'
    scrape_interval: 10s
```

### Adicionando Novas Métricas

1. **No Backend** (`backend/app/monitoring/prometheus_metrics.py`):
```python
# Definir nova métrica
my_custom_metric = Counter('my_custom_total', 'Description of metric')

# Registrar evento
def record_custom_event():
    my_custom_metric.inc()
```

2. **No Código da Aplicação**:
```python
from app.monitoring.prometheus_metrics import record_custom_event

# Usar a métrica
record_custom_event()
```

## 📝 Configuração do Loki

### 1. Configuração Automática
O sistema já configura automaticamente o logging Loki através de `backend/app/monitoring/loki_config.py`.

### 2. Uso nos Componentes
```python
from app.monitoring.loki_config import get_structured_logger

# Criar logger para componente
logger = get_structured_logger("my_component")

# Usar logging estruturado
logger.log_request("GET", "/api/test", 200, 0.5, user_id="123")
logger.log_business_event("user_signup", {"plan": "premium"})
logger.log_error(exception, {"context": "user_data"})
```

### 3. Queries no Grafana
Exemplos de queries Loki:

```logql
# Logs de erro
{application="ml_project_backend"} |= "ERROR"

# Requests por endpoint
{application="ml_project_backend"} | json | line_format "{{.method}} {{.path}} - {{.status_code}}"

# Logs de um componente específico
{application="ml_project_backend", component="auth"}

# Performance analysis
{application="ml_project_backend"} | json | duration > 1s
```

## 🎨 Componentes Frontend

### KPICard
Usado para exibir métricas principais:

```jsx
<KPICard
  title="Total de Produtos"
  value={127}
  change="+5"
  changeType="positive"
  icon="📦"
  color="blue"
/>
```

### DataTable
Tabela de dados com funcionalidades:

```jsx
<DataTable
  title="Lista de Produtos"
  columns={columns}
  data={products}
  actions={[
    {
      label: 'Editar',
      onClick: (item) => console.log('Edit:', item),
      className: 'bg-blue-100 text-blue-700'
    }
  ]}
/>
```

## 🔍 Monitoramento e Alertas

### Métricas Recomendadas para Alertas

1. **Taxa de Erro Alta**:
   ```promql
   rate(http_requests_total{status_code=~"5.."}[5m]) > 0.05
   ```

2. **Uso de CPU Alto**:
   ```promql
   system_cpu_usage_percent > 80
   ```

3. **Uso de Memória Alto**:
   ```promql
   system_memory_usage_percent > 85
   ```

4. **Campanhas sem Conversões**:
   ```promql
   increase(campaigns_conversions_total[1h]) == 0
   ```

### Configuração de Alertas no Grafana

1. Vá para o dashboard desejado
2. Edite o panel
3. Na aba **Alert**, configure:
   - **Condition**: quando disparar o alerta
   - **Frequency**: frequência de verificação
   - **Notification**: para onde enviar

## 🧪 Testes e Validação

### Testar Métricas
```bash
# Gerar métricas de teste
curl -X POST http://localhost:8000/api/metrics/test-metrics

# Verificar métricas Prometheus
curl http://localhost:8000/api/metrics/prometheus

# Health check
curl http://localhost:8000/api/metrics/health
```

### Testar Frontend
```bash
cd frontend
npm run test
npm run build
```

## 🐛 Troubleshooting

### Problemas Comuns

1. **Loki não conecta**:
   - Verificar se `LOKI_URL` está correto
   - Sistema fallback para console logging

2. **Prometheus não coleta métricas**:
   - Verificar endpoint `/api/metrics/prometheus`
   - Conferir configuração `prometheus.yml`

3. **Grafana não mostra dados**:
   - Verificar data sources
   - Conferir queries e time range

### Logs de Debug
```bash
# Ver logs do backend
docker-compose logs backend

# Ver logs do Prometheus
docker-compose logs prometheus

# Ver logs do Grafana
docker-compose logs grafana
```

## 📈 Próximos Passos

1. **Personalizar Dashboards**: Criar dashboards específicos para seu negócio
2. **Alertas Avançados**: Configurar alertas via email/Slack
3. **Métricas de Negócio**: Adicionar métricas específicas do domínio
4. **Distributed Tracing**: Integrar Jaeger para tracing distribuído
5. **Logs Estruturados**: Expandir logging estruturado por toda aplicação

## 📞 Suporte

Para dúvidas ou problemas:
1. Verificar logs dos serviços
2. Consultar documentação do Grafana/Prometheus/Loki
3. Abrir issue no repositório

---

**Desenvolvido com ❤️ para o ML Project**