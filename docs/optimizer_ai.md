# 🧠 Optimizer AI - Documentação Técnica

## 📋 Visão Geral

O **Optimizer AI** é um microserviço de IA generativa especializado em copywriting, oferecendo endpoints para geração de títulos e descrições otimizadas para marketing. O serviço utiliza técnicas avançadas de processamento de linguagem natural e algoritmos de otimização para criar conteúdo persuasivo e eficaz.

---

## 🏗️ Arquitetura

### Componentes Principais

```
┌─────────────────────────────────────────┐
│              Client Apps                │
├─────────────────────────────────────────┤
│            Load Balancer                │
├─────────────────────────────────────────┤
│          Kubernetes Ingress             │
├─────────────────────────────────────────┤
│         Optimizer AI Service           │
│  ┌─────────────┬─────────────────────┐  │
│  │   FastAPI   │   AI Generation     │  │
│  │   Endpoints │   Engine            │  │
│  └─────────────┴─────────────────────┘  │
└─────────────────────────────────────────┘
```

### Stack Tecnológico

- **Framework**: FastAPI 0.116.1
- **Runtime**: Python 3.12
- **Server**: Uvicorn
- **Containerização**: Docker
- **Orquestração**: Kubernetes
- **Arquitetura**: Microserviços

---

## 🚀 Endpoints da API

### Base URL
```
http://localhost:8001 (desenvolvimento)
http://optimizer-ai.local (produção)
```

### 1. **POST** `/generate_title`

Gera títulos otimizados usando IA para copywriting.

#### Request Body
```json
{
  "text": "Smartphone com câmera avançada e bateria de longa duração",
  "keywords": ["smartphone", "câmera", "bateria"],
  "tone": "professional",
  "max_length": 60
}
```

#### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `text` | string | ✅ | Texto base ou descrição do produto (1-1000 chars) |
| `keywords` | array[string] | ❌ | Palavras-chave para incluir |
| `tone` | string | ❌ | Tom: `professional`, `casual`, `exciting`, `luxury` |
| `max_length` | integer | ❌ | Comprimento máximo (10-100 chars, padrão: 60) |

#### Response
```json
{
  "title": "Professional Smartphone Solutions",
  "alternatives": [
    "Advanced Camera Technology",
    "Premium Battery Experience"
  ],
  "keywords_used": ["smartphone"],
  "length": 32,
  "tone": "professional"
}
```

### 2. **POST** `/generate_description`

Gera descrições otimizadas com call-to-action.

#### Request Body
```json
{
  "text": "Produto inovador para escritório",
  "keywords": ["produtividade", "escritório"],
  "tone": "professional",
  "max_length": 160,
  "cta_style": "soft"
}
```

#### Parâmetros

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `text` | string | ✅ | Texto base ou informações do produto (1-2000 chars) |
| `keywords` | array[string] | ❌ | Palavras-chave para incluir |
| `tone` | string | ❌ | Tom: `professional`, `casual`, `exciting`, `luxury` |
| `max_length` | integer | ❌ | Comprimento máximo (50-500 chars, padrão: 160) |
| `cta_style` | string | ❌ | Estilo CTA: `soft`, `direct`, `urgent` |

#### Response
```json
{
  "description": "Innovative office solutions designed to deliver outstanding performance and reliability. Learn more about our comprehensive platform.",
  "alternatives": [
    "Quality productivity tools for modern workspaces. Discover how our solutions work.",
    "Professional office technology that provides effective results. Contact us today."
  ],
  "keywords_used": ["office", "productivity"],
  "length": 142,
  "tone": "professional",
  "cta_included": true
}
```

### 3. **GET** `/health`

Endpoint de verificação de saúde do serviço.

#### Response
```json
{
  "status": "ok",
  "service": "optimizer_ai"
}
```

---

## 🐳 Deploy com Docker

### Build da Imagem

```bash
cd optimizer_ai/
docker build -t optimizer-ai:latest .
```

### Execução Local

