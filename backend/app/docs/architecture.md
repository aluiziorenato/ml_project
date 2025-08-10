
# 🧩 Arquitetura do Projeto — ML Integration

Este documento descreve a arquitetura técnica do projeto `ml_project`, que integra um backend em FastAPI com um frontend em React, utilizando autenticação via Mercado Libre e serviços containerizados com Docker Compose.

---

## 📐 Visão Geral

O projeto é composto por quatro serviços principais:

- **Backend (FastAPI)**: API RESTful com autenticação OAuth2 e integração com Mercado Libre.
- **Frontend (React)**: Interface SPA que consome os dados da API.
- **Banco de Dados (PostgreSQL)**: Armazena dados persistentes e tokens.
- **pgAdmin**: Interface web para administração do banco.

Todos os serviços são orquestrados via Docker Compose.

---

## 🔄 Fluxo de Dados

```plaintext
Usuário → Frontend → Backend → Mercado Libre API
                             ↘ PostgreSQL
```

1. O usuário acessa o frontend.
2. O frontend redireciona para o backend para autenticação.
3. O backend inicia o fluxo OAuth2 com Mercado Libre.
4. Após autenticação, o backend recebe o token e armazena no banco.
5. O frontend consome dados protegidos via API.

---

## 🧱 Componentes Técnicos

### 🔹 Backend (FastAPI)

- Framework assíncrono e leve
- Rotas organizadas em `app/api`
- Integração com Mercado Libre via OAuth2
- Modelos SQLAlchemy e Pydantic
- Migrações com Alembic
- Testes com Pytest

### 🔹 Frontend (React)

- SPA moderna
- Comunicação com backend via fetch/axios
- Interface para login e visualização de dados

### 🔹 Banco de Dados (PostgreSQL)

- Persistência de dados
- Armazenamento de tokens de acesso
- Gerenciado via pgAdmin

### 🔹 pgAdmin

- Interface web para gerenciar PostgreSQL
- Acesso via `http://localhost:8080`

---

## 🔐 Autenticação OAuth2

- O backend inicia o fluxo via `/api/oauth/login`
- O usuário é redirecionado para Mercado Libre
- Após login, o backend recebe o token via `/api/oauth/callback`
- O token é armazenado e utilizado para chamadas autenticadas

---

## ⚙️ Containerização

Todos os serviços são definidos no `docker-compose.yml`:

- `backend`: roda FastAPI com Uvicorn
- `frontend`: roda React com Node
- `db`: PostgreSQL
- `pgadmin`: interface de administração

Volumes e redes são configurados para persistência e comunicação entre serviços.

---

## 📈 Escalabilidade e Extensibilidade

- Separação clara entre camadas (API, serviços, modelos)
- Fácil adição de novos endpoints e integrações
- Possibilidade de escalar com Gunicorn + Uvicorn
- Pronto para deploy em cloud (ex: Railway, Render)

---

## 🛡️ Segurança

- Tokens protegidos via OAuth2
- Uso de `SECRET_KEY` para criptografia
- Sugestão: adicionar rate limiting e criptografia de tokens

---

## 📦 Requisitos para Produção

- Configuração de variáveis seguras (.env)
- Banco de dados gerenciado
- CI/CD com GitHub Actions
- Monitoramento com Prometheus/Grafana (opcional)

---

## 📌 Conclusão

A arquitetura do projeto é moderna, modular e preparada para produção. A separação entre serviços, o uso de containers e a integração com Mercado Libre tornam o projeto escalável e fácil de manter.
