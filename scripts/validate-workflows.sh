#!/bin/bash

# 🔍 CI/CD Workflow Validation Script
# Este script valida a configuração dos workflows do GitHub Actions

set -e

echo "🚀 Iniciando validação dos workflows CI/CD..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções utilitárias
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

# Diretórios base
GITHUB_DIR=".github"
WORKFLOWS_DIR="$GITHUB_DIR/workflows"
DOCS_DIR="docs"

echo ""
print_info "Verificando estrutura de diretórios..."

# 1. Verificar estrutura de diretórios
if [ -d "$GITHUB_DIR" ]; then
    print_success "Diretório .github encontrado"
else
    print_error "Diretório .github não encontrado"
    exit 1
fi

if [ -d "$WORKFLOWS_DIR" ]; then
    print_success "Diretório .github/workflows encontrado"
else
    print_error "Diretório .github/workflows não encontrado"
    exit 1
fi

# 2. Verificar arquivos de workflow obrigatórios
echo ""
print_info "Verificando arquivos de workflow..."

REQUIRED_WORKFLOWS=(
    "ci-cd.yml"
    "security.yml"
)

OPTIONAL_WORKFLOWS=(
    "ci.yml"
    "backend-coverage.yml"
    "comprehensive-tests.yml"
    "test-coverage-automation.yml"
)

for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        print_success "Workflow $workflow encontrado"
    else
        print_error "Workflow obrigatório $workflow não encontrado"
        exit 1
    fi
done

for workflow in "${OPTIONAL_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        print_success "Workflow opcional $workflow encontrado"
    else
        print_warning "Workflow opcional $workflow não encontrado"
    fi
done

# 3. Verificar configuração do Dependabot
echo ""
print_info "Verificando configuração do Dependabot..."

if [ -f "$GITHUB_DIR/dependabot.yml" ]; then
    print_success "Arquivo dependabot.yml encontrado"
    
    # Verificar se contém configurações básicas
    if grep -q "package-ecosystem" "$GITHUB_DIR/dependabot.yml"; then
        print_success "Configuração do Dependabot parece válida"
    else
        print_warning "Configuração do Dependabot pode estar incompleta"
    fi
else
    print_error "Arquivo dependabot.yml não encontrado"
fi

# 4. Verificar sintaxe YAML dos workflows
echo ""
print_info "Verificando sintaxe YAML dos workflows..."

