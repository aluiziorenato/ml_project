# 🚀 Guia Rápido de Deploy - Monitoramento ML Project

## 📋 Pré-requisitos
- Docker e Docker Compose instalados
- Arquivo `.env` configurado no backend
- Portas disponíveis: 3001 (Grafana), 9090 (Prometheus), 3100 (Loki)

## ⚡ Deploy Rápido

### 1. Configurar Variáveis de Ambiente
```bash
# backend/.env
METRICS_API_KEY=your-secure-random-key-here-256-bits
ENABLE_METRICS_AUTH=true
LOKI_URL=http://loki:3100
PROMETHEUS_PORT=8000
```

### 2. Atualizar Chave no Prometheus
```bash
# Editar monitoring/prometheus.yml - linha com credentials
credentials: 'your-secure-random-key-here-256-bits'
```

### 3. Deploy Completo
```bash
# Deploy com monitoramento
docker-compose -f docker-compose.yml -f docker-compose.monitoring.yml up -d

# Verificar serviços
docker-compose ps
```

### 4. Acessar Interfaces

| Serviço | URL | Credenciais |
|---------|-----|-------------|
| **Grafana** | http://localhost:3001 | admin / admin123 |
| **Prometheus** | http://localhost:9090 | - |
| **Backend API** | http://localhost:8000 | - |
| **Métricas** | http://localhost:8000/api/metrics/prometheus | Bearer token |

## 🧪 Testes de Validação

### 1. Testar Métricas (com autenticação)
```bash
# Gerar métricas de teste
curl -X POST http://localhost:8000/api/metrics/test-metrics

# Verificar métricas (com auth)
curl -H "Authorization: Bearer your-key" http://localhost:8000/api/metrics/prometheus

# Health check
curl http://localhost:8000/api/metrics/health
```

### 2. Verificar Dashboards Grafana
1. Acesse http://localhost:3001
2. Login: admin / admin123
3. Vá para "Dashboards" → "ML Project"
4. Verifique:
   - **Sistema de Monitoramento**: CPU, memória, requests
   - **Performance da API**: Latência, erros, endpoints

### 3. Testar Alertas Prometheus
1. Acesse http://localhost:9090
2. Vá para "Alerts"
3. Verifique regras carregadas
4. Status: Inactive/Pending/Firing

## 🚨 Alertas Configurados

| Alerta | Threshold | Duração |
|--------|-----------|---------|
| CPU Alto | > 85% | 5 min |
| CPU Crítico | > 95% | 2 min |
| Memória Alta | > 90% | 5 min |
| Taxa Erro API | > 5% | 5 min |
| Tempo Resposta | > 2s | 5 min |
| Serviço Offline | - | 1 min |

## 🔧 Troubleshooting

### Problema: Prometheus não coleta métricas
```bash
# Verificar logs
docker logs prometheus

# Testar endpoint manualmente
curl -H "Authorization: Bearer your-key" http://backend:8000/api/metrics/prometheus
```

### Problema: Grafana sem dados
1. Verificar data source Prometheus em http://localhost:3001
2. Teste conexão: Configuration → Data Sources → Prometheus
3. URL deve ser: http://prometheus:9090

### Problema: Alertas não funcionam
1. Verificar arquivo alert_rules.yml carregado
2. Prometheus → Status → Configuration
3. Verificar syntax: `promtool check rules monitoring/alert_rules.yml`

## 📊 Métricas Principais

### Sistema
- `system_cpu_usage_percent` - CPU usage
- `system_memory_usage_percent` - Memory usage  
- `system_disk_usage_percent` - Disk usage

### API
- `http_requests_total` - Total requests
- `http_request_duration_seconds` - Response time
- `application_errors_total` - Application errors

### Business
- `campaigns_active_total` - Active campaigns
- `ml_model_accuracy` - Model accuracy
- `user_logins_total` - User logins

## 🔒 Produção - Checklist Segurança

- [ ] Alterar METRICS_API_KEY para chave forte (256+ bits)
- [ ] Configurar HTTPS com certificados SSL
- [ ] Restringir acesso via firewall (portas 9090, 3001)
- [ ] Configurar backup automático Grafana
- [ ] Monitorar logs de acesso não autorizado
- [ ] Configurar notificações de alerta (Slack/email)

## 📞 Suporte

Para problemas ou dúvidas:
1. Verifique logs: `docker-compose logs [serviço]`
2. Execute teste: `python test_monitoring_integration.py`
3. Consulte DASHBOARD_MONITORING_GUIDE.md