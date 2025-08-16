# 🎯 Sistema de Modo Estratégico e Campanhas para Datas Especiais

## 📋 Sumário Executivo

Este documento detalha a implementação do sistema de modo estratégico que permite ao usuário definir estratégias globais para campanhas publicitárias e adaptar automaticamente limites, ações, automações e relatórios conforme a escolha. O sistema inclui campanhas especializadas para datas especiais com automação inteligente.

---

## 🎯 Objetivo

Implementar um sistema robusto de estratégias globais que:
- **Permite escolha entre 4 modos estratégicos** (Maximizar Lucro, Escalar Vendas, Proteger Margem, Campanhas Agressivas)
- **Adapta automaticamente** limites, ações e automações baseado na estratégia escolhida
- **Integra com IA existente** (ACOS Service, Campaign Automation, Discount Scheduler)
- **Gerencia campanhas especiais** para datas comemorativas
- **Oferece dashboards visuais** e relatórios comparativos
- **Envia alertas multicanal** baseados na estratégia ativa

---

## 🚀 Modos Estratégicos

### 1. 💰 Maximizar Lucro
**Objetivo**: Focar na maximização da margem de lucro por venda

**Configurações Automáticas**:
- ACOS Target: 10-15% (conservador)
- Limites de gasto: 70% da margem bruta por produto
- Lances: Reduzidos em 20% para keywords de alta competição
- Pausar campanhas: Quando ACOS > 20%
- Prioridade: Produtos com margem > 40%

**Automações Ativadas**:
- Redução automática de lances quando ACOS > 15%
- Pausa de campanhas com ROI negativo
- Realocação de orçamento para produtos de alta margem
- Alertas quando margem < 35%

### 2. 📈 Escalar Vendas sem Prejuízo
**Objetivo**: Maximizar volume de vendas mantendo rentabilidade

**Configurações Automáticas**:
- ACOS Target: 15-25% (moderado)
- Limites de gasto: 85% da margem bruta por produto
- Lances: Aumentados em 15% para keywords com boa conversão
- Pausar campanhas: Quando ACOS > 30%
- Prioridade: Produtos com histórico de vendas consistente

**Automações Ativadas**:
- Aumento automático de orçamento para campanhas performantes
- Expansão de keywords baseada em IA
- Ativação de campanhas para produtos similares
- Alertas quando volume de vendas cai > 20%

### 3. 🛡️ Proteger Margem em Datas Especiais
**Objetivo**: Manter margem mesmo com aumento de competição

**Configurações Automáticas**:
- ACOS Target: 8-12% (muito conservador)
- Limites de gasto: 60% da margem bruta por produto
- Lances: Reduzidos em 30% durante datas especiais
- Pausar campanhas: Quando ACOS > 15%
- Prioridade: Produtos exclusivos ou com baixa concorrência

**Automações Ativadas**:
- Monitoramento intensivo de concorrentes
- Ajuste de preços baseado na demanda
- Pausa preventiva de campanhas em horários de pico
- Alertas quando margem < 25%

### 4. ⚡ Campanhas com Custo Agressivo
**Objetivo**: Conquistar market share através de investimento agressivo

**Configurações Automáticas**:
- ACOS Target: 25-40% (agressivo)
- Limites de gasto: 120% da margem bruta por produto
- Lances: Aumentados em 50% para keywords estratégicas
- Pausar campanhas: Quando ACOS > 50%
- Prioridade: Novos produtos ou entrada em novos mercados

**Automações Ativadas**:
- Lances máximos para posições top
- Ativação de todas as keywords sugeridas pela IA
- Campanhas 24/7 durante datas especiais
- Alertas quando posição média > 3

---

## 📅 Gestão de Datas Especiais

### Datas Pré-Configuradas
- **Black Friday** (Novembro)
- **Cyber Monday** (Novembro)
- **Natal** (Dezembro)
- **Ano Novo** (Janeiro)
- **Dia dos Namorados** (Junho)
- **Dia das Mães** (Maio)
- **Dia dos Pais** (Agosto)
- **Dia das Crianças** (Outubro)

### Configurações por Data
Cada data especial permite:
- **Período de ativação** (data início/fim)
- **Multiplicador de orçamento** (1.5x a 3.0x)
- **Ajuste de ACOS target** (+/- 10%)
- **Estratégia específica** (sobrescreve estratégia global)
- **Produtos prioritários** (categorias ou IDs específicos)
- **Horários de pico** (concentrar orçamento)