```bash
# Executar container
docker run -d \
  --name optimizer-ai \
  -p 8001:8001 \
  optimizer-ai:latest

# Verificar logs
docker logs optimizer-ai

# Verificar saúde
curl http://localhost:8001/health
```

### Configuração de Ambiente

O serviço suporta as seguintes variáveis de ambiente:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `PORT` | `8001` | Porta do serviço |
| `LOG_LEVEL` | `info` | Nível de log |
| `PYTHONPATH` | `/app` | Caminho Python |

---

## ☸️ Deploy no Kubernetes

### Pré-requisitos

- Cluster Kubernetes configurado
- kubectl instalado e configurado
- Imagem Docker disponível no registry

### Deploy Completo

```bash
# Aplicar manifesto completo
kubectl apply -f Deployment.yaml

# Verificar status
kubectl get pods -n ml-project
kubectl get services -n ml-project
kubectl get ingress -n ml-project
```

### Componentes Kubernetes

#### 1. **Namespace**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ml-project
```

#### 2. **Deployment**
- **Replicas**: 2 instâncias
- **Strategy**: RollingUpdate
- **Resources**: 256Mi-512Mi RAM, 250m-500m CPU
- **Probes**: Health checks configurados

#### 3. **Services**
- **ClusterIP**: Comunicação interna (porta 80)
- **NodePort**: Acesso externo (porta 30001)

#### 4. **Ingress**
- **Host**: optimizer-ai.local
- **CORS**: Configurado para APIs
- **SSL**: Suporte configurável

#### 5. **HPA (Horizontal Pod Autoscaler)**
- **Min replicas**: 2
- **Max replicas**: 5
- **Target CPU**: 70%

### Monitoramento

```bash
# Status dos pods
kubectl get pods -n ml-project -l app=optimizer-ai

# Logs em tempo real
kubectl logs -f deployment/optimizer-ai -n ml-project

# Métricas de HPA
kubectl get hpa -n ml-project

# Status do serviço
kubectl get svc optimizer-ai-service -n ml-project
```

---

## 🔧 Algoritmos de IA

### Engine de Geração de Conteúdo

O serviço implementa algoritmos inspirados em IA para:

#### 1. **Extração de Conceitos**
- Análise de texto com regex otimizado
- Filtragem de stop words
- Identificação de conceitos-chave

#### 2. **Geração de Títulos**
- Templates baseados em tom de voz
- Incorporação inteligente de keywords
- Otimização por comprimento

#### 3. **Geração de Descrições**
- Estruturas narrativas adaptáveis
- Call-to-action contextual
- Variações tonais automáticas

#### 4. **Otimização SEO**
- Densidade de palavras-chave
- Comprimento otimizado
- Estrutura persuasiva

### Tons de Voz Suportados

| Tom | Características | Uso Recomendado |
|-----|----------------|----------------|
| `professional` | Formal, técnico, confiável | B2B, serviços corporativos |
| `casual` | Amigável, acessível, direto | E-commerce, lifestyle |
| `exciting` | Energético, inovador, impactante | Tecnologia, startups |
| `luxury` | Sofisticado, exclusivo, premium | Produtos de luxo, alta qualidade |

---

## 📊 Exemplos de Uso

### Exemplo 1: E-commerce

```bash
curl -X POST "http://localhost:8001/generate_title" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Tênis esportivo com tecnologia de amortecimento",
    "keywords": ["tênis", "esporte", "conforto"],
    "tone": "exciting",
    "max_length": 50
  }'
```

**Response:**
```json
{
  "title": "Revolutionary Tênis Innovation!",
  "alternatives": ["Game-Changing Esporte Technology"],
  "keywords_used": ["tênis", "esporte"],
  "length": 32,
  "tone": "exciting"
}
```

### Exemplo 2: Serviços B2B

```bash
curl -X POST "http://localhost:8001/generate_description" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Software de gestão empresarial para pequenas empresas",
    "keywords": ["gestão", "empresarial", "software"],
    "tone": "professional",
    "max_length": 200,
    "cta_style": "direct"
  }'
