# 🔐 Guia de Segurança e Gerenciamento de Secrets CI/CD

## 📋 Visão Geral

Este documento fornece orientações abrangentes sobre o uso seguro de secrets no pipeline CI/CD do ML Project, garantindo que informações sensíveis sejam protegidas e não expostas em logs ou outputs.

## 🛡️ Princípios de Segurança

### 1. **Mascaramento Automático de Logs**
- GitHub Actions automaticamente mascara valores de secrets nos logs
- Secrets nunca devem ser impressos diretamente com `echo` ou `printf`
- Use `${{ secrets.NAME }}` apenas em contextos seguros

### 2. **Princípio do Menor Privilégio**
- Cada secret tem acesso apenas aos recursos necessários
- Separação clara entre ambientes (staging/production)
- Validação de autorização antes de operações críticas

### 3. **Monitoramento e Auditoria**
- Logs de auditoria para todas as operações com secrets
- Alertas para falhas de autenticação
- Revisões regulares de acesso e uso

## 🔑 Secrets Configurados

### 🚨 Secrets Obrigatórios

| Secret | Descrição | Ambiente | Validação |
|--------|-----------|----------|-----------|
| `SECRET_KEY` | Chave secreta da aplicação | Todos | ≥ 20 caracteres |
| `ML_CLIENT_ID` | Client ID da API do Mercado Livre | Todos | Formato UUID |
| `ML_CLIENT_SECRET` | Secret da API do Mercado Livre | Todos | ≥ 32 caracteres |
| `DOCKER_USERNAME` | Usuário do Docker Hub | Todos | String válida |
| `DOCKER_PASSWORD` | Senha do Docker Hub | Todos | ≥ 8 caracteres |
| `DEPLOY_TOKEN` | Token de autorização para deployment | Produção | ≥ 20 caracteres |
| `PROD_API_KEY` | Chave da API de produção | Produção | ≥ 32 caracteres |

### 📧 Secrets Opcionais

| Secret | Descrição | Uso | Formato |
|--------|-----------|-----|---------|
| `SLACK_WEBHOOK_URL` | URL do webhook do Slack | Notificações | URL HTTPS |
| `TEAMS_WEBHOOK_URL` | URL do webhook do Teams | Notificações | URL HTTPS |
| `NOTIFICATION_EMAIL` | Email para alertas | Notificações | Email válido |
| `SENTRY_DSN` | URL do Sentry | Monitoramento | URL DSN |
| `STAGING_URL` | URL do ambiente de staging | Testes | URL HTTPS |
| `PRODUCTION_URL` | URL do ambiente de produção | Validação | URL HTTPS |

## 🔧 Configuração de Secrets

### Via GitHub CLI

```bash
# Secrets obrigatórios
gh secret set SECRET_KEY --body "sua-chave-secreta-complexa-min-20-chars"
gh secret set ML_CLIENT_ID --body "seu-client-id-mercado-livre"
gh secret set ML_CLIENT_SECRET --body "seu-client-secret-ml-min-32-chars"
gh secret set DOCKER_USERNAME --body "seu-usuario-docker"
gh secret set DOCKER_PASSWORD --body "sua-senha-docker-segura"

# 🔐 Novos secrets para deployment seguro
gh secret set DEPLOY_TOKEN --body "token-deploy-autorizado-min-20-chars"
gh secret set PROD_API_KEY --body "chave-api-producao-min-32-chars"

# Secrets opcionais
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/..."
gh secret set TEAMS_WEBHOOK_URL --body "https://outlook.office.com/webhook/..."
gh secret set NOTIFICATION_EMAIL --body "alerts@sua-empresa.com"
gh secret set SENTRY_DSN --body "https://abc123@sentry.io/123456"
gh secret set STAGING_URL --body "https://staging.sua-app.com"
gh secret set PRODUCTION_URL --body "https://producao.sua-app.com"
```

### Via Interface Web

1. Acesse: `Repositório > Settings > Secrets and variables > Actions`
2. Clique em "New repository secret"
3. Configure cada secret individualmente
4. Verifique que os valores não aparecem na interface após salvos

## 🛡️ Uso Seguro no Workflow

### ✅ Práticas Corretas

```yaml
# ✅ Uso seguro - secret é mascarado automaticamente
- name: Deploy com autenticação
  run: |
    curl -H "Authorization: Bearer ${{ secrets.DEPLOY_TOKEN }}" \
         -H "X-API-Key: ${{ secrets.PROD_API_KEY }}" \
         https://api.deployment.com/deploy

# ✅ Validação sem exposição
- name: Validar secret
  run: |
    if [ -z "${{ secrets.DEPLOY_TOKEN }}" ]; then
      echo "❌ DEPLOY_TOKEN não configurado"
      exit 1
    fi
    echo "✅ DEPLOY_TOKEN está configurado"
```

### ❌ Práticas Perigosas

```yaml
# ❌ NUNCA faça isso - expõe o secret no log
- name: Debug incorreto
  run: |
    echo "Token: ${{ secrets.DEPLOY_TOKEN }}"
    
# ❌ NUNCA salve secrets em arquivos
- name: Configuração incorreta
  run: |
    echo "${{ secrets.PROD_API_KEY }}" > config.txt
```

