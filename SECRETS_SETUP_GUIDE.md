# 🔐 Configuração de Secrets - ML Project CI/CD

Este arquivo fornece exemplos e instruções para configurar os secrets necessários para o pipeline CI/CD do ML Project.

## 📋 Quick Setup Commands

### 1. Configurar Secrets Obrigatórios

```bash
# 🔑 Secrets de aplicação
gh secret set SECRET_KEY --body "chave-secreta-aplicacao-super-complexa-min-20-chars"
gh secret set ML_CLIENT_ID --body "seu-client-id-mercado-livre"
gh secret set ML_CLIENT_SECRET --body "seu-client-secret-mercado-livre-min-32-chars"

# 🐳 Secrets do Docker Hub
gh secret set DOCKER_USERNAME --body "seu-usuario-docker-hub"
gh secret set DOCKER_PASSWORD --body "sua-senha-docker-hub-segura"

# 🚀 NOVOS: Secrets de Deploy Protegido
gh secret set DEPLOY_TOKEN --body "token-autorizacao-deploy-producao-min-20-chars"
gh secret set PROD_API_KEY --body "chave-api-producao-acesso-seguro-min-32-chars"
```

### 2. Configurar Secrets Opcionais (Recomendados)

```bash
# 📧 Notificações
gh secret set SLACK_WEBHOOK_URL --body "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX"
gh secret set TEAMS_WEBHOOK_URL --body "https://outlook.office.com/webhook/xxxx-xxxx-xxxx-xxxx/IncomingWebhook/xxxx/xxxx"
gh secret set NOTIFICATION_EMAIL --body "alerts@sua-empresa.com"

# 📊 Monitoramento
gh secret set SENTRY_DSN --body "https://examplePublicKey@o0.ingest.sentry.io/0"

# 🌐 URLs de Ambiente
gh secret set STAGING_URL --body "https://staging.sua-aplicacao.com"
gh secret set PRODUCTION_URL --body "https://producao.sua-aplicacao.com"
```

## 🛡️ Validações de Segurança

### Comprimento Mínimo de Secrets

- `SECRET_KEY`: Mínimo 20 caracteres
- `ML_CLIENT_SECRET`: Mínimo 32 caracteres
- `DEPLOY_TOKEN`: Mínimo 20 caracteres
- `PROD_API_KEY`: Mínimo 32 caracteres

### Formato Recomendado

```bash
# Exemplo de SECRET_KEY (Django/Flask style)
SECRET_KEY="django-insecure-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz"

# Exemplo de DEPLOY_TOKEN (JWT style)
DEPLOY_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ"

# Exemplo de PROD_API_KEY (API Key style)
PROD_API_KEY="sk-prod-1234567890abcdef1234567890abcdef"
```

## 🧪 Testar Configuração

### 1. Validar Secrets Localmente

```bash
# Executar script de validação
chmod +x scripts/validate-secrets.sh
./scripts/validate-secrets.sh
```

### 2. Testar no CI/CD

```bash
# Criar branch de teste
git checkout -b test-ci-cd-secrets-config
git commit --allow-empty -m "test: Validar configuração de secrets CI/CD"
git push origin test-ci-cd-secrets-config

# Criar PR de teste
gh pr create \
  --title "Test: Validação de Secrets CI/CD" \
  --body "🔐 **PR de Teste - Configuração de Secrets**

Este PR testa a configuração de secrets no pipeline CI/CD:

## 🎯 Objetivos
- [x] Validar que todos os secrets obrigatórios estão configurados
- [x] Testar job de validação de secrets
- [x] Confirmar que valores sensíveis não são expostos nos logs
- [x] Verificar autorização de deployment protegida

## 🔍 Verificações
- Workflow executa job \`validate-secrets\` com sucesso
- Deploy só é autorizado com tokens válidos
- Logs não expõem valores sensíveis
- Rollback automático funciona em caso de falha

## 🛡️ Aspectos de Segurança
- Mascaramento automático de secrets nos logs
- Validação de comprimento mínimo
- Autorização prévia para operações críticas
- Conformidade com práticas de segurança"
```

## 🚨 Troubleshooting

### Erro: "Secret não configurado"

```bash
# Verificar se secret existe
gh secret list

# Configurar secret ausente
gh secret set NOME_DO_SECRET --body "valor-do-secret"
```

### Erro: "Token muito curto"

```bash
# Para DEPLOY_TOKEN (mínimo 20 chars)
gh secret set DEPLOY_TOKEN --body "token-deploy-validado-20-chars-minimo"

# Para PROD_API_KEY (mínimo 32 chars)
gh secret set PROD_API_KEY --body "chave-api-producao-32-caracteres-minimo"
```

### Workflow falha na validação

```bash
# Executar validação local para debug
./scripts/validate-secrets.sh

# Verificar logs do workflow
gh run list --limit 5
gh run view <run-id> --log
```

## 📋 Checklist de Configuração

### Antes do primeiro deploy:

- [ ] Todos os secrets obrigatórios configurados
- [ ] Secrets têm comprimento mínimo adequado
- [ ] Script de validação executa sem erros
- [ ] PR de teste criado e workflow executado
- [ ] Logs verificados (sem exposição de secrets)
- [ ] Documentação de segurança revisada

### Para produção:

- [ ] `DEPLOY_TOKEN` configurado e validado
- [ ] `PROD_API_KEY` configurado e validado
- [ ] URLs de produção configuradas
- [ ] Notificações configuradas (Slack/Teams/Email)
- [ ] Monitoramento configurado (Sentry)
- [ ] Backup dos secrets em local seguro

## 📞 Suporte

- 📚 **Documentação**: `docs/secrets-security-guide.md`
- 🔧 **Script de validação**: `scripts/validate-secrets.sh`
- 🧪 **Testes**: `test_security_integration.py`

## 🔗 Links Úteis

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [OWASP Secrets Management](https://owasp.org/www-project-secrets-management-cheat-sheet/)
- [CI/CD Security Best Practices](https://docs.github.com/en/actions/security-guides)