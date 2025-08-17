# 📊 Guia de Acesso aos Artefatos de Cobertura de Testes

## 🎯 Objetivo

Este documento fornece instruções detalhadas sobre como acessar e utilizar os relatórios de cobertura de testes gerados automaticamente pelo pipeline CI/CD do ML Project.

## 📁 Tipos de Artefatos Gerados

### 1. 📊 Relatórios de Cobertura Consolidados
- **Nome do Artefato**: `coverage-reports-latest` (última execução) / `coverage-reports-{run_number}` (execução específica)
- **Conteúdo**:
  - `backend-coverage-html/` - Relatório HTML interativo
  - `backend-coverage.xml` - Relatório XML para ferramentas
  - `coverage-badge.svg` - Badge de cobertura
  - `README.md` - Instruções detalhadas

### 2. 🔧 Artefatos por Módulo
- **Backend**: `backend-coverage-{run_number}`
- **Backend Integration**: `backend-integration-coverage-{run_number}`
- Cada artefato contém relatórios HTML e XML específicos do módulo

## 🔍 Como Acessar os Artefatos

### Método 1: Via GitHub Actions (Recomendado)

1. **Navegue até a aba Actions**
   ```
   https://github.com/aluiziorenato/ml_project/actions
   ```

2. **Selecione a execução do workflow desejada**
   - Clique na execução mais recente do "ML Project CI/CD Pipeline"
   - Ou selecione uma execução específica por commit/branch

3. **Baixe os artefatos**
   - Role até a seção "Artifacts" no final da página
   - Clique em `coverage-reports-latest` para a versão mais recente
   - Ou clique em artefatos específicos por módulo

4. **Extraia e visualize**
   ```bash
   unzip coverage-reports-latest.zip
   cd coverage-reports-latest
   open backend-coverage-html/index.html  # macOS
   # ou
   xdg-open backend-coverage-html/index.html  # Linux
   # ou abra o arquivo em qualquer navegador web
   ```

### Método 2: Via Pull Request

1. **Visualize o comentário automático**
   - Todo PR recebe um comentário automático com resumo da cobertura
   - Links diretos para artefatos estão incluídos no comentário

2. **Acesse via link direto**
   - Clique no link "📊 Relatório HTML" no comentário do PR
   - Será redirecionado para a execução do workflow com os artefatos

### Método 3: Via API do GitHub (Avançado)

```bash
# Listar artefatos da última execução
curl -H "Authorization: token YOUR_TOKEN" \
  "https://api.github.com/repos/aluiziorenato/ml_project/actions/artifacts"

# Baixar artefato específico
curl -H "Authorization: token YOUR_TOKEN" \
  -L "https://api.github.com/repos/aluiziorenato/ml_project/actions/artifacts/{artifact_id}/zip" \
  -o coverage-report.zip
```

## 📊 Interpretando os Relatórios

### Relatório HTML Interativo

**Página Principal (index.html)**:
- Visão geral da cobertura por módulo
- Percentuais de cobertura de linhas, branches e funções
- Links para detalhes de cada arquivo

**Navegação**:
- Clique em qualquer módulo/arquivo para ver detalhes
- Linhas vermelhas = não cobertas por testes
- Linhas verdes = cobertas por testes
- Números ao lado das linhas = quantas vezes foram executadas

### Relatório XML

**Uso típico**:
- Integração com IDEs (VS Code, PyCharm, etc.)
- Ferramentas de CI/CD (SonarQube, Code Climate)
- Scripts automatizados de análise

**Estrutura**:
```xml
<coverage version="..." timestamp="...">
  <sources>...</sources>
  <packages>
    <package name="app">
      <classes>
        <class name="module.py" filename="app/module.py">
          <methods>...</methods>
          <lines>
            <line number="1" hits="5"/>
            <line number="2" hits="0"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>
```

## 📈 Monitoramento e Alertas

### Métricas Importantes

1. **Cobertura Geral**: Meta mínima de 80%
2. **Cobertura por Módulo**:
   - `app/auth/` - Meta: 95%+ (crítico)
   - `app/db/` - Meta: 90%+ (crítico)
   - `app/routers/` - Meta: 85%+ (importante)
   - `app/services/` - Meta: 80%+ (importante)

### Alertas Automáticos

O pipeline irá alertar quando:
- Cobertura geral cair abaixo de 80%
- Módulos críticos ficarem abaixo das metas
- Houve regressão significativa (>5%) comparado ao branch principal

## 🛠️ Integrações Disponíveis

### 1. Codecov Dashboard
- **URL**: https://codecov.io/gh/aluiziorenato/ml_project
- **Funcionalidades**:
  - Histórico de cobertura
  - Comparação entre branches
  - Comentários automáticos em PRs
  - Gráficos de tendências

### 2. Badge de Cobertura
```markdown
![Coverage](https://codecov.io/gh/aluiziorenato/ml_project/branch/main/graph/badge.svg)
```

### 3. IDE Integration
- Configure seu IDE para usar os arquivos `coverage.xml`
- Muitos IDEs mostram cobertura diretamente no editor

## 🔧 Configuração Local

Para gerar relatórios localmente:

```bash
cd backend

# Instalar dependências
pip install pytest pytest-cov coverage

# Executar testes com cobertura
pytest --cov=app --cov-report=html --cov-report=xml --cov-report=term-missing

# Visualizar relatório
open htmlcov/index.html
```

## 📅 Retenção de Artefatos

- **coverage-reports-latest**: 7 dias
- **coverage-reports-{run_number}**: 30 dias
- **Artefatos específicos de módulos**: 14 dias

## 🚨 Solução de Problemas

### Problema: Artefatos não aparecem
**Soluções**:
1. Verifique se o workflow foi executado completamente
2. Confirme se você tem permissões de acesso ao repositório
3. Aguarde alguns minutos após a conclusão do workflow

### Problema: Relatório HTML não abre
**Soluções**:
1. Verifique se extraiu completamente o ZIP
2. Tente abrir diretamente no navegador
3. Verifique se não há bloqueios de JavaScript

### Problema: Cobertura mostrada como 0%
**Soluções**:
1. Verifique se os testes foram executados com sucesso
2. Confirme se os arquivos de teste estão no diretório correto
3. Verifique logs do workflow para erros

## 📞 Suporte

- **Issues**: [GitHub Issues](https://github.com/aluiziorenato/ml_project/issues)
- **Discussões**: [GitHub Discussions](https://github.com/aluiziorenato/ml_project/discussions)
- **Documentação**: [Checklist de Testes](../checklist_testes.md)

---

**Última atualização**: Dezembro 2024  
**Versão do guia**: 1.0  
**Responsável**: Equipe de Desenvolvimento ML Project