## 🔍 Validação e Monitoramento

### Script de Validação

O repositório inclui um script de validação automática:

```bash
# Executar validação local
./scripts/validate-secrets.sh

# Executar no CI/CD (automático)
# O script é executado automaticamente no job 'validate-secrets'
```

### Verificações Implementadas

1. **Presença de Secrets**: Verifica se todos os secrets obrigatórios estão configurados
2. **Comprimento Mínimo**: Valida que secrets críticos têm tamanho adequado
3. **Formato**: Verifica formato básico de URLs e emails
4. **Ambiente**: Confirma secrets específicos para produção

### Logs de Segurança

```yaml
# Exemplo de log seguro no workflow
echo "🔐 Usando DEPLOY_TOKEN para autenticação..."  # ✅ Seguro
echo "🔑 Token recebido: $(echo ${{ secrets.DEPLOY_TOKEN }} | wc -c) chars"  # ✅ Seguro
echo "✅ Autenticação realizada com sucesso"  # ✅ Seguro
```

## 🚨 Procedimentos de Emergência

### Compromisso de Secret

Se um secret for comprometido:

1. **Ação Imediata**:
   ```bash
   # Revogar/rotacionar o secret comprometido
   gh secret set SECRET_NAME --body "novo-valor-seguro"
   ```

2. **Investigação**:
   - Revisar logs de acesso
   - Identificar escopo do compromisso
   - Verificar impacto em sistemas

3. **Prevenção**:
   - Implementar rotação automática
   - Revisar políticas de acesso
   - Atualizar documentação

### Falha de Deployment

Em caso de falha relacionada a secrets:

1. **Verificar Logs**:
   ```bash
   # Verificar logs do workflow (sem secrets expostos)
   gh run list --limit 5
   gh run view <run-id> --log
   ```

2. **Validar Configuração**:
   ```bash
   # Executar validação de secrets
   ./scripts/validate-secrets.sh
   ```

3. **Rollback Automático**:
   - O workflow implementa rollback automático
   - Verificar que sistemas voltaram ao estado anterior
   - Investigar causa raiz

## 📊 Auditoria e Compliance

### Relatórios de Auditoria

O workflow gera automaticamente:

- ✅ Log de validação de secrets
- ✅ Confirmação de autorização de deployment
- ✅ Status de segurança de cada step
- ✅ Registro de uso de secrets por job

### Conformidade

- 🔒 **LGPD**: Dados pessoais protegidos via secrets
- 🛡️ **ISO 27001**: Controles de acesso implementados
- 📋 **SOC 2**: Logs de auditoria mantidos
- 🔐 **OWASP**: Melhores práticas de segurança aplicadas

## 🧪 Testando a Configuração

### Criar PR de Teste

```bash
# 1. Criar branch de teste
git checkout -b test-ci-cd-secrets-integration
git commit --allow-empty -m "test: Validar integração segura de secrets no CI/CD"
git push origin test-ci-cd-secrets-integration

# 2. Criar PR
gh pr create \
  --title "Test: CI/CD Pipeline - Integração Segura de Secrets" \
  --body "🔐 **Teste de Validação de Secrets**

Esta PR testa a integração segura dos secrets no pipeline CI/CD:

## 🧪 Objetivos do Teste
- [x] Validar que secrets obrigatórios estão configurados
- [x] Confirmar que valores sensíveis não são expostos nos logs
- [x] Testar autorização de deployment protegida
- [x] Verificar funcionamento do rollback automático

## 🛡️ Aspectos de Segurança Testados
- [x] Mascaramento automático de secrets nos logs
- [x] Validação de comprimento mínimo de tokens
- [x] Autorização prévia para deployments críticos
- [x] Conformidade com melhores práticas de segurança

## 📋 Checklist de Validação
- [ ] Workflow executa sem expor valores sensíveis
- [ ] Job de validação de secrets passa com sucesso
- [ ] Deploy é autorizado apenas com tokens válidos
- [ ] Logs mostram apenas informações não-sensíveis
- [ ] Rollback funciona em caso de falha

Após a execução, verificar que todos os secrets são manuseados de forma segura."
```

### Monitorar Execução

1. **GitHub Actions**: `<repo>/actions`
2. **Security Tab**: `<repo>/security`
3. **Verificar Logs**: Confirmar que secrets não aparecem
4. **Validar Deploy**: Confirmar autorização funcionou

## 📚 Recursos Adicionais

- 📖 [Documentação GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- 🔐 [OWASP Secrets Management](https://owasp.org/www-project-secrets-management-cheat-sheet/)
- 🛡️ [CI/CD Security Best Practices](https://docs.github.com/en/actions/security-guides)

## 📞 Suporte

Para questões relacionadas a secrets e segurança:

- 🔐 **Equipe DevSecOps**: devsecops@empresa.com
- 🛡️ **Segurança**: security@empresa.com
- 📋 **Documentação**: Ver `docs/ci-cd-workflow-documentation.md`

---

**⚠️ IMPORTANTE**: Este documento contém informações sobre práticas de segurança. Mantenha-o atualizado e revise regularmente as configurações de secrets.