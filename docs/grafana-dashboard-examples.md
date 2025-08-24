# 📊 Grafana Dashboard Examples - ML Project

Este documento contém exemplos completos de dashboards Grafana para o projeto ML, incluindo queries Prometheus, alertas e instruções de validação em produção.

## 🎯 Dashboards Principais

### 1. 📈 Dashboard Sistema - Visão Geral

Dashboard para monitoramento geral do sistema com métricas de performance e recursos.

```json
{
  "dashboard": {
    "id": null,
    "title": "ML Project - Sistema Geral",
    "tags": ["ml-project", "sistema", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Taxa de Requisições (por minuto)",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m]) * 60",
            "legendFormat": "{{method}} {{endpoint}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "displayMode": "list",
              "orientation": "horizontal"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 500}
              ]
            },
            "unit": "reqps"
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Uso de CPU (%)",
        "type": "gauge",
        "targets": [
          {
            "expr": "system_cpu_usage_percent",
            "legendFormat": "CPU Usage",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 70},
                {"color": "red", "value": 85}
              ]
            },
            "unit": "percent",
            "min": 0,
            "max": 100
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Uso de Memória (%)",
        "type": "gauge",
        "targets": [
          {
            "expr": "system_memory_usage_percent",
            "legendFormat": "Memory Usage",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 75},
                {"color": "red", "value": 90}
              ]
            },
            "unit": "percent",
            "min": 0,
            "max": 100
          }
        },
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      },
      {
        "id": 4,
        "title": "Tempo de Resposta (Percentis)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P50",
            "refId": "A"
          },
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P95",
            "refId": "B"
          },
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99",
            "refId": "C"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "palette-classic"
            },
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "linear",
              "barAlignment": 0,
              "lineWidth": 1,
              "fillOpacity": 10,
              "gradientMode": "none",
              "spanNulls": false,
              "insertNulls": false,
              "showPoints": "never",
              "pointSize": 5,
              "stacking": {"mode": "none", "group": "A"},
              "axisPlacement": "auto",
              "axisLabel": "",
              "scaleDistribution": {"type": "linear"}
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 0.5},
                {"color": "red", "value": 1.0}
              ]
            },
            "unit": "s"
          }
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      },
      {
        "id": 5,
        "title": "Status Codes por Endpoint",
        "type": "table",
        "targets": [
          {
            "expr": "sum by (endpoint, status_code) (rate(http_requests_total[5m]) * 60)",
            "legendFormat": "{{endpoint}} - {{status_code}}",
            "refId": "A",
            "format": "table"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 50},
                {"color": "red", "value": 100}
              ]
            },
            "unit": "reqps"
          },
          "overrides": [
            {
              "matcher": {"id": "byName", "options": "status_code"},
              "properties": [
                {
                  "id": "mappings",
                  "value": [
                    {"options": {"2*": {"color": "green", "index": 0}}, "type": "regex"},
                    {"options": {"4*": {"color": "yellow", "index": 1}}, "type": "regex"},
                    {"options": {"5*": {"color": "red", "index": 2}}, "type": "regex"}
                  ]
                }
              ]
            }
          ]
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "timepicker": {},
    "templating": {"list": []},
    "annotations": {"list": []},
    "refresh": "30s",
    "schemaVersion": 30,
    "version": 1,
    "links": []
  }
}
```

### 2. 🏢 Dashboard Negócios - Campanhas e ML

Dashboard focado em métricas de negócio, campanhas e modelos ML.

