#!/bin/bash

# 🔐 CI/CD Secrets Validation Script
# Este script valida se todos os secrets necessários estão configurados
# e fornece orientações sobre segurança de logs e gerenciamento de secrets

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔐 Validação de Secrets do CI/CD${NC}"
    echo "========================================="
    echo ""
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_security_note() {
    echo -e "${YELLOW}🛡️ SEGURANÇA: $1${NC}"
}

check_secret() {
    local secret_name=$1
    local required=$2
    local description=$3
    
    # Check if running in GitHub Actions
    if [ -n "$GITHUB_ACTIONS" ]; then
        # In GitHub Actions, we can only check if the secret is not empty
        if [ -n "${!secret_name}" ]; then
            print_success "$secret_name configurado ($description)"
            return 0
        else
            if [ "$required" = "true" ]; then
                print_error "$secret_name não está configurado ($description)"
                return 1
            else
                print_warning "$secret_name não está configurado ($description) - OPCIONAL"
                return 0
            fi
        fi
    else
        # Running locally - provide instructions
        print_info "Para verificar $secret_name localmente, configure como variável de ambiente"
        echo "  export $secret_name=<seu_valor_secreto>"
        return 0
    fi
}

validate_secrets() {
    echo "🔍 Validando secrets obrigatórios..."
    echo ""
    
    local all_valid=true
    
    # Required secrets
    check_secret "SECRET_KEY" "true" "Chave secreta da aplicação" || all_valid=false
    check_secret "ML_CLIENT_ID" "true" "Client ID da API do Mercado Livre" || all_valid=false
    check_secret "ML_CLIENT_SECRET" "true" "Secret da API do Mercado Livre" || all_valid=false
    check_secret "DOCKER_USERNAME" "true" "Usuário do Docker Hub" || all_valid=false
    check_secret "DOCKER_PASSWORD" "true" "Senha do Docker Hub" || all_valid=false
    check_secret "DEPLOY_TOKEN" "true" "Token de autorização para deployment" || all_valid=false
    check_secret "PROD_API_KEY" "true" "Chave da API de produção" || all_valid=false
    
    echo ""
    echo "🔍 Validando secrets opcionais..."
    echo ""
    
    # Optional secrets
    check_secret "SLACK_WEBHOOK_URL" "false" "URL do webhook do Slack"
    check_secret "TEAMS_WEBHOOK_URL" "false" "URL do webhook do Teams"
    check_secret "NOTIFICATION_EMAIL" "false" "Email para notificações"
    check_secret "SENTRY_DSN" "false" "URL do Sentry para monitoramento"
    check_secret "STAGING_URL" "false" "URL do ambiente de staging"
    check_secret "PRODUCTION_URL" "false" "URL do ambiente de produção"
    
    return $([ "$all_valid" = "true" ])
}

print_security_guidelines() {
    echo ""
    echo "🛡️ DIRETRIZES DE SEGURANÇA PARA CI/CD"
    echo "======================================"
    echo ""
    
    print_security_note "LOGS E EXPOSIÇÃO DE SECRETS:"
    echo "  • GitHub Actions automaticamente mascara secrets nos logs"
    echo "  • NUNCA faça echo/print direto de valores de secrets"
    echo "  • Use \${{ secrets.SECRET_NAME }} apenas em contextos seguros"
    echo "  • Logs podem ser visualizados por colaboradores do repositório"
    echo ""
    
    print_security_note "CONFIGURAÇÃO DE SECRETS:"
    echo "  • Acesse: Repositório > Settings > Secrets and variables > Actions"
    echo "  • Use secrets específicos por ambiente (staging/production)"
    echo "  • Implemente rotação regular de secrets sensíveis"
    echo "  • Monitore uso e acesso aos secrets"
    echo ""
    
    print_security_note "MELHORES PRÁTICAS:"
    echo "  • Use o princípio do menor privilégio"
    echo "  • Implemente aprovação manual para deploys de produção"
    echo "  • Configure alertas para falhas de autenticação"
    echo "  • Mantenha backup seguro de secrets críticos"
    echo "  • Documente purpose e owner de cada secret"
    echo ""
    
    print_security_note "MONITORAMENTO E AUDITORIA:"
    echo "  • Monitore logs de deploy para comportamentos anômalos"
    echo "  • Configure alertas para falhas de autenticação"
    echo "  • Implemente logging de auditoria para operações críticas"
    echo "  • Revise regularmente permissions e access logs"
    echo ""
}

