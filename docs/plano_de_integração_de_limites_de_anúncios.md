# 📊 Plano de Integração de Limites de Gastos por Produto em Campanhas Publicitárias

## 📋 Sumário Executivo

Este documento apresenta o plano detalhado para implementação de um sistema de controle de gastos por produto nas campanhas publicitárias, integrando-se aos serviços existentes de automação (ACOS Service, Campaign Automation e Discount Campaign Scheduler).

---

## 🎯 Objetivo

Implementar um sistema robusto de controle de gastos publicitários por produto, permitindo:
- **Controle granular** de orçamento por item/categoria
- **Cálculo automático de markup** baseado na margem de lucro
- **Otimização inteligente** de campanhas com base em limites personalizados
- **Proteção contra gastos excessivos** em produtos de baixa margem

---

## 🧮 Metodologia de Cálculo de Markup

### Fórmula Base do Sistema

```
Limite de Gasto = (Margem de Lucro × Preço de Venda) × Fator de Agressividade

Onde:
- Margem de Lucro = (Preço de Venda - Custo do Produto) / Preço de Venda
- Fator de Agressividade = 0.1 a 0.8 (10% a 80% da margem)
```

### Componentes do Cálculo

#### 1. **Margem Bruta do Produto**
```python
margem_bruta = (preco_venda - custo_produto) / preco_venda
```

#### 2. **Limite Máximo de Gasto Diário**
```python
limite_diario = margem_bruta * preco_venda * fator_agressividade * volume_diario_esperado
```

#### 3. **Ajuste por Performance Histórica**
```python
ajuste_performance = limite_base * (1 + (roas_historico - 3.0) * 0.2)
```

### Estratégias de Markup por Categoria

| Categoria | Margem Típica | Fator Recomendado | Limite de ACOS |
|-----------|---------------|-------------------|-----------------|
| Eletrônicos | 15-25% | 0.3-0.5 | 5-12% |
| Moda | 40-60% | 0.4-0.6 | 15-35% |
| Casa & Jardim | 30-50% | 0.4-0.7 | 12-35% |
| Livros | 25-35% | 0.2-0.4 | 5-15% |
| Beleza | 45-65% | 0.5-0.8 | 20-50% |

---

## 💡 Exemplos Práticos

### Exemplo 1: Smartphone (Eletrônicos)
```
Produto: Smartphone XYZ
Preço de Venda: R$ 1.200,00
Custo do Produto: R$ 960,00
Margem Bruta: (1200 - 960) / 1200 = 20%
Fator de Agressividade: 0.4 (moderado)
Volume Diário Esperado: 5 unidades

Cálculo:
Limite Diário = 0.20 × 1200 × 0.4 × 5 = R$ 480,00
ACOS Máximo = 480 / (1200 × 5) = 8%
```

### Exemplo 2: Vestido Feminino (Moda)
```
Produto: Vestido Fashion ABC
Preço de Venda: R$ 150,00
Custo do Produto: R$ 60,00
Margem Bruta: (150 - 60) / 150 = 60%
Fator de Agressividade: 0.6 (agressivo)
Volume Diário Esperado: 10 unidades

Cálculo:
Limite Diário = 0.60 × 150 × 0.6 × 10 = R$ 540,00
ACOS Máximo = 540 / (150 × 10) = 36%
```

### Exemplo 3: Kit Ferramentas (Casa & Jardim)
```
Produto: Kit Ferramentas Pro
Preço de Venda: R$ 89,90
Custo do Produto: R$ 45,00
Margem Bruta: (89.90 - 45) / 89.90 = 50%
Fator de Agressividade: 0.5 (moderado-agressivo)
Volume Diário Esperado: 8 unidades

Cálculo:
Limite Diário = 0.50 × 89.90 × 0.5 × 8 = R$ 179,80
ACOS Máximo = 179.80 / (89.90 × 8) = 25%
```

---

## 🎪 Influência nas Campanhas Publicitárias

### 1. **Automação de Lances**
- **Redução automática** quando próximo do limite
- **Pausa temporária** ao atingir 90% do limite diário
- **Reativação inteligente** no próximo período

### 2. **Distribuição de Orçamento**
- **Priorização** de produtos com maior margem
- **Realocação dinâmica** entre campanhas
- **Otimização cross-selling** para produtos complementares

### 3. **Estratégias de Bidding**
```python
# Exemplo de ajuste automático de lance
if gasto_atual >= limite_diario * 0.8:
    novo_lance = lance_atual * 0.7  # Reduz 30%
elif gasto_atual <= limite_diario * 0.3:
    novo_lance = lance_atual * 1.2  # Aumenta 20%
```