```json
{
  "dashboard": {
    "id": null,
    "title": "ML Project - Métricas de Negócio", 
    "tags": ["ml-project", "business", "campaigns", "ml"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Campanhas Ativas",
        "type": "stat",
        "targets": [
          {
            "expr": "campaigns_active_total",
            "legendFormat": "Campanhas Ativas",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "green", "value": 5}
              ]
            },
            "unit": "short"
          }
        },
        "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Cliques por Campanha (Últimas 24h)",
        "type": "bargauge",
        "targets": [
          {
            "expr": "increase(campaigns_clicks_total[24h])",
            "legendFormat": "{{campaign_id}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "displayMode": "gradient",
              "orientation": "horizontal"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 100},
                {"color": "red", "value": 1000}
              ]
            },
            "unit": "short"
          }
        },
        "gridPos": {"h": 6, "w": 9, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Taxa de Conversão por Campanha",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(campaigns_conversions_total[1h]) / rate(campaigns_clicks_total[1h]) * 100",
            "legendFormat": "{{campaign_id}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 2},
                {"color": "green", "value": 5}
              ]
            },
            "unit": "percent"
          }
        },
        "gridPos": {"h": 6, "w": 9, "x": 15, "y": 0}
      },
      {
        "id": 4,
        "title": "Predições de Modelos ML (por hora)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "rate(ml_model_predictions_total[5m]) * 3600",
            "legendFormat": "{{model_name}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "linear",
              "lineWidth": 2,
              "fillOpacity": 20,
              "gradientMode": "opacity"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1000},
                {"color": "red", "value": 5000}
              ]
            },
            "unit": "ops"
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 6}
      },
      {
        "id": 5,
        "title": "Acurácia dos Modelos ML",
        "type": "timeseries",
        "targets": [
          {
            "expr": "ml_model_accuracy",
            "legendFormat": "{{model_name}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "linear",
              "lineWidth": 2,
              "fillOpacity": 0
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 0.7},
                {"color": "green", "value": 0.85}
              ]
            },
            "unit": "percentunit",
            "min": 0,
            "max": 1
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 6}
      },
      {
        "id": 6,
        "title": "Chamadas de API por Serviço",
        "type": "piechart",
        "targets": [
          {
            "expr": "sum by (service) (rate(api_calls_total[1h]) * 3600)",
            "legendFormat": "{{service}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "hideFrom": {
                "legend": false,
                "tooltip": false,
                "vis": false
              }
            },
            "mappings": [],
            "unit": "short"
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 14}
      },
      {
        "id": 7,
        "title": "ROI por Campanha (Estimado)",
        "type": "table",
        "targets": [
          {
            "expr": "campaigns_conversions_total / campaigns_clicks_total * 100",
            "legendFormat": "Conversion Rate",
            "refId": "A",
            "format": "table"
          },
          {
            "expr": "campaigns_clicks_total",
            "legendFormat": "Total Clicks",
            "refId": "B", 
            "format": "table"
          },
          {
            "expr": "campaigns_conversions_total",
            "legendFormat": "Total Conversions",
            "refId": "C",
            "format": "table"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "yellow", "value": 2},
                {"color": "green", "value": 5}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 14}
      }
    ],
    "time": {"from": "now-6h", "to": "now"},
    "timepicker": {},
    "templating": {"list": []},
    "annotations": {"list": []},
    "refresh": "1m",
    "schemaVersion": 30,
    "version": 1,
    "links": []
  }
}
```

### 3. 🚨 Dashboard Alertas e Erros

Dashboard para monitoramento de erros e alertas críticos.