# Verificar se yamllint está disponível
if command -v yamllint &> /dev/null; then
    for workflow_file in "$WORKFLOWS_DIR"/*.yml "$WORKFLOWS_DIR"/*.yaml; do
        if [ -f "$workflow_file" ]; then
            if yamllint "$workflow_file" &> /dev/null; then
                print_success "Sintaxe YAML válida: $(basename "$workflow_file")"
            else
                print_error "Erro de sintaxe YAML em: $(basename "$workflow_file")"
                yamllint "$workflow_file"
            fi
        fi
    done
else
    print_warning "yamllint não instalado - pulando verificação de sintaxe"
    print_info "Para instalar: pip install yamllint"
fi

# 5. Verificar estrutura do workflow principal (ci-cd.yml)
echo ""
print_info "Verificando estrutura do workflow principal..."

CI_CD_FILE="$WORKFLOWS_DIR/ci-cd.yml"

if [ -f "$CI_CD_FILE" ]; then
    # Verificar jobs obrigatórios
    REQUIRED_JOBS=(
        "lint-backend"
        "test-backend"
        "security-scan"
        "build-and-push"
        "deploy"
        "notifications"
    )
    
    for job in "${REQUIRED_JOBS[@]}"; do
        if grep -q "$job:" "$CI_CD_FILE"; then
            print_success "Job $job encontrado no ci-cd.yml"
        else
            print_error "Job obrigatório $job não encontrado no ci-cd.yml"
        fi
    done
    
    # Verificar triggers
    if grep -q "on:" "$CI_CD_FILE"; then
        print_success "Triggers configurados no ci-cd.yml"
    else
        print_error "Triggers não configurados no ci-cd.yml"
    fi
    
    # Verificar variáveis de ambiente
    if grep -q "env:" "$CI_CD_FILE"; then
        print_success "Variáveis de ambiente configuradas"
    else
        print_warning "Variáveis de ambiente não encontradas"
    fi
    
    # Verificar uso de secrets
    if grep -q "secrets\." "$CI_CD_FILE"; then
        print_success "Uso de secrets detectado"
    else
        print_warning "Nenhum uso de secrets detectado"
    fi
fi

# 6. Verificar estrutura do workflow de segurança
echo ""
print_info "Verificando workflow de segurança..."

SECURITY_FILE="$WORKFLOWS_DIR/security.yml"

if [ -f "$SECURITY_FILE" ]; then
    SECURITY_JOBS=(
        "dependency-scan"
        "secret-scan"
        "container-scan"
        "code-security-scan"
    )
    
    for job in "${SECURITY_JOBS[@]}"; do
        if grep -q "$job:" "$SECURITY_FILE"; then
            print_success "Job de segurança $job encontrado"
        else
            print_warning "Job de segurança $job não encontrado"
        fi
    done
else
    print_error "Workflow de segurança não encontrado"
fi

# 7. Verificar documentação
echo ""
print_info "Verificando documentação..."

DOC_FILES=(
    "$DOCS_DIR/ci-cd-workflow-documentation.md"
    "$DOCS_DIR/ci-cd-workflow-improvements.md"
    "$DOCS_DIR/implementation-summary.md"
)

for doc_file in "${DOC_FILES[@]}"; do
    if [ -f "$doc_file" ]; then
        print_success "Documentação encontrada: $(basename "$doc_file")"
    else
        print_warning "Documentação não encontrada: $(basename "$doc_file")"
    fi
done

# 8. Verificar estrutura de dependências
echo ""
print_info "Verificando estrutura de dependências do projeto..."

# Verificar requirements.txt nos serviços
SERVICES=(
    "backend"
    "simulator_service"
    "learning_service"
    "optimizer_ai"
    "discount_campaign_scheduler"
    "campaign_automation_service"
)

for service in "${SERVICES[@]}"; do
    if [ -f "$service/requirements.txt" ]; then
        print_success "requirements.txt encontrado em $service"
    else
        print_warning "requirements.txt não encontrado em $service"
    fi
done

# Verificar package.json do frontend
if [ -f "frontend/package.json" ]; then
    print_success "package.json encontrado no frontend"
else
    print_warning "package.json não encontrado no frontend"
fi

# 9. Verificar Dockerfiles
echo ""
print_info "Verificando Dockerfiles..."

for service in "${SERVICES[@]}"; do
    if [ -f "$service/Dockerfile" ]; then
        print_success "Dockerfile encontrado em $service"
    else
        print_warning "Dockerfile não encontrado em $service"
    fi
done

if [ -f "frontend/Dockerfile" ]; then
    print_success "Dockerfile encontrado no frontend"
else
    print_warning "Dockerfile não encontrado no frontend"
fi

# 10. Gerar relatório de validação
echo ""
print_info "Gerando relatório de validação..."

REPORT_FILE="workflow-validation-report.md"

cat > "$REPORT_FILE" << EOF
# 📊 Relatório de Validação dos Workflows CI/CD

**Data da Validação**: $(date)
**Script Version**: 1.0

## ✅ Verificações Realizadas

### 📁 Estrutura de Arquivos
- [x] Diretório .github existe
- [x] Diretório .github/workflows existe
- [x] Arquivos de workflow principais presentes

### 🔧 Workflows Configurados
EOF

# Adicionar status dos workflows ao relatório
for workflow in "${REQUIRED_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "- [x] $workflow (obrigatório)" >> "$REPORT_FILE"
    else
        echo "- [ ] $workflow (obrigatório) ❌" >> "$REPORT_FILE"
    fi
done

for workflow in "${OPTIONAL_WORKFLOWS[@]}"; do
    if [ -f "$WORKFLOWS_DIR/$workflow" ]; then
        echo "- [x] $workflow (opcional)" >> "$REPORT_FILE"
    else
        echo "- [ ] $workflow (opcional)" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF

### 🤖 Dependabot
EOF

if [ -f "$GITHUB_DIR/dependabot.yml" ]; then
    echo "- [x] Configuração do Dependabot presente" >> "$REPORT_FILE"
else
    echo "- [ ] Configuração do Dependabot ausente ❌" >> "$REPORT_FILE"
fi

cat >> "$REPORT_FILE" << EOF

### 📊 Jobs do CI/CD Principal
EOF

for job in "${REQUIRED_JOBS[@]}"; do
    if grep -q "$job:" "$CI_CD_FILE" 2>/dev/null; then
        echo "- [x] $job" >> "$REPORT_FILE"
    else
        echo "- [ ] $job ❌" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF

### 🔒 Jobs de Segurança
EOF

for job in "${SECURITY_JOBS[@]}"; do
    if grep -q "$job:" "$SECURITY_FILE" 2>/dev/null; then
        echo "- [x] $job" >> "$REPORT_FILE"
    else
        echo "- [ ] $job ⚠️" >> "$REPORT_FILE"
    fi
done

cat >> "$REPORT_FILE" << EOF

## 📋 Próximos Passos

### Configuração de Secrets Obrigatórios
\`\`\`bash
gh secret set SECRET_KEY --body "your-secret-key"
gh secret set ML_CLIENT_ID --body "your-client-id"
gh secret set ML_CLIENT_SECRET --body "your-client-secret"
gh secret set DOCKER_USERNAME --body "your-docker-username"
gh secret set DOCKER_PASSWORD --body "your-docker-password"
\`\`\`

### Configuração de Secrets Opcionais
\`\`\`bash
gh secret set SLACK_WEBHOOK_URL --body "your-slack-webhook"
gh secret set TEAMS_WEBHOOK_URL --body "your-teams-webhook"
gh secret set NOTIFICATION_EMAIL --body "your-email@company.com"
gh secret set SENTRY_DSN --body "your-sentry-dsn"
\`\`\`

### Testes Recomendados
1. Criar PR de teste para validar pipeline
2. Verificar execução de todos os jobs
3. Testar notificações
4. Validar deploy em staging

---

**Gerado automaticamente pelo script de validação**
EOF

print_success "Relatório de validação gerado: $REPORT_FILE"

# 11. Sugestões de melhorias
echo ""
print_info "Sugestões de melhorias:"

echo "1. 📋 Configurar secrets no GitHub:"
echo "   gh secret set SECRET_KEY --body 'your-secret'"

echo "2. 🧪 Testar workflow com PR:"
echo "   git checkout -b test-ci-cd"
echo "   git push origin test-ci-cd"

echo "3. 📊 Monitorar execução em:"
echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[\/:]//; s/.git$//')/actions"

echo "4. 🔒 Revisar configurações de segurança:"
echo "   https://github.com/$(git remote get-url origin | sed 's/.*github.com[\/:]//; s/.git$//')/settings/security_analysis"

echo ""
print_success "Validação dos workflows CI/CD concluída!"
print_info "Verifique o relatório detalhado em: $REPORT_FILE"

exit 0