print_configuration_guide() {
    echo ""
    echo "📋 GUIA DE CONFIGURAÇÃO DE SECRETS"
    echo "=================================="
    echo ""
    
    echo "1. SECRETS OBRIGATÓRIOS:"
    echo ""
    echo "gh secret set SECRET_KEY --body \"sua-chave-secreta-complexa\""
    echo "gh secret set ML_CLIENT_ID --body \"seu-client-id-mercado-livre\""
    echo "gh secret set ML_CLIENT_SECRET --body \"seu-client-secret-mercado-livre\""
    echo "gh secret set DOCKER_USERNAME --body \"seu-usuario-docker\""
    echo "gh secret set DOCKER_PASSWORD --body \"sua-senha-docker\""
    echo "gh secret set DEPLOY_TOKEN --body \"token-autorizacao-deploy-min-20-chars\""
    echo "gh secret set PROD_API_KEY --body \"chave-api-producao-min-32-chars\""
    echo ""
    
    echo "2. SECRETS OPCIONAIS:"
    echo ""
    echo "gh secret set SLACK_WEBHOOK_URL --body \"https://hooks.slack.com/services/...\""
    echo "gh secret set TEAMS_WEBHOOK_URL --body \"https://outlook.office.com/webhook/...\""
    echo "gh secret set NOTIFICATION_EMAIL --body \"alerts@sua-empresa.com\""
    echo "gh secret set SENTRY_DSN --body \"https://abc123@sentry.io/123456\""
    echo "gh secret set STAGING_URL --body \"https://staging.sua-app.com\""
    echo "gh secret set PRODUCTION_URL --body \"https://producao.sua-app.com\""
    echo ""
}

print_testing_guide() {
    echo ""
    echo "🧪 TESTANDO O PIPELINE COM SECRETS"
    echo "=================================="
    echo ""
    
    echo "1. CRIAR PR DE TESTE:"
    echo "   git checkout -b test-ci-cd-secrets"
    echo "   git commit --allow-empty -m \"test: Validar pipeline CI/CD com secrets\""
    echo "   git push origin test-ci-cd-secrets"
    echo "   gh pr create --title \"Test: CI/CD Pipeline com Secrets\" --body \"Validando integração segura de secrets\""
    echo ""
    
    echo "2. MONITORAR EXECUÇÃO:"
    echo "   • GitHub Actions: $(git config --get remote.origin.url | sed 's/\.git$//')/actions"
    echo "   • Security Tab: $(git config --get remote.origin.url | sed 's/\.git$//')/security"
    echo "   • Verificar logs sem exposição de valores sensíveis"
    echo ""
    
    echo "3. VALIDAR SEGURANÇA:"
    echo "   • Confirmar que secrets não aparecem nos logs"
    echo "   • Verificar que deploy foi autorizado corretamente"
    echo "   • Testar mecanismos de rollback em caso de falha"
    echo ""
}

# Main execution
main() {
    print_header
    
    if validate_secrets; then
        print_success "Todos os secrets obrigatórios estão configurados!"
        echo ""
        print_info "Pipeline está pronto para execução segura"
    else
        print_error "Alguns secrets obrigatórios não estão configurados"
        echo ""
        print_warning "Configure os secrets ausentes antes de executar o pipeline"
    fi
    
    print_security_guidelines
    print_configuration_guide
    print_testing_guide
    
    echo ""
    print_info "Para mais informações, consulte: docs/ci-cd-workflow-documentation.md"
    echo ""
}

# Execute main function
main "$@"