```json
{
  "dashboard": {
    "id": null,
    "title": "ML Project - Alertas e Monitoramento",
    "tags": ["ml-project", "alerts", "errors", "monitoring"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Taxa de Erro (%)",
        "type": "stat",
        "targets": [
          {
            "expr": "rate(http_requests_total{status_code=~\"4..|5..\"}[5m]) / rate(http_requests_total[5m]) * 100",
            "legendFormat": "Error Rate",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 5}
              ]
            },
            "unit": "percent"
          }
        },
        "gridPos": {"h": 6, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Erros por Status Code",
        "type": "bargauge",
        "targets": [
          {
            "expr": "sum by (status_code) (rate(http_requests_total{status_code=~\"4..|5..\"}[5m]) * 60)",
            "legendFormat": "{{status_code}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "displayMode": "gradient",
              "orientation": "horizontal"
            },
            "mappings": [
              {"options": {"match": "null", "result": {"text": "N/A"}}, "type": "special"}
            ],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 10}
              ]
            },
            "unit": "reqps"
          }
        },
        "gridPos": {"h": 6, "w": 9, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Alertas de Sistema",
        "type": "logs",
        "targets": [
          {
            "expr": "{job=\"backend\"} |= \"ERROR\" or |= \"CRITICAL\"",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"}
          }
        },
        "gridPos": {"h": 6, "w": 9, "x": 15, "y": 0}
      },
      {
        "id": 4,
        "title": "Tempo de Resposta P99 (por endpoint)",
        "type": "timeseries",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m])) by (endpoint)",
            "legendFormat": "{{endpoint}}",
            "refId": "A"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "palette-classic"},
            "custom": {
              "drawStyle": "line",
              "lineInterpolation": "linear",
              "lineWidth": 1,
              "fillOpacity": 10,
              "gradientMode": "none"
            },
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 1},
                {"color": "red", "value": 3}
              ]
            },
            "unit": "s"
          }
        },
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 6}
      },
      {
        "id": 5,
        "title": "Erros de Aplicação por Tipo",
        "type": "table",
        "targets": [
          {
            "expr": "sum by (error_type) (rate(application_errors_total[1h]) * 3600)",
            "legendFormat": "{{error_type}}",
            "refId": "A",
            "format": "table"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [],
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 10},
                {"color": "red", "value": 50}
              ]
            },
            "unit": "short"
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 14}
      },
      {
        "id": 6,
        "title": "Status de Conectividade Externa",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"backend\"}",
            "legendFormat": "Backend",
            "refId": "A"
          },
          {
            "expr": "up{job=\"postgres\"}",
            "legendFormat": "Database",
            "refId": "B"
          },
          {
            "expr": "up{job=\"redis\"}",
            "legendFormat": "Redis",
            "refId": "C"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {"mode": "thresholds"},
            "mappings": [
              {"options": {"0": {"text": "DOWN"}}, "type": "value"},
              {"options": {"1": {"text": "UP"}}, "type": "value"}
            ],
            "thresholds": {
              "steps": [
                {"color": "red", "value": null},
                {"color": "green", "value": 1}
              ]
            },
            "unit": "short"
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 14}
      }
    ],
    "time": {"from": "now-1h", "to": "now"},
    "timepicker": {},
    "templating": {"list": []},
    "annotations": {"list": []},
    "refresh": "30s",
    "schemaVersion": 30,
    "version": 1,
    "links": []
  }
}
```

## 🔔 Configuração de Alertas

### Regras de Alerta Prometheus

Crie arquivo `alert_rules.yml` no diretório de configuração do Prometheus:

```yaml
groups:
  - name: ml_project_alerts
    rules:
      # Alerta de alta taxa de erro
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
          service: backend
        annotations:
          summary: "Taxa de erro alta detectada"
          description: "Taxa de erro de {{ $value | humanizePercentage }} nos últimos 5 minutos"

      # Alerta de tempo de resposta alto
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
          service: backend
        annotations:
          summary: "Tempo de resposta P95 alto"
          description: "P95 do tempo de resposta é {{ $value }}s"

      # Alerta de uso de CPU alto
      - alert: HighCPUUsage
        expr: system_cpu_usage_percent > 80
        for: 3m
        labels:
          severity: warning
          component: system
        annotations:
          summary: "Uso de CPU alto"
          description: "Uso de CPU em {{ $value }}%"

      # Alerta de uso de memória alto
      - alert: HighMemoryUsage
        expr: system_memory_usage_percent > 85
        for: 3m
        labels:
          severity: critical
          component: system
        annotations:
          summary: "Uso de memória alto"
          description: "Uso de memória em {{ $value }}%"

      # Alerta de baixa taxa de conversão
      - alert: LowConversionRate
        expr: rate(campaigns_conversions_total[1h]) / rate(campaigns_clicks_total[1h]) < 0.02
        for: 10m
        labels:
          severity: warning
          component: business
        annotations:
          summary: "Taxa de conversão baixa"
          description: "Taxa de conversão da campanha {{ $labels.campaign_id }} está em {{ $value | humanizePercentage }}"

      # Alerta de acurácia de modelo baixa
      - alert: LowModelAccuracy
        expr: ml_model_accuracy < 0.7
        for: 5m
        labels:
          severity: warning
          component: ml
        annotations:
          summary: "Acurácia de modelo baixa"
          description: "Modelo {{ $labels.model_name }} com acurácia de {{ $value | humanizePercentage }}"
```

