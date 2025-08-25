# 🚀 ML Project - Documentação Completa

## 📋 Visão Geral

O ML Project é uma plataforma abrangente de automação de vendas para o Mercado Livre, incorporando Machine Learning, AutoML e inteligência artificial para otimizar estratégias de vendas e maximizar resultados.

## 🏗️ Arquitetura do Sistema

### Componentes Principais

#### 1. **AutoML (Novidade!)**
- **Localização**: `/automl/`
- **Funcionalidades**:
  - Experimentação automatizada com `experiment.py`
  - Otimização de hiperparâmetros com `tuning.py` 
  - Tracking de experimentos com MLflow via `tracking.py`
  - Integração com múltiplos algoritmos de ML

#### 2. **Backend Core**
- **Localização**: `/backend/`
- **Tecnologia**: FastAPI + SQLAlchemy
- **Funcionalidades**: API REST, autenticação, persistência

#### 3. **Serviços Especializados**
- **Simulator Service**: Simulação de campanhas e previsões
- **Learning Service**: Aprendizado contínuo e retreinamento
- **Optimizer AI**: Otimização de textos e copywriting
- **Campaign Automation**: Automação de campanhas
- **Discount Scheduler**: Agendamento inteligente de descontos

#### 4. **Infraestrutura**
- **Docker**: Containerização completa
- **PostgreSQL**: Banco de dados principal
- **Redis**: Cache e sessões
- **MLflow**: Tracking de experimentos ML
- **Nginx**: Proxy reverso e load balancing

## 🚀 Quick Start

### Pré-requisitos
- Docker e Docker Compose
- Python 3.11+
- Git

### Instalação Rápida

```bash
# 1. Clonar o repositório
git clone <repository-url>
cd ml_project

# 2. Deploy com Docker
cd deploy
docker-compose up -d

# 3. Acessar aplicações
# Backend API: http://localhost:8000
# MLflow UI: http://localhost:5000
# Grafana: http://localhost:3001
# Jupyter: http://localhost:8888
```

### Instalação para Desenvolvimento

```bash
# 1. Instalar dependências do AutoML
cd automl
pip install -r requirements.txt

# 2. Instalar dependências do backend
cd ../backend
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# 4. Executar serviços
uvicorn backend.app.main:app --reload
```

## 🤖 AutoML - Guia Completo

### Experimentação Automatizada

```python
from automl.experiment import ExperimentManager

# Criar manager
manager = ExperimentManager("meu_experimento")

# Criar experimento
experiment_id = manager.create_experiment(
    name="Previsão de Vendas",
    description="Modelo para prever vendas baseado em características do produto",
    dataset_info={"shape": (1000, 10), "target": "vendas"}
)

# Executar experimento
results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=X_data,
    y=y_data,
    problem_type="regression"
)
```

### Otimização de Hiperparâmetros

```python
from automl.tuning import HyperparameterTuner
from sklearn.ensemble import RandomForestRegressor

# Criar tuner
tuner = HyperparameterTuner()

# Otimizar modelo
model = RandomForestRegressor(random_state=42)
results = tuner.auto_tune_model(
    model=model,
    model_type="random_forest_regressor",
    X=X_data,
    y=y_data,
    method="random_search"
)
```

### Tracking com MLflow

```python
from automl.tracking import create_tracker

# Criar tracker
tracker = create_tracker("meus_experimentos")

# Rastrear experimento
run_id = tracker.track_automl_experiment(
    experiment_results=results,
    dataset_info=dataset_info
)
```

## 📊 Exemplos Práticos

### Análise de Concorrência
- **Notebook**: `/examples/concorrencia_exemplo.ipynb`
- **Objetivo**: Analisar dados de concorrentes e otimizar preços
- **Dados**: Dataset simulado com 1000+ produtos
- **Modelos**: Random Forest, Linear Regression
- **Saídas**: Insights acionáveis e recomendações

### Casos de Uso Comuns

1. **Precificação Dinâmica**
   ```python
   # Usar AutoML para determinar preço ótimo
   price_model = manager.run_basic_experiment(
       experiment_id="price_optimization",
       X=product_features,
       y=optimal_prices,
       problem_type="regression"
   )
   ```

2. **Previsão de Demanda**
   ```python
   # Prever demanda futura
   demand_model = tuner.auto_tune_model(
       model=XGBRegressor(),
       model_type="gradient_boosting",
       X=historical_data,
       y=demand_data
   )
   ```

3. **Segmentação de Clientes**
   ```python
   # Clustering automático
   clustering_results = manager.run_basic_experiment(
       experiment_id="customer_segmentation",
       X=customer_features,
       y=None,  # Unsupervised
       problem_type="clustering"
   )
   ```

## 🐳 Deploy e Produção

### Ambiente de Produção

```bash
# Deploy completo com monitoramento
cd deploy
docker-compose -f docker-compose.yaml up -d

# Verificar status
docker-compose ps
docker-compose logs backend
```

### Configurações de Produção