---

## 🔧 Integração com Serviços Existentes

### ACOS Service (Porta 8016)
**Adaptações por Estratégia**:
- Thresholds dinâmicos baseados no modo estratégico
- Ações automáticas personalizadas
- Alertas com severidade baseada na estratégia
- Cálculo de ACOS otimizado por produto

**Endpoints Integrados**:
```python
POST /acos/strategy/apply
GET /acos/strategy/status
PUT /acos/strategy/thresholds
```

### Campaign Automation Service (Porta 8014)
**Adaptações por Estratégia**:
- Automações de lance baseadas no modo
- Gestão de orçamento dinâmico
- Agendamento de campanhas para datas especiais
- Otimização de keywords por estratégia

**Endpoints Integrados**:
```python
POST /campaigns/strategy/configure
GET /campaigns/strategy/performance
PUT /campaigns/strategy/budgets
```

### Discount Campaign Scheduler (Porta 8015)
**Adaptações por Estratégia**:
- Sugestões de desconto baseadas no modo
- Agendamento automático para datas especiais
- Análise de impacto na margem
- Sincronização com estratégia global

**Endpoints Integrados**:
```python
POST /discounts/strategy/schedule
GET /discounts/strategy/suggestions
PUT /discounts/strategy/limits
```

---

## 🏗️ Arquitetura do Sistema

### Strategic Mode Service (Porta 8017)
**Responsabilidades**:
- Gerenciar configurações de estratégias
- Coordenar adaptações nos serviços
- Calcular limites dinâmicos
- Processar alertas multicanal
- Gerar relatórios comparativos

**Tecnologias**:
- FastAPI para API REST
- SQLAlchemy para persistência
- Celery para tarefas assíncronas
- Redis para cache e mensageria
- PostgreSQL para dados transacionais

### Banco de Dados

#### Tabela: strategic_modes
```sql
CREATE TABLE strategic_modes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    acos_min DECIMAL(5,2),
    acos_max DECIMAL(5,2),
    budget_multiplier DECIMAL(3,2),
    bid_adjustment DECIMAL(3,2),
    margin_threshold DECIMAL(5,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: special_dates
```sql
CREATE TABLE special_dates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    budget_multiplier DECIMAL(3,2),
    acos_adjustment DECIMAL(3,2),
    strategy_override INTEGER REFERENCES strategic_modes(id),
    peak_hours JSONB,
    priority_categories JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: strategy_configurations