## 🏭 Instruções para Validação em Produção

### 1. 📝 Lista de Verificação Pré-Produção

Antes de implementar em produção, verifique:

#### ✅ Configuração do Prometheus
```bash
# Verificar configuração do Prometheus
curl http://prometheus:9090/api/v1/config
curl http://prometheus:9090/api/v1/targets

# Verificar se métricas estão sendo coletadas
curl http://prometheus:9090/api/v1/query?query=up

# Testar queries específicas
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[5m])"
```

#### ✅ Configuração do Grafana
```bash
# Verificar conectividade com Prometheus
curl -H "Authorization: Bearer <API_KEY>" \
  http://grafana:3000/api/datasources/proxy/1/api/v1/label/__name__/values

# Testar dashboard queries
curl -H "Authorization: Bearer <API_KEY>" \
  "http://grafana:3000/api/ds/query" \
  -d '{"queries":[{"expr":"up","refId":"A"}]}'
```

#### ✅ Endpoints de Métricas
```bash
# Verificar endpoint de métricas
curl http://backend:8000/api/metrics/prometheus

# Verificar endpoint de health
curl http://backend:8000/api/metrics/health

# Testar geração de métricas
curl -X POST http://backend:8000/api/metrics/test-metrics
```

### 2. 🧪 Testes de Validação em Produção

#### Script de Validação Automatizada

