#!/usr/bin/env python3
"""
Script para testar conexão com banco de dados PostgreSQL.

Uso:
    # Com Docker Compose (padrão)
    python scripts/check_db.py
    
    # Com configuração local
    DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/ml_db python scripts/check_db.py
    
    # Com teste CRUD
    python scripts/check_db.py --test-crud
    
    # Com output verboso
    python scripts/check_db.py --verbose
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Optional

# Adiciona o diretório do app ao path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from sqlmodel import create_engine, Session, SQLModel, select, text
    from sqlalchemy.exc import OperationalError, SQLAlchemyError
    from app.config import settings
except ImportError as e:
    print(f"❌ Erro ao importar dependências: {e}")
    print("💡 Certifique-se de que as dependências estão instaladas: pip install -r requirements.txt")
    sys.exit(1)


def test_connection(database_url: str, verbose: bool = False) -> bool:
    """
    Testa conexão básica com o banco de dados.
    
    Args:
        database_url: URL de conexão com o banco
        verbose: Se deve mostrar detalhes adicionais
        
    Returns:
        bool: True se conexão bem-sucedida, False caso contrário
    """
    print(f"🔗 Testando conexão com banco de dados...")
    if verbose:
        # Oculta senha na URL para logs
        safe_url = database_url.replace(database_url.split('@')[0].split('://')[-1], '***')
        print(f"   URL: {safe_url}")
    
    try:
        engine = create_engine(database_url, echo=verbose)
        
        with engine.connect() as conn:
            # Teste básico de conexão
            result = conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                print("✅ Conexão estabelecida com sucesso!")
                
                # Informações adicionais do banco
                if verbose:
                    version_result = conn.execute(text("SELECT version()"))
                    version = version_result.scalar()
                    print(f"   PostgreSQL Version: {version.split()[1] if version else 'Unknown'}")
                    
                    db_result = conn.execute(text("SELECT current_database()"))
                    db_name = db_result.scalar()
                    print(f"   Database: {db_name}")
                    
                    user_result = conn.execute(text("SELECT current_user"))
                    user = user_result.scalar()
                    print(f"   User: {user}")
                
                return True
            else:
                print("❌ Teste de conexão falhou - resposta inesperada")
                return False
                
    except OperationalError as e:
        print(f"❌ Erro de conexão: {e}")
        if "Connection refused" in str(e):
            print("💡 Dicas:")
            print("   - Verifique se o PostgreSQL está rodando")
            print("   - Para Docker: docker-compose up -d db")
            print("   - Para local: systemctl status postgresql")
        elif "authentication failed" in str(e).lower():
            print("💡 Dicas:")
            print("   - Verifique usuário e senha na DATABASE_URL")
            print("   - Confirme permissões do usuário no banco")
        elif "database" in str(e).lower() and "does not exist" in str(e).lower():
            print("💡 Dicas:")
            print("   - Verifique se o banco de dados existe")
            print("   - Execute: docker-compose exec db createdb ml_db -U postgres")
        return False
        
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def test_crud_operations(database_url: str, verbose: bool = False) -> bool:
    """
    Testa operações CRUD básicas no banco.
    
    Args:
        database_url: URL de conexão com o banco
        verbose: Se deve mostrar detalhes adicionais
        
    Returns:
        bool: True se todas operações bem-sucedidas, False caso contrário
    """
    print(f"\n🔧 Testando operações CRUD...")
    
    try:
        engine = create_engine(database_url, echo=verbose)
        
        # Nome da tabela de teste
        test_table = "test_connection_check"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        with engine.connect() as conn:
            # CREATE - Criar tabela de teste
            if verbose:
                print("   Criando tabela de teste...")
            conn.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {test_table} (
                    id SERIAL PRIMARY KEY,
                    test_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            conn.commit()
            
            # INSERT - Inserir dados de teste
            if verbose:
                print("   Inserindo dados de teste...")
            test_data = f"test_data_{timestamp}"
            conn.execute(text(f"""
                INSERT INTO {test_table} (test_data) VALUES ('{test_data}')
            """))
            conn.commit()
            
            # READ - Ler dados inseridos
            if verbose:
                print("   Lendo dados inseridos...")
            result = conn.execute(text(f"""
                SELECT id, test_data FROM {test_table} 
                WHERE test_data = '{test_data}'
            """))
            row = result.fetchone()
            
            if not row:
                print("❌ Falha na operação READ - dados não encontrados")
                return False
                
            record_id = row[0]
            if verbose:
                print(f"   Registro criado com ID: {record_id}")
            
            # UPDATE - Atualizar dados
            if verbose:
                print("   Atualizando dados...")
            updated_data = f"updated_{test_data}"
            conn.execute(text(f"""
                UPDATE {test_table} 
                SET test_data = '{updated_data}' 
                WHERE id = {record_id}
            """))
            conn.commit()
            
            # Verificar UPDATE
            result = conn.execute(text(f"""
                SELECT test_data FROM {test_table} WHERE id = {record_id}
            """))
            updated_row = result.fetchone()
            
            if not updated_row or updated_row[0] != updated_data:
                print("❌ Falha na operação UPDATE")
                return False
            
            # DELETE - Remover dados de teste
            if verbose:
                print("   Removendo dados de teste...")
            conn.execute(text(f"""
                DELETE FROM {test_table} WHERE id = {record_id}
            """))
            conn.commit()
            
            # Verificar DELETE
            result = conn.execute(text(f"""
                SELECT COUNT(*) FROM {test_table} WHERE id = {record_id}
            """))
            count = result.scalar()
            
            if count != 0:
                print("❌ Falha na operação DELETE")
                return False
            
            # Limpar tabela de teste
            conn.execute(text(f"DROP TABLE IF EXISTS {test_table}"))
            conn.commit()
            
            print("✅ Todas as operações CRUD executadas com sucesso!")
            return True
            
    except SQLAlchemyError as e:
        print(f"❌ Erro nas operações CRUD: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado no teste CRUD: {e}")
        return False


def check_environment(verbose: bool = False) -> bool:
    """
    Verifica configurações de ambiente.
    
    Args:
        verbose: Se deve mostrar detalhes adicionais
        
    Returns:
        bool: True se ambiente configurado corretamente
    """
    print(f"\n🌍 Verificando configurações de ambiente...")
    
    issues = []
    
    # Verificar DATABASE_URL
    db_url = os.getenv('DATABASE_URL') or settings.database_url
    if not db_url or db_url == "postgresql+psycopg2://user:password@localhost/db":
        issues.append("DATABASE_URL não configurada ou usando valor padrão")
    elif verbose:
        safe_url = db_url.replace(db_url.split('@')[0].split('://')[-1], '***')
        print(f"   ✅ DATABASE_URL: {safe_url}")
    
    # Verificar outras configurações importantes
    if not settings.secret_key or settings.secret_key == "change-this-secret-key-in-production":
        issues.append("SECRET_KEY não configurada ou usando valor padrão inseguro")
    elif verbose:
        print(f"   ✅ SECRET_KEY: configurada")
    
    if not settings.admin_email or settings.admin_email == "admin@example.com":
        issues.append("ADMIN_EMAIL não configurada ou usando valor padrão")
    elif verbose:
        print(f"   ✅ ADMIN_EMAIL: {settings.admin_email}")
    
    if not settings.admin_password:
        issues.append("ADMIN_PASSWORD não configurada")
    elif verbose:
        print(f"   ✅ ADMIN_PASSWORD: configurada")
    
    # Configurações do Mercado Livre (opcionais mas importantes)
    if not settings.ml_client_id:
        if verbose:
            print(f"   ⚠️  ML_CLIENT_ID: não configurada (opcional)")
    elif verbose:
        print(f"   ✅ ML_CLIENT_ID: configurada")
    
    if not settings.ml_client_secret:
        if verbose:
            print(f"   ⚠️  ML_CLIENT_SECRET: não configurada (opcional)")
    elif verbose:
        print(f"   ✅ ML_CLIENT_SECRET: configurada")
    
    if issues:
        print("❌ Problemas encontrados na configuração:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 Dicas:")
        print("   - Copie .env.example para .env: cp .env.example .env")
        print("   - Configure as variáveis necessárias no arquivo .env")
        return False
    else:
        print("✅ Configurações de ambiente OK!")
        return True


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Testa conexão e operações com banco de dados PostgreSQL",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python scripts/check_db.py                                    # Teste básico
  python scripts/check_db.py --verbose                         # Com detalhes
  python scripts/check_db.py --test-crud                       # Inclui teste CRUD
  DATABASE_URL=postgresql://user:pass@localhost:5432/db python scripts/check_db.py
        """
    )
    
    parser.add_argument(
        '--test-crud', 
        action='store_true',
        help='Executa testes de operações CRUD (CREATE, READ, UPDATE, DELETE)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Exibe informações detalhadas durante os testes'
    )
    
    parser.add_argument(
        '--skip-env-check',
        action='store_true',
        help='Pula verificação de configurações de ambiente'
    )
    
    args = parser.parse_args()
    
    print("🏥 Diagnóstico de Conexão com Banco de Dados")
    print("=" * 50)
    
    # Obter URL do banco
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        try:
            database_url = settings.database_url
        except Exception as e:
            print(f"❌ Erro ao carregar configurações: {e}")
            sys.exit(1)
    
    success = True
    
    # Verificar ambiente
    if not args.skip_env_check:
        success &= check_environment(args.verbose)
    
    # Testar conexão
    success &= test_connection(database_url, args.verbose)
    
    # Testar CRUD se solicitado
    if args.test_crud and success:
        success &= test_crud_operations(database_url, args.verbose)
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Todos os testes executados com sucesso!")
        print("\n💡 Próximos passos:")
        print("   - Execute pytest para testes automatizados")
        print("   - Teste a aplicação: docker-compose up")
        print("   - Acesse http://localhost:8000/docs para Swagger")
        sys.exit(0)
    else:
        print("❌ Alguns testes falharam. Verifique as configurações e tente novamente.")
        sys.exit(1)


if __name__ == "__main__":
    main()