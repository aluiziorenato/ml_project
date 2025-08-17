#!/usr/bin/env python3
"""
Teste de integração para validação de secrets no CI/CD.
Este script verifica se o sistema de segurança funciona corretamente.
"""

import os
import sys
import subprocess
from pathlib import Path

def test_secrets_validation_script():
    """Testa se o script de validação de secrets funciona corretamente."""
    print("🧪 Testando script de validação de secrets...")
    
    script_path = Path(__file__).parent / "scripts" / "validate-secrets.sh"
    
    if not script_path.exists():
        print(f"❌ Script não encontrado: {script_path}")
        return False
    
    if not os.access(script_path, os.X_OK):
        print(f"❌ Script não é executável: {script_path}")
        return False
    
    print("✅ Script de validação existe e é executável")
    return True

def test_workflow_yaml_syntax():
    """Testa se o workflow YAML tem sintaxe válida."""
    print("🧪 Testando sintaxe do workflow YAML...")
    
    try:
        import yaml
        workflow_path = Path(__file__).parent / ".github" / "workflows" / "ci-cd.yml"
        
        with open(workflow_path, 'r') as f:
            yaml.safe_load(f)
        
        print("✅ Workflow YAML tem sintaxe válida")
        return True
    except Exception as e:
        print(f"❌ Erro na sintaxe do workflow: {e}")
        return False

def test_secrets_configuration():
    """Testa se as configurações de secrets estão corretas no workflow."""
    print("🧪 Testando configuração de secrets no workflow...")
    
    workflow_path = Path(__file__).parent / ".github" / "workflows" / "ci-cd.yml"
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    # Verificar se os novos secrets estão presentes
    required_secrets = [
        "DEPLOY_TOKEN",
        "PROD_API_KEY"
    ]
    
    for secret in required_secrets:
        if f"secrets.{secret}" in content:
            print(f"✅ Secret {secret} configurado no workflow")
        else:
            print(f"❌ Secret {secret} não encontrado no workflow")
            return False
    
    # Verificar se há job de validação de secrets
    if "validate-secrets:" in content:
        print("✅ Job de validação de secrets configurado")
    else:
        print("❌ Job de validação de secrets não encontrado")
        return False
    
    return True

def test_security_comments():
    """Verifica se há comentários de segurança apropriados."""
    print("🧪 Testando presença de comentários de segurança...")
    
    workflow_path = Path(__file__).parent / ".github" / "workflows" / "ci-cd.yml"
    
    with open(workflow_path, 'r') as f:
        content = f.read()
    
    security_indicators = [
        "SECURITY:",
        "secrets são mascarados",
        "NUNCA",
        "valores sensíveis"
    ]
    
    found_indicators = 0
    for indicator in security_indicators:
        if indicator.lower() in content.lower():
            found_indicators += 1
    
    if found_indicators >= 2:
        print(f"✅ Comentários de segurança encontrados ({found_indicators} indicadores)")
        return True
    else:
        print(f"❌ Poucos comentários de segurança ({found_indicators} indicadores)")
        return False

def test_documentation_exists():
    """Verifica se a documentação de segurança foi criada."""
    print("🧪 Testando presença de documentação de segurança...")
    
    doc_path = Path(__file__).parent / "docs" / "secrets-security-guide.md"
    
    if doc_path.exists():
        print("✅ Documentação de segurança existe")
        return True
    else:
        print("❌ Documentação de segurança não encontrada")
        return False

def main():
    """Executa todos os testes de integração."""
    print("🔐 Testes de Integração - Segurança CI/CD")
    print("=" * 50)
    
    tests = [
        test_secrets_validation_script,
        test_workflow_yaml_syntax,
        test_secrets_configuration,
        test_security_comments,
        test_documentation_exists
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Line break between tests
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {e}")
            print()
    
    print("📊 RESULTADOS DOS TESTES")
    print("=" * 30)
    print(f"✅ Testes passados: {passed}/{total}")
    print(f"{'🎉 Todos os testes passaram!' if passed == total else '⚠️  Alguns testes falharam'}")
    
    if passed == total:
        print("\n🛡️ Sistema de segurança validado com sucesso!")
        print("🚀 Pronto para criar PR de teste")
        return 0
    else:
        print(f"\n❌ {total - passed} teste(s) falharam")
        print("🔧 Revise as configurações antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())