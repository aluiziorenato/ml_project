# 🚀 CI/CD Workflow - Documentação Completa

## 📋 Visão Geral

Este documento descreve o sistema completo de CI/CD (Integração Contínua/Deploy Contínuo) implementado para o ML Project. O workflow garante deploys seguros, rápidos e confiáveis através de uma pipeline automatizada robusta.

## 🏗️ Arquitetura do Workflow

### 📁 Estrutura de Arquivos

```
.github/
├── workflows/
│   ├── ci-cd.yml          # Pipeline principal de CI/CD
│   ├── security.yml       # Scanning de segurança
│   └── dependabot.yml     # Configuração do Dependabot
└── dependabot.yml         # Atualizações automáticas de dependências
```

### 🔄 Pipeline Principal (ci-cd.yml)

#### 1. **Lint Jobs** (Execução Paralela)
- `lint-backend` - Validação do código backend
- `lint-simulator-service` - Validação do serviço simulador
- `lint-learning-service` - Validação do serviço de aprendizado
- `lint-optimizer-ai` - Validação do otimizador AI
- `lint-discount-campaign-scheduler` - Validação do agendador de campanhas
- `lint-campaign-automation` - Validação da automação de campanhas
- `lint-tests` - Validação dos testes principais
- `lint-modules` - Validação dos módulos AI (matriz)

#### 2. **Test & Coverage Jobs** (Execução Paralela)
- `test-backend` - Testes unitários do backend
- `test-backend-integration` - Testes de integração com PostgreSQL
- `test-simulator-service` - Testes do serviço simulador
- `test-learning-service` - Testes do serviço de aprendizado
- `test-optimizer-ai` - Testes do otimizador AI
- `test-discount-campaign-scheduler` - Testes do agendador
- `test-campaign-automation` - Testes da automação de campanhas
- `test-modules` - Testes dos módulos AI (matriz)
- `test-main-tests` - Testes principais do projeto
- `test-frontend` - Testes unitários do frontend
- `test-frontend-cypress` - Testes E2E com Cypress

#### 3. **Security & Build** (Execução Sequencial)
- `security-scan` - Varredura de vulnerabilidades com Trivy
- `build-and-push` - Build e push das imagens Docker

#### 4. **Deploy & Notifications** (Execução Sequencial)
- `deploy-draft` - Deploy para ambiente de staging/desenvolvimento
- `deploy` - Deploy para produção com rollback automático
- `coverage-report` - Geração e upload de relatórios de cobertura
- `notifications` - Notificações multi-canal

## 🔒 Sistema de Segurança

### 🛡️ Scanning Automático (security.yml)

#### Tipos de Verificação:
1. **Vulnerabilidades de Dependências**
   - Safety: Verificação de vulnerabilidades conhecidas
   - Bandit: Análise de segurança do código Python
   - npm audit: Vulnerabilidades no frontend

2. **Varredura de Segredos**
   - TruffleHog: Detecção de credenciais expostas
   - Verificação histórica completa

3. **Segurança de Containers**
   - Trivy: Análise de vulnerabilidades em imagens Docker
   - Verificação de base images

4. **Análise de Código**
   - CodeQL: Análise estática de segurança
   - Detecção de padrões de código inseguro

### 🤖 Dependabot Automático

- **Atualizações Semanais**: Python (pip) e Node.js (npm)
- **Atualizações Mensais**: Docker e GitHub Actions
- **Revisão Automática**: PRs com labels e assignees
- **Controle de Limite**: Máximo de PRs por categoria

## 🚀 Processo de Deploy

### 🎯 Deploy Estratégico

#### Staging (develop/PR):
1. Build e testes automáticos
2. Deploy para ambiente de staging
3. Testes de integração
4. Comentário automático no PR

#### Produção (main/master):
1. **Pré-Deploy**:
   - Captura do estado atual
   - Backup de configurações
   - Preparação para rollback

2. **Deploy Execution**:
   - Deploy escalonado por serviço
   - Verificação de rollout
   - Monitoramento em tempo real

3. **Validação Pós-Deploy**:
   - Smoke tests automáticos
   - Testes de integração
   - Health checks abrangentes

4. **Rollback Automático**:
   - Ativado em caso de falha
   - Restauração do estado anterior
   - Notificações de emergência

### 🔄 Mecanismo de Rollback

```yaml
# Ativação automática em caso de:
- Falha no deploy
- Smoke tests falharam
- Health checks falharam
- Testes de integração falharam

# Processo de rollback:
1. Captura do estado atual
2. Reversão para versão anterior
3. Verificação da saúde do sistema
4. Notificações de alerta
```

## 📊 Monitoramento e Relatórios

### 📈 Coverage Reports
- **Codecov Integration**: Upload automático para todos os módulos
- **Artefatos HTML**: Relatórios interativos
- **Flags Específicos**: Por módulo/serviço
- **PR Comments**: Resumo automático da cobertura

### 🔍 Artefatos Gerados
- Relatórios de cobertura (HTML/XML)
- Logs de segurança (SARIF)
- Screenshots de testes E2E
- Documentação automática

## 📢 Sistema de Notificações

### 📱 Multi-Canal
1. **Slack**: Notificações detalhadas com status
2. **Microsoft Teams**: Cards adaptativos
3. **Email**: Relatórios completos
4. **GitHub Issues**: Criação automática em falhas

### 🚨 Alertas de Emergência
- **Deploy Failures**: Notificação imediata
- **Security Issues**: Alertas de alta prioridade
- **System Health**: Monitoramento contínuo

## ⚙️ Configuração e Secrets