#### Variáveis de Ambiente Críticas
```env
# Segurança
SECRET_KEY=your-super-secret-key-here
ML_CLIENT_ID=your-mercado-livre-client-id
ML_CLIENT_SECRET=your-mercado-livre-client-secret

# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/ml_db
REDIS_URL=redis://db:6379

# MLflow
MLFLOW_TRACKING_URI=postgresql+psycopg2://postgres:postgres@db:5432/ml_db

# Email (para alertas)
SMTP_SERVER=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### Monitoramento
- **Prometheus**: Métricas de sistema e aplicação
- **Grafana**: Dashboards visuais
- **Health Checks**: Endpoints `/health` em todos os serviços
- **Logs**: Estruturados e centralizados

## 🔧 Configuração Avançada

### MLflow Tracking Server

```bash
# Configurar MLflow com PostgreSQL
mlflow server \
  --backend-store-uri postgresql+psycopg2://postgres:postgres@db:5432/ml_db \
  --default-artifact-root /path/to/artifacts \
  --host 0.0.0.0 \
  --port 5000
```

### Escalabilidade

#### Kubernetes (Futuro)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-project-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ml-project-backend
  template:
    metadata:
      labels:
        app: ml-project-backend
    spec:
      containers:
      - name: backend
        image: ml-project/backend:latest
        ports:
        - containerPort: 8000
```

## 📈 Monitoramento e Métricas

### Métricas Principais
- **Experimentos**: Taxa de sucesso, tempo de execução
- **Modelos**: Accuracy, precision, recall, F1-score
- **Sistema**: CPU, memória, rede, disco
- **Negócio**: ROI, conversões, vendas

### Alertas Configurados
- Falha em experimentos críticos
- Performance de modelo abaixo do threshold
- Recursos de sistema em limite
- Erro em APIs externas

## 🔒 Segurança

### Práticas Implementadas
- **Autenticação**: JWT tokens
- **Autorização**: RBAC (Role-Based Access Control)
- **Criptografia**: Dados sensíveis em repouso
- **HTTPS**: TLS 1.3 em produção
- **Rate Limiting**: Proteção contra abuso
- **Input Validation**: Sanitização de dados

### Compliance
- **LGPD**: Proteção de dados pessoais
- **SOC 2**: Controles de segurança
- **ISO 27001**: Gestão de segurança da informação

## 🔄 CI/CD

### Pipeline Automatizado
1. **Lint**: Verificação de código
2. **Test**: Testes unitários e integração
3. **Security**: Scan de vulnerabilidades
4. **Build**: Criação de imagens Docker
5. **Deploy**: Deploy automatizado

### Configuração GitHub Actions
```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run AutoML tests
        run: |
          cd automl
          pip install -r requirements.txt
          python -m pytest tests/
```

## 🧪 Testes

### Estrutura de Testes
- **Unitários**: `/tests/test_*.py`
- **Integração**: `/tests/test_integration.py`
- **E2E**: `/tests/test_e2e_*.py`
- **AutoML**: `/tests/test_experiment.py`

### Executar Testes
```bash
# Todos os testes
pytest tests/

# Apenas AutoML
pytest tests/test_experiment.py

# Com coverage
pytest --cov=automl tests/
```

## 📚 API Reference

### AutoML Endpoints

#### Experimentos
- `POST /api/automl/experiments` - Criar experimento
- `GET /api/automl/experiments/{id}` - Obter experimento
- `GET /api/automl/experiments` - Listar experimentos

#### Modelos
- `POST /api/automl/models/train` - Treinar modelo
- `POST /api/automl/models/predict` - Fazer predição
- `GET /api/automl/models/{id}/metrics` - Métricas do modelo

#### Tracking
- `GET /api/automl/tracking/runs` - Listar runs
- `GET /api/automl/tracking/experiments` - Listar experimentos
- `POST /api/automl/tracking/compare` - Comparar runs

## 🔮 Roadmap Futuro

### Próximas Funcionalidades
1. **AutoML Avançado**: Neural Architecture Search (NAS)
2. **Deep Learning**: Integração com PyTorch/TensorFlow
3. **Real-time ML**: Streaming ML com Kafka
4. **Explainable AI**: SHAP, LIME integration
5. **Multi-tenant**: Suporte a múltiplos clientes

### Melhorias Planejadas
- **Performance**: Caching inteligente
- **UX**: Interface web para AutoML
- **Automação**: Auto-deployment de modelos
- **Integração**: Mais marketplaces

## 🆘 Troubleshooting

### Problemas Comuns

#### MLflow não inicia
```bash
# Verificar logs
docker-compose logs mlflow

# Resetar banco
docker-compose down -v
docker-compose up -d postgres
docker-compose up -d mlflow
```

#### Experimentos falham
```bash
# Verificar dependências
pip install -r automl/requirements.txt

# Verificar logs
tail -f automl_results/experiment_*.log
```

#### Performance lenta
```bash
# Verificar recursos
docker stats

# Otimizar parâmetros
# Reduzir n_iter em hyperparameter tuning
# Usar cv=3 em vez de cv=5
```

## 📞 Suporte

### Canais de Suporte
- **Issues**: GitHub Issues para bugs
- **Discussions**: GitHub Discussions para dúvidas
- **Email**: support@mlproject.com
- **Slack**: #ml-project-support

### Contribuição
1. Fork o repositório
2. Crie uma branch feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

---

**Desenvolvido pela ML Project Team** 🚀  
**Versão**: 2.0  
**Última atualização**: Dezembro 2024