### 4. **Segmentação de Campanhas**
- **Campanhas específicas** por faixa de margem
- **Horários otimizados** baseados em performance histórica
- **Geografias prioritárias** com melhor conversão

---

## 🚀 Benefícios Esperados

### Financeiros
- **Redução de 25-40%** nos gastos desnecessários
- **Aumento de 15-30%** na margem líquida das campanhas
- **ROI médio** melhorado em 35-50%
- **Previsibilidade** de custos publicitários

### Operacionais
- **Automação completa** do controle de gastos
- **Alertas proativos** antes de ultrapassar limites
- **Dashboards intuitivos** para monitoramento
- **Relatórios detalhados** de performance por produto

### Estratégicos
- **Competitividade** mantida em produtos-chave
- **Escalabilidade** para milhares de produtos
- **Flexibilidade** para ajustes sazonais
- **Integração** com sistemas existentes

---

## 🛣️ Roadmap de Implementação

### **Fase 1: Fundação (Semanas 1-2)**
- [ ] **Análise de Dados Históricos**
  - Levantamento de margens por produto/categoria
  - Análise de performance de campanhas existentes
  - Identificação de padrões de gastos

- [ ] **Modelagem de Dados**
  - Criação das tabelas de limites por produto
  - Estrutura de configurações por categoria
  - Histórico de ajustes e performance

- [ ] **API Base**
  - Endpoints para configuração de limites
  - Serviços de cálculo de markup
  - Validações e regras de negócio

### **Fase 2: Motor de Cálculo (Semanas 3-4)**
- [ ] **Algoritmo de Cálculo**
  - Implementação das fórmulas de markup
  - Sistema de fatores de agressividade
  - Ajustes por performance histórica

- [ ] **Integração com Serviços Existentes**
  - Conexão com ACOS Service (porta 8016)
  - Integração com Campaign Automation (porta 8014)
  - Sincronização com Discount Scheduler (porta 8015)

- [ ] **Testes Automatizados**
  - Testes unitários para cálculos
  - Testes de integração entre serviços
  - Simulações de cenários extremos

### **Fase 3: Automação Inteligente (Semanas 5-6)**
- [ ] **Sistema de Alertas**
  - Notificações por email/webhook
  - Alertas em tempo real no dashboard
  - Escalação automática para gerentes

- [ ] **Ações Automáticas**
  - Pausa automática de campanhas
  - Ajuste de lances em tempo real
  - Realocação de orçamento

- [ ] **Dashboard de Monitoramento**
  - Visão consolidada de todos os limites
  - Gráficos de performance vs limites
  - Relatórios executivos automatizados

### **Fase 4: Otimização e ML (Semanas 7-8)**
- [ ] **Machine Learning**
  - Previsão de performance por produto
  - Sugestões automáticas de limites
  - Detecção de anomalias

- [ ] **A/B Testing**
  - Testes de diferentes estratégias
  - Comparação de performance
  - Otimização contínua

- [ ] **API Avançada**
  - Endpoints para relatórios avançados
  - Webhooks para integrações externas
  - Cache inteligente para performance

---

## 🔧 Especificações Técnicas

### Modelo de Dados

```python
class ProductSpendLimit(Base):
    __tablename__ = "product_spend_limits"
    
    id = Column(Integer, primary_key=True)
    product_id = Column(String, nullable=False, index=True)
    category_id = Column(String, nullable=False)
    
    # Dados financeiros
    sale_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)
    margin_percentage = Column(Float, nullable=False)
    
    # Configurações de limite
    aggressiveness_factor = Column(Float, default=0.4)
    daily_limit = Column(Float, nullable=False)
    monthly_limit = Column(Float, nullable=False)
    
    # Controle
    is_active = Column(Boolean, default=True)
    auto_adjust = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### API Endpoints

```python
# Configuração de Limites
POST   /api/spend-limits/products/{product_id}
GET    /api/spend-limits/products/{product_id}
PUT    /api/spend-limits/products/{product_id}
DELETE /api/spend-limits/products/{product_id}

# Cálculos e Simulações
POST   /api/spend-limits/calculate
POST   /api/spend-limits/simulate
GET    /api/spend-limits/suggestions/{product_id}

# Monitoramento
GET    /api/spend-limits/status
GET    /api/spend-limits/alerts
GET    /api/spend-limits/reports/daily
GET    /api/spend-limits/reports/monthly

