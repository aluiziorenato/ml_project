
---

## 📁 app/core/README.md

```markdown
# ⚙️ Core — Configurações Globais

Esta pasta centraliza configurações e utilitários usados em toda a aplicação.

## 📌 Objetivo

- Carregar variáveis de ambiente.
- Configurar segurança, CORS, logs e inicializações globais.

## 📁 Componentes

- `config.py`: carrega `.env` usando Pydantic.
- `security.py`: funções de autenticação, geração de tokens.
- `logging.py`: configuração de logs estruturados (ex: Loguru).

## 🔐 Segurança

- Tokens JWT são gerados e validados aqui.
- Funções de hash e verificação de senha podem ser incluídas.

## 🧠 Boas Práticas

- Nunca exponha segredos diretamente no código.
- Centralize configurações para facilitar manutenção.
- Use `BaseSettings` do Pydantic para validação automática.