```bash
#!/bin/bash
# validate_monitoring.sh

echo "🔍 Validando sistema de monitoramento em produção..."

# Configuração
PROMETHEUS_URL="http://prometheus:9090"
GRAFANA_URL="http://grafana:3000"
BACKEND_URL="http://backend:8000"
GRAFANA_API_KEY="${GRAFANA_API_KEY}"

# Funções de validação
validate_prometheus() {
    echo "📊 Validando Prometheus..."
    
    # Verificar se Prometheus está online
    if curl -sf "${PROMETHEUS_URL}/api/v1/targets" > /dev/null; then
        echo "✅ Prometheus está online"
    else
        echo "❌ Prometheus não está acessível"
        return 1
    fi
    
    # Verificar targets ativos
    active_targets=$(curl -s "${PROMETHEUS_URL}/api/v1/targets" | jq '.data.activeTargets | length')
    echo "📈 Targets ativos: ${active_targets}"
    
    # Verificar métricas específicas
    metrics_to_check=(
        "up"
        "http_requests_total"
        "system_cpu_usage_percent"
        "system_memory_usage_percent"
    )
    
    for metric in "${metrics_to_check[@]}"; do
        result=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=${metric}" | jq -r '.data.result | length')
        if [[ $result -gt 0 ]]; then
            echo "✅ Métrica ${metric}: ${result} séries"
        else
            echo "⚠️ Métrica ${metric}: sem dados"
        fi
    done
}

validate_grafana() {
    echo "📊 Validando Grafana..."
    
    # Verificar se Grafana está online
    if curl -sf "${GRAFANA_URL}/api/health" > /dev/null; then
        echo "✅ Grafana está online"
    else
        echo "❌ Grafana não está acessível"
        return 1
    fi
    
    # Verificar datasources
    if [[ -n "$GRAFANA_API_KEY" ]]; then
        datasources=$(curl -s -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
                     "${GRAFANA_URL}/api/datasources" | jq 'length')
        echo "🔗 Datasources configurados: ${datasources}"
        
        # Testar conectividade com Prometheus
        test_query='{"queries":[{"expr":"up","refId":"A","datasource":{"type":"prometheus"}}]}'
        query_result=$(curl -s -H "Authorization: Bearer ${GRAFANA_API_KEY}" \
                      -H "Content-Type: application/json" \
                      -d "${test_query}" \
                      "${GRAFANA_URL}/api/ds/query")
        
        if echo "$query_result" | jq -e '.results' > /dev/null; then
            echo "✅ Consultas Grafana funcionando"
        else
            echo "⚠️ Problema com consultas Grafana"
        fi
    else
        echo "⚠️ GRAFANA_API_KEY não definida, pulando testes de API"
    fi
}

validate_backend_metrics() {
    echo "🖥️ Validando métricas do backend..."
    
    # Verificar endpoint de métricas
    if curl -sf "${BACKEND_URL}/api/metrics/prometheus" > /dev/null; then
        echo "✅ Endpoint de métricas acessível"
        
        # Contar métricas disponíveis
        metrics_count=$(curl -s "${BACKEND_URL}/api/metrics/prometheus" | grep -c "^# TYPE")
        echo "📊 Tipos de métricas disponíveis: ${metrics_count}"
        
    else
        echo "❌ Endpoint de métricas não acessível"
        return 1
    fi
    
    # Verificar endpoint de health
    if health_response=$(curl -s "${BACKEND_URL}/api/metrics/health"); then
        status=$(echo "$health_response" | jq -r '.status')
        if [[ "$status" == "healthy" ]]; then
            echo "✅ Health check: ${status}"
            
            # Mostrar métricas de sistema
            cpu=$(echo "$health_response" | jq -r '.system.cpu_percent')
            memory=$(echo "$health_response" | jq -r '.system.memory.percent')
            echo "💻 CPU: ${cpu}%, Memória: ${memory}%"
        else
            echo "⚠️ Health check: ${status}"
        fi
    else
        echo "❌ Health endpoint não acessível"
        return 1
    fi
}

validate_alerts() {
    echo "🚨 Validando alertas..."
    
    # Verificar regras de alerta
    if alerts_response=$(curl -s "${PROMETHEUS_URL}/api/v1/rules"); then
        rules_count=$(echo "$alerts_response" | jq '.data.groups | map(.rules | length) | add')
        active_alerts=$(echo "$alerts_response" | jq '.data.groups | map(.rules[] | select(.state == "firing")) | length')
        
        echo "📋 Regras de alerta: ${rules_count}"
        echo "🔥 Alertas ativos: ${active_alerts}"
        
        if [[ $active_alerts -gt 0 ]]; then
            echo "⚠️ Há alertas ativos - verifique o dashboard"
        fi
    else
        echo "❌ Não foi possível verificar alertas"
    fi
}

load_test_metrics() {
    echo "🧪 Executando teste de carga nas métricas..."
    
    # Gerar algumas requisições para testar métricas
    for i in {1..10}; do
        curl -s "${BACKEND_URL}/api/metrics/health" > /dev/null
        curl -s "${BACKEND_URL}/api/metrics/prometheus" > /dev/null
        sleep 0.1
    done
    
    # Gerar métricas de teste
    curl -s -X POST "${BACKEND_URL}/api/metrics/test-metrics" > /dev/null
    
    echo "✅ Teste de carga concluído"
    
    # Aguardar propagação das métricas
    sleep 5
    
    # Verificar se métricas foram atualizadas
    http_requests=$(curl -s "${PROMETHEUS_URL}/api/v1/query?query=http_requests_total" | jq '.data.result | length')
    
    if [[ $http_requests -gt 0 ]]; then
        echo "✅ Métricas de HTTP atualizadas: ${http_requests} séries"
    else
        echo "⚠️ Métricas de HTTP não encontradas"
    fi
}

# Executar validações
echo "🚀 Iniciando validação completa..."
echo "=================================="

validate_prometheus || echo "❌ Falha na validação do Prometheus"
echo ""

validate_grafana || echo "❌ Falha na validação do Grafana" 
echo ""

validate_backend_metrics || echo "❌ Falha na validação das métricas do backend"
echo ""

validate_alerts || echo "❌ Falha na validação dos alertas"
echo ""

load_test_metrics || echo "❌ Falha no teste de carga"
echo ""

echo "🎉 Validação completa!"
echo "📊 Acesse os dashboards em: ${GRAFANA_URL}"
echo "📈 Acesse o Prometheus em: ${PROMETHEUS_URL}"
```

### 3. 📋 Checklist de Validação Manual

#### ✅ Dashboards Grafana