# Ações Automáticas
POST   /api/spend-limits/actions/pause-campaign
POST   /api/spend-limits/actions/adjust-bid
POST   /api/spend-limits/actions/reallocate-budget
```

### Integração com Serviços Existentes

#### ACOS Service Integration
```python
# Monitoramento automático via ACOS Service
acos_threshold = daily_limit / (sale_price * expected_daily_volume)
acos_rule = {
    "name": f"Limite Produto {product_id}",
    "threshold_value": acos_threshold,
    "action_type": "pause_campaign",
    "product_id": product_id
}
```

#### Campaign Automation Integration
```python
# Ajuste automático de campanhas
campaign_config = {
    "max_daily_budget": daily_limit,
    "bid_adjustment_factor": aggressiveness_factor,
    "auto_pause_threshold": daily_limit * 0.9
}
```

---

## 📊 Monitoramento e Alertas

### Métricas Chave
- **Gasto atual vs. Limite** (em tempo real)
- **ACOS por produto** vs. limite calculado
- **Margem líquida efetiva** após gastos publicitários
- **Eficiência de conversão** por produto

### Tipos de Alertas
1. **Crítico** (95% do limite): Pausa automática iminente
2. **Alto** (80% do limite): Redução automática de lances
3. **Médio** (60% do limite): Monitoramento intensificado
4. **Baixo** (30% do limite): Oportunidade de aumento

### Dashboard KPIs
```
┌─────────────────────────────────────┐
│ CONTROLE DE GASTOS POR PRODUTO      │
├─────────────────────────────────────┤
│ 📊 Produtos Monitorados: 1,247     │
│ 🎯 Dentro do Limite: 89%           │
│ ⚠️  Próximos do Limite: 8%          │
│ 🚫 Pausados por Limite: 3%         │
│                                     │
│ 💰 Economia Estimada: R$ 15,429    │
│ 📈 ROI Médio: +42%                 │
│ 🕐 Última Atualização: 14:23       │
└─────────────────────────────────────┘
```

---

## 🔄 Instruções de Integração

### 1. **Preparação do Ambiente**
```bash
# Clone e configure o ambiente
git clone [repository]
cd ml_project

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite as configurações necessárias
```

### 2. **Configuração do Banco de Dados**
```bash
# Execute migrações
alembic upgrade head

# Popule dados iniciais
python scripts/populate_spend_limits.py
```

### 3. **Configuração dos Serviços**
```bash
# Inicie todos os serviços
docker-compose up -d

# Verifique status
curl http://localhost:8016/health  # ACOS Service
curl http://localhost:8014/health  # Campaign Automation
curl http://localhost:8015/health  # Discount Scheduler
```

### 4. **Primeira Configuração**
```python
# Exemplo de configuração via API
import requests

# Configure limite para um produto
product_limit = {
    "product_id": "MLB123456789",
    "sale_price": 150.00,
    "cost_price": 60.00,
    "aggressiveness_factor": 0.5,
    "category_id": "fashion"
}

response = requests.post(
    "http://localhost:8017/api/spend-limits/products/MLB123456789",
    json=product_limit
)
```

### 5. **Monitoramento Inicial**
- Acesse o dashboard: `http://localhost:3000/spend-limits`
- Configure alertas: `http://localhost:3000/alerts`
- Visualize relatórios: `http://localhost:3000/reports`

---

## 🧪 Testes e Validação

### Cenários de Teste
1. **Produto Alto Volume, Baixa Margem**
2. **Produto Baixo Volume, Alta Margem**
3. **Campanha com Múltiplos Produtos**
4. **Situação de Pico de Tráfego**
5. **Falha de Comunicação entre Serviços**

### Métricas de Sucesso
- **99.5%** de uptime do sistema
- **< 100ms** tempo de resposta para cálculos
- **> 95%** precisão nas previsões de gasto
- **< 5%** de falsos positivos em alertas

---

## 📞 Suporte e Manutenção

### Contatos Técnicos
- **Desenvolvedor Principal**: Aluizio Renato
- **DevOps**: [email]
- **Suporte 24/7**: [email/slack]

### Documentação Adicional
- **API Reference**: `/docs/api-reference.md`
- **Troubleshooting**: `/docs/troubleshooting.md`
- **Performance Tuning**: `/docs/performance.md`

---

**Desenvolvido para Marketplace Automation** 🇧🇷

*Versão 1.0 - Dezembro 2024*