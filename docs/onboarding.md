# 🎯 Onboarding - ML Project

Bem-vindo ao ML Project! Este guia irá ajudá-lo a começar rapidamente e se tornar produtivo em nossa plataforma de AutoML.

## 📚 Índice
1. [Configuração Inicial](#-configuração-inicial)
2. [Primeiro Experimento](#-primeiro-experimento)
3. [Conceitos Fundamentais](#-conceitos-fundamentais)
4. [Fluxos de Trabalho](#-fluxos-de-trabalho)
5. [Exemplos Práticos](#-exemplos-práticos)
6. [Melhores Práticas](#-melhores-práticas)
7. [Recursos Avançados](#-recursos-avançados)

## 🚀 Configuração Inicial

### Passo 1: Ambiente de Desenvolvimento

```bash
# Clonar repositório
git clone <repository-url>
cd ml_project

# Opção A: Docker (Recomendado)
cd deploy
docker-compose up -d

# Opção B: Instalação Local
pip install -r automl/requirements.txt
pip install -r backend/requirements.txt
```

### Passo 2: Verificar Instalação

```bash
# Verificar serviços Docker
docker-compose ps

# Acessar interfaces
# Backend: http://localhost:8000
# MLflow: http://localhost:5000
# Jupyter: http://localhost:8888
```

### Passo 3: Configuração Básica

```bash
# Copiar configurações
cp backend/.env.example backend/.env

# Editar variáveis essenciais
vim backend/.env
```

```env
# Configurações mínimas
SECRET_KEY=dev-secret-key-change-in-production
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/ml_db
MLFLOW_TRACKING_URI=http://localhost:5000
```

### Passo 4: Validar Instalação

#### 4.1 Teste de Conexão com Banco

Use o script de diagnóstico para verificar a conexão:

```bash
cd backend

# Teste básico de conexão
python scripts/check_db.py

# Teste completo com CRUD
python scripts/check_db.py --test-crud --verbose
```

#### 4.2 Executar Testes Automatizados

Valide a instalação executando os testes automatizados:

```bash
# Opção A: Com Docker (recomendado)
docker-compose up -d db
docker-compose exec backend pytest -v

# Opção B: Localmente
cd backend
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ml_db
pytest -v

# Verificar cobertura de testes
docker-compose exec backend pytest --cov=app --cov-report=term-missing
```

#### 4.3 Validar Logs de Inicialização

```bash
# Ver logs do backend
docker-compose logs backend

# Verificar se há erros
docker-compose logs backend | grep -i "error\|exception"

# Logs esperados (sucesso):
# ✅ Database connection established
# ✅ Created default admin user: admin@example.com
# ✅ Application startup complete
```

#### 4.4 Teste Manual com psql

```bash
# Conectar ao banco via Docker
docker-compose exec db psql -U postgres -d ml_db

# Ou localmente
psql -h localhost -U postgres -d ml_db

# Comandos de teste:
\l              # Listar bancos
\dt             # Listar tabelas
SELECT 1;       # Teste básico
\q              # Sair
```

#### ✅ Checklist de Validação

- [ ] Script `check_db.py` executa sem erros
- [ ] Conexão com PostgreSQL estabelecida
- [ ] Testes automatizados passam (`pytest -v`)
- [ ] Logs de inicialização sem erros críticos
- [ ] Usuário admin criado automaticamente
- [ ] Variáveis de ambiente configuradas

**Nota**: Use host `@db:5432` para Docker e `@localhost:5432` para desenvolvimento local. Certifique-se de que o serviço de banco está rodando antes de executar os testes.

## 🧪 Primeiro Experimento

### Hello World AutoML

Abra o Jupyter Notebook em `http://localhost:8888` e execute:

```python
# 1. Importar bibliotecas
import sys
sys.path.append('/app')

from automl.experiment import ExperimentManager
from sklearn.datasets import make_classification
import numpy as np

# 2. Criar dados de exemplo
X, y = make_classification(
    n_samples=500, 
    n_features=10, 
    n_informative=5,
    random_state=42
)

# 3. Inicializar experimento
manager = ExperimentManager("meu_primeiro_experimento")

# 4. Criar experimento
experiment_id = manager.create_experiment(
    name="Hello World AutoML",
    description="Meu primeiro experimento com AutoML",
    dataset_info={
        "shape": X.shape,
        "features": 10,
        "target": "classificação_binária"
    }
)

# 5. Executar AutoML
results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=X,
    y=y,
    problem_type="classification"
)

# 6. Ver resultados
print(f"✅ Experimento concluído!")
print(f"🏆 Melhor modelo: {results['best_model']}")
print(f"📊 Accuracy: {results['best_score']:.4f}")
```

**Parabéns! 🎉** Você executou seu primeiro experimento AutoML!

## 🔧 Conceitos Fundamentais

### 1. Experiment Manager
Gerencia todo o ciclo de vida dos experimentos ML:

```python
manager = ExperimentManager("projeto_vendas")

# Criar experimento
exp_id = manager.create_experiment(
    name="Previsão de Vendas Q4",
    description="Modelo para prever vendas do 4º trimestre",
    dataset_info={"fonte": "vendas_historicas.csv"}
)

# Executar múltiplos experimentos
for algorithm in ["classification", "regression"]:
    results = manager.run_basic_experiment(
        experiment_id=exp_id,
        X=X_data,
        y=y_data,
        problem_type=algorithm
    )
```

### 2. Hyperparameter Tuner
Otimiza automaticamente os parâmetros dos modelos:

```python
from automl.tuning import HyperparameterTuner

tuner = HyperparameterTuner()

# Comparar métodos de otimização
comparison = tuner.compare_tuning_methods(
    model=RandomForestClassifier(),
    model_type="random_forest_classifier",
    X=X_data,
    y=y_data
)

print(f"Melhor método: {comparison['best_method']}")
```

### 3. MLflow Tracker
Rastrea e versiona experimentos:

```python
from automl.tracking import create_tracker

tracker = create_tracker("vendas_q4")

# Rastrear experimento automaticamente
run_id = tracker.track_automl_experiment(
    experiment_results=results,
    model=trained_model,
    dataset_info=dataset_info
)

# Comparar múltiplos runs
comparison_df = tracker.compare_runs(
    run_ids=[run1, run2, run3],
    metrics=["accuracy", "precision", "recall"]
)
```

## 🔄 Fluxos de Trabalho

### Fluxo Básico: Classificação

```python
# 1. Preparar dados
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 2. Configurar experimento
manager = ExperimentManager("classificacao_clientes")
experiment_id = manager.create_experiment(
    name="Classificação de Clientes Premium",
    description="Identificar clientes com alto potencial de compra",
    dataset_info={
        "samples": len(X),
        "features": X.shape[1],
        "classes": len(np.unique(y))
    }
)

# 3. AutoML
results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=X_train,
    y=y_train,
    problem_type="classification"
)

# 4. Otimizar melhor modelo
from sklearn.ensemble import RandomForestClassifier
best_model = RandomForestClassifier(random_state=42)

tuning_results = tuner.auto_tune_model(
    model=best_model,
    model_type="random_forest_classifier",
    X=X_train,
    y=y_train,
    method="random_search"
)

# 5. Tracking
tracker = create_tracker("classificacao_clientes")
run_id = tracker.track_automl_experiment(results)
tuning_run_id = tracker.track_hyperparameter_tuning(tuning_results)

# 6. Relatório
report = manager.generate_experiment_report(experiment_id)
print(report)
```

### Fluxo Avançado: Regressão com Validação

```python
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_squared_error, r2_score

# 1. Experimento de regressão
manager = ExperimentManager("previsao_precos")
experiment_id = manager.create_experiment(
    name="Previsão de Preços Ótimos",
    description="Modelo para determinar preço ideal baseado em características do produto",
    dataset_info={
        "target": "preco_otimo",
        "features": ["categoria", "concorrencia", "demanda", "sazonalidade"]
    }
)

# 2. Executar com validação cruzada
results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=features_numericas,
    y=precos_target,
    problem_type="regression"
)

# 3. Validação adicional
best_model_name = results['best_model']
if best_model_name == "random_forest":
    from sklearn.ensemble import RandomForestRegressor
    model = RandomForestRegressor(random_state=42)
else:
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()

# Cross-validation
cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
print(f"R² médio: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# 4. Modelo final
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

# Métricas finais
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MSE: {mse:.4f}")
print(f"R²: {r2:.4f}")
```

## 💡 Exemplos Práticos

### Exemplo 1: Análise de Concorrência

```python
# Abrir o notebook de exemplo
# /examples/concorrencia_exemplo.ipynb

# Este notebook demonstra:
# - Análise exploratória de dados de concorrentes
# - Previsão de vendas com AutoML
# - Otimização de preços
# - Geração de insights acionáveis
```

### Exemplo 2: Previsão de Demanda Sazonal

```python
import pandas as pd
from datetime import datetime, timedelta

# Gerar dados de demanda sazonal
dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
np.random.seed(42)

# Simular sazonalidade
seasonal_demand = []
for date in dates:
    base_demand = 100
    # Maior demanda no verão e natal
    seasonal_factor = 1 + 0.3 * np.sin(2 * np.pi * date.dayofyear / 365)
    # Picos no fim de semana
    weekend_factor = 1.2 if date.weekday() >= 5 else 1.0
    # Ruído
    noise = np.random.normal(0, 0.1)
    
    demand = base_demand * seasonal_factor * weekend_factor * (1 + noise)
    seasonal_demand.append(max(0, demand))

# Criar features temporais
demand_df = pd.DataFrame({
    'date': dates,
    'demand': seasonal_demand
})

demand_df['dayofweek'] = demand_df['date'].dt.dayofweek
demand_df['dayofyear'] = demand_df['date'].dt.dayofyear
demand_df['month'] = demand_df['date'].dt.month
demand_df['is_weekend'] = (demand_df['dayofweek'] >= 5).astype(int)

# Preparar dados para ML
features = ['dayofweek', 'dayofyear', 'month', 'is_weekend']
X = demand_df[features].values
y = demand_df['demand'].values

# Experimento AutoML
manager = ExperimentManager("demanda_sazonal")
experiment_id = manager.create_experiment(
    name="Previsão de Demanda Sazonal",
    description="Modelo para prever demanda considerando sazonalidade",
    dataset_info={
        "periodo": "2023-2024",
        "frequencia": "diária",
        "features": features
    }
)

results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=X,
    y=y,
    problem_type="regression"
)

print(f"✅ Modelo de demanda criado!")
print(f"📊 Score: {results['best_score']:.4f}")
```

### Exemplo 3: Segmentação de Clientes

```python
# Gerar dados de clientes
np.random.seed(42)
n_customers = 1000

customers_data = pd.DataFrame({
    'customer_id': range(1, n_customers + 1),
    'age': np.random.randint(18, 80, n_customers),
    'income': np.random.lognormal(mean=10, sigma=0.5, size=n_customers),
    'purchases_last_30d': np.random.poisson(lam=3, size=n_customers),
    'avg_order_value': np.random.gamma(shape=2, scale=50, size=n_customers),
    'time_since_last_purchase': np.random.exponential(scale=15, size=n_customers),
    'total_lifetime_value': np.random.gamma(shape=3, scale=200, size=n_customers)
})

# Criar target baseado em regras de negócio
customers_data['is_premium'] = (
    (customers_data['income'] > customers_data['income'].quantile(0.7)) &
    (customers_data['total_lifetime_value'] > customers_data['total_lifetime_value'].quantile(0.8))
).astype(int)

# Features para clustering
features = ['age', 'income', 'purchases_last_30d', 'avg_order_value', 
           'time_since_last_purchase', 'total_lifetime_value']

X = customers_data[features].values
y = customers_data['is_premium'].values

# Experimento de classificação
manager = ExperimentManager("segmentacao_clientes")
experiment_id = manager.create_experiment(
    name="Segmentação de Clientes Premium",
    description="Identificar clientes premium para campanhas direcionadas",
    dataset_info={
        "clientes": n_customers,
        "features": features,
        "target": "is_premium"
    }
)

results = manager.run_basic_experiment(
    experiment_id=experiment_id,
    X=X,
    y=y,
    problem_type="classification"
)

print(f"✅ Modelo de segmentação criado!")
print(f"🎯 Accuracy: {results['best_score']:.4f}")

# Identificar clientes premium potenciais
if results['best_model'] == 'random_forest':
    from sklearn.ensemble import RandomForestClassifier
    final_model = RandomForestClassifier(random_state=42)
    final_model.fit(X, y)
    
    # Predições
    predictions = final_model.predict(X)
    probabilities = final_model.predict_proba(X)[:, 1]
    
    # Clientes com alta probabilidade de serem premium
    potential_premium = customers_data[
        (predictions == 1) & (probabilities > 0.8)
    ]['customer_id'].tolist()
    
    print(f"🌟 Identificados {len(potential_premium)} clientes premium potenciais")
```

## ✅ Melhores Práticas

### 1. Preparação de Dados

```python
# ✅ Bom: Preparação consistente
def prepare_data(df, target_column):
    """Preparar dados para AutoML"""
    # Remover valores nulos
    df_clean = df.dropna()
    
    # Separar features e target
    X = df_clean.drop(columns=[target_column])
    y = df_clean[target_column]
    
    # Encoding de variáveis categóricas
    from sklearn.preprocessing import LabelEncoder
    le = LabelEncoder()
    
    for col in X.select_dtypes(include=['object']).columns:
        X[col] = le.fit_transform(X[col].astype(str))
    
    return X.values, y.values

# ❌ Evitar: Preparação inconsistente
# X = df.drop('target')  # Sem tratamento de nulos
# y = df['target']      # Sem validação
```

### 2. Nomenclatura de Experimentos

```python
# ✅ Bom: Nomes descritivos
experiment_name = "vendas_q4_2024_random_forest_v2"
description = "Previsão de vendas Q4 2024 usando Random Forest com features de sazonalidade v2"

# ❌ Evitar: Nomes genéricos
experiment_name = "teste1"
description = "teste"
```

### 3. Documentação de Experimentos

```python
# ✅ Bom: Documentação completa
dataset_info = {
    "fonte": "vendas_historicas_2020_2024.csv",
    "shape": X.shape,
    "features": list(feature_names),
    "target": "vendas_mensais",
    "preprocessing": "StandardScaler + LabelEncoder",
    "train_period": "2020-01-01 to 2023-12-31",
    "test_period": "2024-01-01 to 2024-12-31",
    "business_context": "Previsão para planejamento de estoque Q1 2025"
}

# ❌ Evitar: Documentação mínima
dataset_info = {"shape": X.shape}
```

### 4. Versionamento de Modelos

```python
# ✅ Bom: Versionamento semântico
model_version = "vendas_v2.1.0"  # major.minor.patch
tags = {
    "version": model_version,
    "environment": "production",
    "data_version": "v2024.12",
    "algorithm": "random_forest"
}

tracker.start_run(run_name=f"model_{model_version}", tags=tags)

# ❌ Evitar: Sem versionamento
tracker.start_run(run_name="modelo")
```

### 5. Validação de Resultados

```python
# ✅ Bom: Validação robusta
from sklearn.model_selection import TimeSeriesSplit

# Para dados temporais
tscv = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X, y, cv=tscv, scoring='r2')

# Validar múltiplas métricas
from sklearn.metrics import classification_report, confusion_matrix

if problem_type == "classification":
    y_pred = model.predict(X_test)
    print(classification_report(y_test, y_pred))
    print(confusion_matrix(y_test, y_pred))

# ❌ Evitar: Validação única
score = model.score(X_test, y_test)  # Só uma métrica
```

## 🔬 Recursos Avançados

### 1. Pipeline Customizado

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# Pipeline customizado
custom_pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', RandomForestClassifier(random_state=42))
])

# Usar com AutoML
tuner = HyperparameterTuner()
custom_param_space = {
    'classifier__n_estimators': [50, 100, 200],
    'classifier__max_depth': [3, 5, 10, None]
}

# Otimizar pipeline completo
results = tuner.grid_search_tuning(
    model=custom_pipeline,
    X=X,
    y=y,
    param_grid=custom_param_space
)
```

### 2. Métricas Customizadas

```python
from sklearn.metrics import make_scorer

def business_metric(y_true, y_pred):
    """Métrica customizada baseada em regras de negócio"""
    # Penalizar mais falsos negativos (perder cliente premium)
    fp = ((y_pred == 1) & (y_true == 0)).sum()  # Falso positivo
    fn = ((y_pred == 0) & (y_true == 1)).sum()  # Falso negativo
    tp = ((y_pred == 1) & (y_true == 1)).sum()  # Verdadeiro positivo
    tn = ((y_pred == 0) & (y_true == 0)).sum()  # Verdadeiro negativo
    
    # Score customizado: penalizar FN 3x mais que FP
    score = (tp + tn) / (tp + tn + fp + 3*fn)
    return score

# Usar métrica customizada
custom_scorer = make_scorer(business_metric)
results = tuner.auto_tune_model(
    model=model,
    model_type="random_forest_classifier",
    X=X,
    y=y,
    scoring=custom_scorer
)
```

### 3. Feature Engineering Automatizado

```python
def auto_feature_engineering(df, target_column):
    """Feature engineering automatizado"""
    # Criar novas features
    df_enhanced = df.copy()
    
    # Features de interação
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for i, col1 in enumerate(numeric_cols):
        for col2 in numeric_cols[i+1:]:
            df_enhanced[f'{col1}_x_{col2}'] = df[col1] * df[col2]
    
    # Features agregadas
    for col in numeric_cols:
        if col != target_column:
            df_enhanced[f'{col}_rolling_mean_7d'] = df[col].rolling(7).mean()
            df_enhanced[f'{col}_rolling_std_7d'] = df[col].rolling(7).std()
    
    # Features temporais (se houver coluna de data)
    date_cols = df.select_dtypes(include=['datetime64']).columns
    for col in date_cols:
        df_enhanced[f'{col}_dayofweek'] = df[col].dt.dayofweek
        df_enhanced[f'{col}_month'] = df[col].dt.month
        df_enhanced[f'{col}_quarter'] = df[col].dt.quarter
    
    return df_enhanced

# Usar no pipeline
df_enhanced = auto_feature_engineering(df, 'target')
X_enhanced, y = prepare_data(df_enhanced, 'target')

# Experimento com features engineered
results = manager.run_basic_experiment(
    experiment_id="feature_engineering_experiment",
    X=X_enhanced,
    y=y,
    problem_type="classification"
)
```

## 🎓 Próximos Passos

### 1. Explorar Notebooks de Exemplo
- `examples/concorrencia_exemplo.ipynb` - Análise de concorrência completa
- Crie seus próprios notebooks baseados nos exemplos

### 2. Integrar com Sistemas Existentes
```python
# API endpoint para predições
@app.post("/predict")
async def predict(data: PredictionRequest):
    # Carregar modelo treinado
    model = load_trained_model(model_id="latest")
    
    # Fazer predição
    prediction = model.predict([data.features])
    
    return {"prediction": prediction[0]}
```

### 3. Configurar Alertas e Monitoramento
```python
# Configurar alertas para degradação de performance
def monitor_model_performance():
    recent_predictions = get_recent_predictions()
    current_accuracy = calculate_accuracy(recent_predictions)
    
    if current_accuracy < THRESHOLD:
        send_alert("Model performance degraded")
        trigger_retrain()
```

### 4. Automatizar Retreinamento
```python
# Scheduler para retreinamento automático
from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler()

@scheduler.scheduled_job('cron', day_of_week='mon', hour=2)
def weekly_retrain():
    # Carregar novos dados
    new_data = fetch_latest_data()
    
    # Retreinar modelo
    retrain_model(new_data)
    
    # Validar e promover para produção
    if validate_model():
        promote_to_production()

scheduler.start()
```

## 📋 Checklist de Onboarding

- [ ] ✅ Ambiente configurado (Docker ou local)
- [ ] ✅ Primeiro experimento executado com sucesso
- [ ] ✅ Jupyter Notebook funcionando
- [ ] ✅ MLflow UI acessível
- [ ] ✅ Notebook de concorrência executado
- [ ] ✅ Experimento customizado criado
- [ ] ✅ Tracking e versionamento configurados
- [ ] ✅ Documentação lida completamente
- [ ] ✅ Melhores práticas compreendidas
- [ ] ✅ Próximos passos definidos

## 🔧 Resolução de Problemas

### Problemas de Conexão com Banco

#### ❌ "Connection refused"
```bash
# Verificar se PostgreSQL está rodando
docker-compose ps db

# Se não estiver rodando, inicializar
docker-compose up -d db

# Para desenvolvimento local
systemctl status postgresql
sudo systemctl start postgresql  # se necessário
```

#### ❌ "Authentication failed"
```bash
# Verificar credenciais no .env
cat backend/.env | grep DATABASE_URL

# Padrão esperado:
# Docker: postgresql+psycopg2://postgres:postgres@db:5432/ml_db
# Local:  postgresql+psycopg2://postgres:postgres@localhost:5432/ml_db
```

#### ❌ "Database does not exist"
```bash
# Criar banco via Docker
docker-compose exec db createdb ml_db -U postgres

# Ou localmente
createdb ml_db -U postgres
```

### Problemas com Testes

#### ❌ Testes falhando com "No module named 'app'"
```bash
# Verificar se está no diretório correto
pwd  # Deve estar em /path/to/ml_project/backend

# Verificar PYTHONPATH
export PYTHONPATH=$PWD:$PYTHONPATH
```

#### ❌ "pydantic_settings not found"
```bash
# Instalar dependências
cd backend
pip install -r requirements.txt

# Ou via Docker
docker-compose exec backend pip install -r requirements.txt
```

### Problemas com Variáveis de Ambiente

#### ❌ Arquivo .env não encontrado
```bash
# Copiar exemplo
cd backend
cp .env.example .env

# Editar configurações
vim .env  # ou nano .env
```

#### ❌ Configurações não carregam
```bash
# Verificar se arquivo .env está no local correto
ls -la backend/.env

# Testar carregamento manual
cd backend
python -c "from app.settings import settings; print(settings.database_url)"
```

### Problemas com Docker

#### ❌ "Port already in use"
```bash
# Verificar portas em uso
netstat -tulpn | grep :5432  # PostgreSQL
netstat -tulpn | grep :8000  # Backend

# Parar outros serviços ou alterar portas no docker-compose.yml
```

#### ❌ "No space left on device"
```bash
# Limpar containers e imagens não utilizados
docker system prune -a

# Verificar espaço em disco
df -h
```

### ✅ Comandos de Diagnóstico Rápido

```bash
# 1. Verificar status dos serviços
docker-compose ps

# 2. Testar conexão com banco
cd backend && python scripts/check_db.py

# 3. Ver logs em tempo real
docker-compose logs -f backend

# 4. Testar aplicação
curl http://localhost:8000/health  # Se endpoint existir

# 5. Executar teste rápido
cd backend && python -c "from app.config import settings; print('✅ Config OK')"
```

## 🆘 Precisa de Ajuda?

### Problemas Comuns e Soluções

**Erro de import do automl:**
```bash
# Verificar path do Python
import sys
print(sys.path)

# Adicionar path correto
sys.path.append('/app')  # Para Docker
# ou
sys.path.append('/caminho/para/ml_project')  # Para instalação local
```

**MLflow não carrega:**
```bash
# Verificar se o serviço está rodando
docker-compose ps mlflow

# Reiniciar se necessário
docker-compose restart mlflow
```

**Jupyter não acessa arquivos:**
```bash
# Verificar volumes no docker-compose
docker-compose logs jupyter
```

### Canais de Suporte
- **GitHub Issues**: Para reportar bugs
- **GitHub Discussions**: Para dúvidas técnicas
- **Documentação**: `/docs/README.md` para referência completa

---

**Bem-vindo à equipe! 🚀**  
Agora você está pronto para criar modelos de ML de classe mundial com nosso sistema AutoML!

**Próximo passo**: Execute o notebook `examples/concorrencia_exemplo.ipynb` para ver o sistema em ação!