```sql
CREATE TABLE strategy_configurations (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    active_strategy INTEGER REFERENCES strategic_modes(id),
    custom_settings JSONB,
    special_date_overrides JSONB,
    notification_channels JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

#### Tabela: strategy_performance_log
```sql
CREATE TABLE strategy_performance_log (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategic_modes(id),
    date DATE,
    total_spend DECIMAL(10,2),
    total_sales DECIMAL(10,2),
    average_acos DECIMAL(5,2),
    campaigns_count INTEGER,
    conversions INTEGER,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 📊 Dashboard e Interface

### 1. Tela de Configuração Estratégica
**Localização**: `/dashboard/strategy-config`

**Componentes**:
- Seletor de modo estratégico (4 opções)
- Preview de configurações automáticas
- Configuração de datas especiais
- Teste de cenários (simulação)
- Histórico de mudanças

**Funcionalidades**:
- Aplicação imediata ou agendada
- Validação de impacto financeiro
- Aprovação em duas etapas para mudanças críticas

### 2. Dashboard de Monitoramento Estratégico
**Localização**: `/dashboard/strategy-monitor`

**KPIs Principais**:
- ACOS atual vs target da estratégia
- Orçamento utilizado vs limite
- Performance vs estratégia anterior
- Alertas ativos por severidade
- ROI por modo estratégico

**Gráficos**:
- Timeline de performance por estratégia
- Comparativo mensal entre estratégias
- Heatmap de performance por categoria
- Mapa de correlação entre métricas

### 3. Relatórios Comparativos
**Localização**: `/dashboard/strategy-reports`

**Relatórios Disponíveis**:
- **Performance por Estratégia**: 30/60/90 dias
- **Análise de Datas Especiais**: ROI por evento
- **Benchmarking**: Comparação com períodos anteriores
- **Previsão de Performance**: IA predictive para próximos 30 dias
- **Análise de Impacto**: Antes/depois de mudanças

---

## 🔔 Sistema de Alertas Multicanal

### Canais de Notificação
1. **Dashboard Web**: Notificações em tempo real
2. **Email**: Resumos diários e alertas críticos
3. **Webhook**: Integração com sistemas externos
4. **Slack/Teams**: Alertas para equipes
5. **SMS**: Apenas para alertas críticos

### Tipos de Alertas por Estratégia

#### Maximizar Lucro
- ACOS > 20% (crítico)
- Margem < 35% (aviso)
- Campaign ROI negativo (crítico)
- Competitor price below cost (informativo)

#### Escalar Vendas
- Volume vendas -20% (crítico)
- ACOS > 30% (aviso)
- Budget 90% utilizado (informativo)
- New keyword opportunities (informativo)

#### Proteger Margem
- Margem < 25% (crítico)
- Competitor activity increase (aviso)
- Peak hour performance drop (informativo)
- ACOS > 15% (aviso)

#### Campanhas Agressivas
- Posição média > 3 (crítico)
- ACOS > 50% (aviso)
- Budget limit reached (informativo)
- Market share opportunity (informativo)

---

## 🤖 Automações Inteligentes

### Motor de Decisão
O sistema utiliza um motor de decisão baseado em regras e machine learning que:

1. **Analisa contexto atual** (estratégia, data, performance)
2. **Consulta serviços de IA** (predições, tendências)
3. **Aplica regras da estratégia** (limites, thresholds)
4. **Executa ações automáticas** (ajustes, pausas, alertas)
5. **Registra resultados** (logs, métricas, feedback)

### Ações Automáticas por Estratégia

```python
# Exemplo de configuração de automação
STRATEGY_AUTOMATIONS = {
    "maximize_profit": {
        "bid_adjustment": {"acos_threshold": 15, "action": "decrease", "percent": 10},
        "campaign_pause": {"acos_threshold": 20, "action": "pause"},
        "budget_reallocation": {"roi_threshold": 1.5, "action": "increase_budget"}
    },
    "scale_sales": {
        "bid_adjustment": {"conversion_rate": 0.05, "action": "increase", "percent": 15},
        "keyword_expansion": {"performance_score": 8, "action": "expand"},
        "budget_increase": {"sales_growth": 0.2, "action": "increase_budget"}
    }
}
```

---

## 🧪 Testes e Validação

### Cenários de Teste

#### 1. Teste de Mudança de Estratégia
```python
def test_strategy_change():
    # Aplicar estratégia "Maximizar Lucro"
    # Verificar ajustes em ACOS service
    # Verificar ajustes em Campaign Automation
    # Verificar alertas configurados
    # Verificar dashboard atualizado
```

#### 2. Teste de Data Especial
```python
def test_special_date_activation():
    # Configurar Black Friday
    # Verificar multiplicador de orçamento aplicado
    # Verificar ajustes de ACOS para a data
    # Verificar produtos prioritários ativados
    # Verificar alertas específicos
```

#### 3. Teste de Automação
```python
def test_automated_actions():
    # Simular ACOS alto
    # Verificar ação automática baseada na estratégia
    # Verificar integração com serviços
    # Verificar logs de ações
    # Verificar alertas enviados
```

### Métricas de Sucesso
- **99.5%** de uptime do strategic mode service
- **< 200ms** tempo de resposta para mudanças de estratégia
- **> 95%** precisão nas automações
- **< 3%** de falsos positivos em alertas
- **> 90%** satisfação do usuário

---

## 🔄 Integração com Frontend

### Componentes React

#### StrategySelector.jsx
```jsx
const StrategySelector = () => {
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [impact, setImpact] = useState(null);
  
  return (
    <div className="strategy-selector">
      <StrategyCards 
        strategies={strategies} 
        selected={selectedStrategy}
        onChange={handleStrategyChange}
      />
      <ImpactPreview impact={impact} />
      <ActionButtons onApply={applyStrategy} />
    </div>
  );
};
```

#### SpecialDatesCalendar.jsx
```jsx
const SpecialDatesCalendar = () => {
  const [dates, setDates] = useState([]);
  const [selectedDate, setSelectedDate] = useState(null);
  
  return (
    <Calendar
      events={specialDates}
      onEventClick={handleDateConfig}
      renderEvent={SpecialDateCard}
    />
  );
};
```

#### StrategyDashboard.jsx
```jsx
const StrategyDashboard = () => {
  const [kpis, setKpis] = useState({});
  const [alerts, setAlerts] = useState([]);
  
  return (
    <DashboardLayout>
      <KPIGrid kpis={kpis} />
      <AlertsPanel alerts={alerts} />
      <PerformanceCharts />
      <RecentActions />
    </DashboardLayout>
  );
};
```

---

## 📈 Roadmap de Implementação

### **Fase 1: Infraestrutura Base (Semanas 1-2)**
- [x] Análise e planejamento
- [ ] **Strategic Mode Service** básico
- [ ] **Banco de dados** e modelos
- [ ] **Endpoints** principais da API
- [ ] **Integração** com serviços existentes

### **Fase 2: Modos Estratégicos (Semanas 3-4)**
- [ ] **Implementação** dos 4 modos estratégicos
- [ ] **Motor de decisão** e automações
- [ ] **Adaptação** dos serviços ACOS, Campaign, Discount
- [ ] **Testes** de integração básicos

### **Fase 3: Datas Especiais (Semanas 5-6)**
- [ ] **Sistema** de datas especiais
- [ ] **Configuração** de períodos e overrides
- [ ] **Automação** específica para eventos
- [ ] **Calendário** e agendamento

### **Fase 4: Frontend e UX (Semanas 7-8)**
- [ ] **Telas** de configuração estratégica
- [ ] **Dashboard** de monitoramento
- [ ] **Relatórios** comparativos
- [ ] **Sistema** de alertas visuais

### **Fase 5: Alertas e Monitoramento (Semanas 9-10)**
- [ ] **Sistema** de alertas multicanal
- [ ] **Configuração** de notificações
- [ ] **Dashboard** de alertas
- [ ] **Escalação** automática

### **Fase 6: Otimização e Testes (Semanas 11-12)**
- [ ] **Testes** automatizados completos
- [ ] **Otimização** de performance
- [ ] **Documentação** técnica
- [ ] **Validação** com usuários

---

## 🔧 Configuração e Deploy

### Variáveis de Ambiente
```env
# Strategic Mode Service
STRATEGIC_MODE_SERVICE_PORT=8017
STRATEGIC_MODE_SECRET_KEY=strategic-mode-secret-key
STRATEGIC_MODE_DATABASE_URL=postgresql://user:pass@db:5432/strategic_db

# Integração com serviços
ACOS_SERVICE_URL=http://acos_service:8016
CAMPAIGN_SERVICE_URL=http://campaign_automation_service:8014
DISCOUNT_SERVICE_URL=http://discount_campaign_scheduler:8015

# Sistema de alertas
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@company.com
SMTP_PASS=password
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
TEAMS_WEBHOOK_URL=https://outlook.office.com/...

# Configurações de automação
AUTO_APPLY_CHANGES=true
SIMULATION_MODE=false
MAX_BUDGET_INCREASE=200
MIN_MARGIN_THRESHOLD=15
```

### Docker Compose Addition
```yaml
strategic_mode_service:
  build:
    context: ./strategic_mode_service
    dockerfile: Dockerfile
  restart: unless-stopped
  environment:
    DATABASE_URL: postgresql://usuario:senha@db:5432/nome_do_banco
    REDIS_URL: redis://redis:6379/16
    ACOS_SERVICE_URL: http://acos_service:8016
    CAMPAIGN_SERVICE_URL: http://campaign_automation_service:8014
    DISCOUNT_SERVICE_URL: http://discount_campaign_scheduler:8015
    SECRET_KEY: strategic-mode-secret-key-change-in-production
  ports:
    - "8017:8017"
  depends_on:
    - db
    - redis
    - acos_service
    - campaign_automation_service
    - discount_campaign_scheduler
  networks:
    - ml_network
```

---

## 📝 Observações Importantes

- **Segurança**: Todas as mudanças críticas requerem autenticação
- **Backup**: Configurações são automaticamente versionadas
- **Rollback**: Sistema permite reverter para estratégia anterior
- **Monitoramento**: Métricas detalhadas para cada componente
- **Escalabilidade**: Preparado para milhares de campanhas simultâneas
- **Compliance**: Logs auditáveis para todas as ações automáticas

**Desenvolvido para Marketplace Automation** 🇧🇷

---

*Este documento está em constante evolução conforme o desenvolvimento progride.*