### 🔐 Secrets Obrigatórios

| Secret | Descrição | Obrigatório |
|--------|-----------|-------------|
| `SECRET_KEY` | Chave secreta da aplicação | ✅ |
| `ML_CLIENT_ID` | Client ID da API do Mercado Livre | ✅ |
| `ML_CLIENT_SECRET` | Secret da API do Mercado Livre | ✅ |
| `DOCKER_USERNAME` | Usuário do Docker Hub | ✅ |
| `DOCKER_PASSWORD` | Senha do Docker Hub | ✅ |

### 📧 Secrets Opcionais

| Secret | Descrição | Uso |
|--------|-----------|-----|
| `SLACK_WEBHOOK_URL` | URL do webhook do Slack | Notificações |
| `TEAMS_WEBHOOK_URL` | URL do webhook do Teams | Notificações |
| `NOTIFICATION_EMAIL` | Email para notificações | Alertas |
| `SENTRY_DSN` | URL do Sentry para monitoramento | Observabilidade |
| `STAGING_URL` | URL do ambiente de staging | Testes |
| `PRODUCTION_URL` | URL do ambiente de produção | Validação |

### 🔧 Configuração Inicial

```bash
# 1. Configure os secrets no GitHub
gh secret set SECRET_KEY --body "your-secret-key"
gh secret set ML_CLIENT_ID --body "your-client-id"
gh secret set ML_CLIENT_SECRET --body "your-client-secret"
gh secret set DOCKER_USERNAME --body "your-docker-username"
gh secret set DOCKER_PASSWORD --body "your-docker-password"

# 2. Configure secrets opcionais para notificações
gh secret set SLACK_WEBHOOK_URL --body "your-slack-webhook"
gh secret set TEAMS_WEBHOOK_URL --body "your-teams-webhook"
gh secret set NOTIFICATION_EMAIL --body "your-email@company.com"
```

## 🎮 Como Usar

### 📝 Fluxo de Desenvolvimento

1. **Feature Development**:
   ```bash
   git checkout -b feature/nova-funcionalidade
   # Desenvolver feature
   git push origin feature/nova-funcionalidade
   # Criar PR para develop
   ```

2. **Testing em Staging**:
   - PR para `develop` → Deploy automático em staging
   - Testes E2E automáticos
   - Revisão de código

3. **Deploy em Produção**:
   ```bash
   git checkout main
   git merge develop
   git push origin main
   # Deploy automático em produção
   ```

### 🔍 Monitoramento

#### Acompanhar Deploys:
1. **GitHub Actions**: [Repository Actions](../../actions)
2. **Codecov**: [Coverage Dashboard](https://codecov.io/gh/aluiziorenato/ml_project)
3. **Security**: [Security Tab](../../security)

#### Logs e Debugging:
- **Workflow Logs**: Disponíveis por 90 dias
- **Artefatos**: Relatórios downloadáveis
- **GitHub Issues**: Criados automaticamente em falhas

## 🚨 Procedimentos de Emergência

### 🔥 Deploy Failure

1. **Verificação Imediata**:
   - Verificar se o rollback foi executado
   - Confirmar saúde dos serviços
   - Revisar logs de erro

2. **Investigação**:
   - Analisar logs do workflow
   - Identificar causa raiz
   - Verificar testes localmente

3. **Resolução**:
   - Corrigir problemas identificados
   - Executar testes completos
   - Re-deploy após validação

### 🔒 Security Alert

1. **Resposta Imediata**:
   - Revisar alertas de segurança
   - Priorizar vulnerabilidades críticas
   - Aplicar patches de emergência

2. **Mitigação**:
   - Atualizar dependências vulneráveis
   - Aplicar hotfixes se necessário
   - Documentar incidente

## 📊 Métricas e KPIs

### ⏱️ Performance Metrics
- **Tempo de Build**: ~15-25 minutos (total)
- **Tempo de Deploy**: ~5-10 minutos
- **Tempo de Rollback**: ~2-3 minutos
- **MTTR**: Mean Time To Recovery

### 📈 Quality Metrics
- **Code Coverage**: Meta de 80%+
- **Security Scan**: 0 vulnerabilidades críticas
- **Test Success Rate**: 95%+
- **Deploy Success Rate**: 98%+

## 🔄 Melhorias Contínuas

### 📅 Roadmap

#### Próximas Implementações:
- [ ] Blue/Green Deployment
- [ ] Canary Releases
- [ ] Automated Performance Testing
- [ ] Infrastructure as Code (Terraform)
- [ ] Multi-region Deployment
- [ ] Chaos Engineering Tests

#### Otimizações Planejadas:
- [ ] Cache de dependências avançado
- [ ] Paralelização de builds
- [ ] Otimização de imagens Docker
- [ ] Melhoria na coleta de métricas

## 📚 Recursos Adicionais

### 📖 Documentação Relacionada
- [Checklist de Testes](../checklist_testes.md)
- [Guia de Implementação](../ci-cd-workflow-improvements.md)
- [Exemplos e Scripts](../ci-cd-examples-and-scripts.md)

### 🔗 Links Úteis
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Dependabot Configuration](https://docs.github.com/en/code-security/dependabot)

### 🆘 Suporte
- **Repository Issues**: [Criar Issue](../../issues/new)
- **Discussions**: [Discussões do Projeto](../../discussions)
- **Wiki**: [Documentação Detalhada](../../wiki)

---

**📅 Última Atualização**: $(date)  
**👨‍💻 Mantido por**: Equipe DevOps  
**🔄 Versão**: 2.0  
**📋 Status**: Ativo e em Produção