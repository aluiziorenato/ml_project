# 🚀 Mercado Livre ML Automation System

Este projeto implementa três módulos independentes para automação de vendas no Mercado Livre, usando IA e Machine Learning.

## 📦 Módulos Implementados

### 1. 🎯 Simulador de Campanhas (`simulator_service`)
**Porta: 8001**

Simula campanhas publicitárias com base em parâmetros de entrada e fornece métricas estimadas.

**Funcionalidades:**
- Simulação de campanhas com métricas realistas
- Cálculo de ROI, CPC, alcance e conversões
- Recomendações baseadas em dados
- Interface web interativa

**Endpoints:**
- `GET /` - Interface web
- `GET /health` - Health check
- `POST /api/simulate` - Simular campanha
- `GET /api/simulation/{campaign_id}` - Buscar simulação

### 2. 🧠 Aprendizado Contínuo (`learning_service`)
**Porta: 8002**

Sistema de aprendizado contínuo que melhora os modelos com base em resultados reais.

**Funcionalidades:**
- Atualização manual de modelos
- Upload em lote via CSV
- Métricas de precisão em tempo real
- Histórico visual de aprendizado

**Endpoints:**
- `GET /` - Interface web
- `GET /health` - Health check
- `POST /api/update-model` - Atualizar modelo
- `POST /api/upload-results` - Upload CSV
- `GET /api/learning-history` - Histórico
- `GET /api/model-performance` - Performance atual

### 3. ✨ Otimizador de Copywriting (`optimizer_ai`)
**Porta: 8003**

Otimiza textos de anúncios usando técnicas de IA para melhorar conversões.

**Funcionalidades:**
- Otimização de textos com IA
- Score SEO e legibilidade
- Testes A/B de variações
- Estimativa de melhoria de performance

**Endpoints:**
- `GET /` - Interface web
- `GET /health` - Health check
- `POST /api/optimize-copy` - Otimizar texto
- `POST /api/ab-test` - Criar teste A/B

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Simulator      │    │  Learning       │    │  Optimizer      │
│  Service        │    │  Service        │    │  AI             │
│  Port: 8001     │    │  Port: 8002     │    │  Port: 8003     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Kubernetes     │
                    │  Cluster        │
                    └─────────────────┘
```

## 🐳 Docker & Kubernetes

Cada serviço inclui:
- **Dockerfile multistage** para build otimizado
- **Kubernetes deployment.yaml** com health checks
- **Kubernetes service.yaml** para exposição
- **Health checks** e probes configurados

### Build e Deploy Local

```bash
# Simulator Service
cd simulator_service
docker build -t simulator-service:latest .
docker run -p 8001:8001 simulator-service:latest

# Learning Service  
cd learning_service
docker build -t learning-service:latest .
docker run -p 8002:8002 learning-service:latest

# Optimizer AI
cd optimizer_ai
docker build -t optimizer-ai:latest .
docker run -p 8003:8003 optimizer-ai:latest
```

### Deploy Kubernetes

```bash
# Deploy todos os serviços
kubectl apply -f simulator_service/k8s/
kubectl apply -f learning_service/k8s/
kubectl apply -f optimizer_ai/k8s/

# Verificar status
kubectl get pods -l component=ml-automation
kubectl get services
```

## 🧪 Testes

### Simulador de Campanhas
```bash
curl -X POST http://localhost:8001/api/simulate \
-H "Content-Type: application/json" \
-d '{
  "product_name": "Smartphone Samsung",
  "category": "electronics",
  "budget": 1000.0,
  "duration_days": 14,
  "target_audience": "young_adults",
  "keywords": ["smartphone", "samsung", "android"]
}'
```

### Aprendizado Contínuo
```bash
curl -X POST http://localhost:8002/api/update-model \
-H "Content-Type: application/json" \
-d '{
  "campaign_id": "CAMP_123456",
  "actual_clicks": 3500,
  "actual_conversions": 105,
  "actual_revenue": 3200.50,
  "predicted_clicks": 3562,
  "predicted_conversions": 106,
  "predicted_revenue": 3093.01
}'
```

### Otimizador de Copywriting
```bash
curl -X POST http://localhost:8003/api/optimize-copy \
-H "Content-Type: application/json" \
-d '{
  "original_text": "Smartphone com boa qualidade",
  "target_audience": "young_adults",
  "product_category": "electronics",
  "optimization_goal": "conversions",
  "keywords": ["smartphone", "android", "barato"]
}'
```

## 🎯 Características

### ✅ Independência e Escalabilidade
- Cada serviço é completamente independente
- Comunicação via REST APIs
- Escalabilidade horizontal com Kubernetes
- Load balancing automático

### ✅ Produção Ready
- Health checks implementados
- Docker multistage para otimização
- Resource limits configurados
- Logging estruturado

### ✅ Interface Amigável
- Frontend HTML/JS integrado
- Design responsivo
- Feedback visual em tempo real
- Fácil integração

## 📊 Métricas e Monitoramento

Cada serviço expõe:
- Health check endpoint (`/health`)
- Logs estruturados
- Métricas de performance
- Status de processamento

## 🔮 Roadmap

- [ ] Integração com Prometheus/Grafana
- [ ] Autenticação JWT
- [ ] Rate limiting
- [ ] Cache Redis
- [ ] Métricas avançadas
- [ ] CI/CD pipeline

## 🛠️ Tecnologias

- **Backend:** FastAPI (Python 3.11)
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Containerização:** Docker multistage
- **Orquestração:** Kubernetes
- **Monitoramento:** Health checks

---

**Desenvolvido para Mercado Livre** 🇧🇷
Sistema completo e pronto para produção!