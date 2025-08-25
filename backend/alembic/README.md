# 📦 Alembic — Migrações de Banco de Dados

Esta pasta contém os scripts de migração gerados pelo Alembic, utilizados para versionar e aplicar alterações no schema do banco de dados PostgreSQL.

## 📌 Objetivo

- Controlar a evolução do banco de dados de forma segura e rastreável.
- Permitir que múltiplos ambientes (dev, staging, prod) mantenham consistência no schema.

## 📁 Estrutura

- `versions/`: scripts de migração com identificadores únicos.
- `env.py`: configurações para geração e execução de migrações.
- `script.py.mako`: template para novos arquivos de migração.

## ⚙️ Comandos Essenciais

- Criar nova migração:
  ```bash
  alembic revision --autogenerate -m "descrição da mudança"

🔗 Configuração
A conexão com o banco é definida em alembic.ini e referenciada em env.py. Certifique-se de que DATABASE_URL esteja corretamente configurado no .env.