```

**Response:**
```json
{
  "description": "Professional software solutions deliver exceptional results through innovative technology and expert service. Our gestão platform provides reliable, scalable solutions for modern enterprises. Get started today.",
  "alternatives": [...],
  "keywords_used": ["software", "gestão", "empresarial"],
  "length": 198,
  "tone": "professional",
  "cta_included": true
}
```

---

## 🚦 Status Codes e Tratamento de Erros

### Códigos de Resposta

| Código | Descrição | Ação |
|--------|-----------|------|
| `200` | Sucesso | Conteúdo gerado com sucesso |
| `400` | Bad Request | Validar parâmetros de entrada |
| `422` | Validation Error | Corrigir formato dos dados |
| `500` | Internal Server Error | Verificar logs do serviço |

### Exemplo de Erro

```json
{
  "detail": "Text must be a non-empty string"
}
```

---

## 🔒 Segurança

### Implementações de Segurança

- **Container não-root**: Execução com usuário `appuser`
- **Security Context**: Configurações restritivas no Kubernetes
- **Resource Limits**: Controle de CPU e memória
- **Health Checks**: Monitoramento contínuo
- **CORS**: Configuração controlada de origens

### Boas Práticas

1. **Validação rigorosa** de inputs
2. **Logging estruturado** para auditoria
3. **Rate limiting** (implementar conforme necessário)
4. **Autenticação/Autorização** (integrar com sistema principal)

---

## 📈 Escalabilidade

### Características

- **Stateless**: Sem dependências de estado
- **Horizontal Scaling**: HPA configurado
- **Resource Efficient**: Otimizado para baixo consumo
- **Fast Startup**: Inicialização rápida

### Recomendações de Produção

1. **Configurar limites de recursos adequados**
2. **Implementar circuit breakers para APIs externas**
3. **Adicionar métricas customizadas (Prometheus)**
4. **Configurar alertas de monitoramento**

---

## 🛠️ Desenvolvimento e Testes

### Setup Local

```bash
# Clonar repositório
git clone <repo-url>
cd optimizer_ai/

# Instalar dependências
pip install -r requirements.txt

# Executar localmente
python main.py
```

### Testes

```bash
# Teste básico de título
curl -X POST "http://localhost:8001/generate_title" \
  -H "Content-Type: application/json" \
  -d '{"text": "produto inovador"}'

# Teste básico de descrição
curl -X POST "http://localhost:8001/generate_description" \
  -H "Content-Type: application/json" \
  -d '{"text": "serviço de qualidade"}'

# Health check
curl http://localhost:8001/health
```

### Debug

```bash
# Logs detalhados
export LOG_LEVEL=debug
python main.py

# Verificar OpenAPI docs
# http://localhost:8001/docs
# http://localhost:8001/redoc
```

---

## 📞 Suporte e Manutenção

### Logs Estruturados

O serviço gera logs estruturados com:
- Timestamps
- Níveis de log
- Contexto da operação
- Detalhes de erro

### Monitoramento Recomendado

- **Métricas de resposta**: Latência, throughput
- **Métricas de erro**: Taxa de erro, tipos de erro
- **Métricas de recursos**: CPU, memória, rede
- **Métricas de negócio**: Títulos/descrições gerados

---

## 🎯 Roadmap

### Próximas Funcionalidades

- [ ] Integração com modelos GPT/LLM
- [ ] Cache inteligente de respostas
- [ ] Análise de sentimento
- [ ] A/B testing de variações
- [ ] Métricas de performance de copy

### Melhorias Técnicas

- [ ] Rate limiting avançado
- [ ] Autenticação JWT
- [ ] Métricas Prometheus
- [ ] Tracing distribuído
- [ ] Pipeline CI/CD

---

**Desenvolvido por Aluizio Renato**  
**Versão**: 1.0.0  
**Data**: 2024