1. **Dashboard Sistema Geral**
   - [ ] Taxa de requisições sendo exibida corretamente
   - [ ] Uso de CPU e memória atualizando em tempo real
   - [ ] Gráfico de tempo de resposta com dados válidos
   - [ ] Tabela de status codes populada

2. **Dashboard Métricas de Negócio**
   - [ ] Contadores de campanhas funcionando
   - [ ] Taxa de conversão calculada corretamente
   - [ ] Métricas de ML sendo atualizadas
   - [ ] Distribuição de API calls exibida

3. **Dashboard Alertas e Monitoramento**
   - [ ] Taxa de erro calculada e exibida
   - [ ] Logs de erros sendo capturados
   - [ ] Status de conectividade correto
   - [ ] Alertas configurados e funcionando

#### ✅ Alertas e Notificações

1. **Testar Alertas Críticos**
   ```bash
   # Simular alta taxa de erro (apenas em ambiente de teste)
   for i in {1..100}; do
     curl http://backend:8000/api/nonexistent-endpoint
   done
   
   # Verificar se alerta foi disparado
   curl http://prometheus:9090/api/v1/alerts
   ```

2. **Testar Notificações**
   - [ ] Slack/Teams recebendo alertas
   - [ ] Email de alertas funcionando
   - [ ] Webhook de alertas configurado

#### ✅ Performance e Escalabilidade

1. **Teste de Carga**
   ```bash
   # Usar Apache Bench para teste de carga
   ab -n 1000 -c 10 http://backend:8000/api/metrics/health
   
   # Verificar se métricas capturam a carga
   curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total[1m])"
   ```

2. **Monitoramento Contínuo**
   - [ ] Métricas sendo coletadas a cada 15 segundos
   - [ ] Dashboards atualizando automaticamente
   - [ ] Retenção de dados configurada (7-30 dias)
   - [ ] Backup dos dados de métricas

### 4. 🔧 Troubleshooting Comum

#### Problema: Métricas não aparecem no Grafana

**Solução:**
```bash
# 1. Verificar conectividade Prometheus
curl http://prometheus:9090/api/v1/targets

# 2. Verificar se backend está expondo métricas
curl http://backend:8000/api/metrics/prometheus

# 3. Verificar configuração do datasource no Grafana
curl -H "Authorization: Bearer <API_KEY>" \
  http://grafana:3000/api/datasources
```

#### Problema: Alertas não disparando

**Solução:**
```bash
# 1. Verificar regras de alerta
curl http://prometheus:9090/api/v1/rules

# 2. Verificar Alertmanager
curl http://alertmanager:9093/api/v1/status

# 3. Testar regra manualmente
curl "http://prometheus:9090/api/v1/query?query=rate(http_requests_total{status_code=~\"5..\"}[5m])"
```

#### Problema: Performance baixa dos dashboards

**Solução:**
1. Otimizar queries Prometheus (reduzir intervalos)
2. Aumentar cache do Grafana
3. Usar recording rules para queries complexas
4. Reduzir frequência de refresh

### 5. 📊 Métricas de Qualidade do Monitoramento

Para garantir que o sistema de monitoramento está funcionando corretamente, monitore estas métricas:

```promql
# Disponibilidade do sistema de monitoramento
up{job="prometheus"}
up{job="grafana"}  
up{job="backend"}

# Latência das queries
prometheus_rule_evaluation_duration_seconds
grafana_api_response_time_seconds

# Volume de métricas coletadas
prometheus_tsdb_samples_appended_total
prometheus_tsdb_head_series

# Alertas disparados
ALERTS{alertstate="firing"}
alertmanager_notifications_total
```

## 🎯 Conclusão

Este guia fornece uma base sólida para implementar e validar dashboards Grafana em produção. Lembre-se de:

1. **Testar em ambiente de staging** antes da produção
2. **Monitorar o próprio sistema de monitoramento**
3. **Revisar e otimizar queries regularmente**
4. **Manter documentação atualizada**
5. **Treinar a equipe** nos dashboards e alertas

Para dúvidas ou problemas, consulte os logs dos serviços e a documentação oficial do Prometheus/Grafana.