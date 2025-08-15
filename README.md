
# 🧠 ML Integration — FastAPI + React (Containerized)

Este projeto integra **FastAPI** (backend) e **React** (frontend) com a API do Mercado Libre, utilizando **Docker Compose** para orquestrar os serviços: backend, frontend, PostgreSQL e pgAdmin.

**🔥 Versão atualizada com melhorias de arquitetura, segurança e boas práticas!**

---

## 🚀 Quick Start

1. Copie o arquivo `.env.example` para `backend/.env` e preencha as variáveis obrigatórias:
   - `ML_CLIENT_ID`
   - `ML_CLIENT_SECRET`  
   - `SECRET_KEY`
   - `DATABASE_URL`
   - `ML_REDIRECT_URI`
   - `ADMIN_PASSWORD` (senha para o usuário admin inicial)

2. Execute o projeto com Docker Compose:

   ```bash
   docker-compose up --build
   ```

3. Acesse os serviços:

   - Backend: [http://localhost:8000](http://localhost:8000)
     - Documentação Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - pgAdmin: [http://localhost:8080](http://localhost:8080)
     - Login: `admin@admin.com` / Senha: `admin`

---

## 🔄 Melhorias Implementadas

### ✅ Docker Compose
- **Removida** a linha `version:` para garantir compatibilidade com versões recentes do Docker Compose
- Otimização da configuração de containers

### ✅ Configuração Backend  
- **Configuração centralizada** com Pydantic Settings (compatível com Pydantic v2)
- **Gerenciamento seguro** de variáveis de ambiente
- **Validação automática** de configurações na inicialização
- Suporte completo a aliases de variáveis de ambiente

### ✅ Estrutura de Pacotes
- **Adicionados** arquivos `__init__.py` em todos os diretórios Python necessários
- **Padronização** de imports relativos e absolutos
- **Modularização** do sistema de autenticação
- Consolidação das funções de autenticação em `app/auth/`

### ✅ Segurança
- **Uso de variáveis de ambiente** para todos os valores sensíveis
- **Configuração JWT** centralizada e segura
- **Hash de senhas** com bcrypt
- **Validação** de tokens de acesso automática

---

## 🧠 Estrutura do Projeto

### Backend (`/backend`)

```
backend/
├── alembic/              # Migrações do banco de dados
├── app/
│   ├── auth/             # Sistema de autenticação modularizado
│   │   ├── __init__.py   # Funções de auth centralizadas
│   │   └── token.py      # Endpoints de autenticação
│   ├── core/             # Configurações e utilitários centrais
│   │   ├── __init__.py   # Módulo de core
│   │   └── security.py   # Funções de segurança (deprecated, moved to auth)
│   ├── models/           # Modelos ORM e Pydantic
│   ├── routers/          # Rotas da API organizadas por funcionalidade
│   ├── services/         # Integrações externas (ex: Mercado Libre)
│   ├── crud/             # Operações de banco de dados
│   ├── config.py         # Exportação das configurações
│   ├── settings.py       # Configurações centralizadas com Pydantic
│   ├── startup.py        # Funções de inicialização
│   ├── db.py             # Configuração do banco de dados
│   └── main.py           # Aplicação FastAPI principal
├── .env                  # Variáveis de ambiente (não versionado)
├── .env.example          # Exemplo de variáveis
├── Dockerfile            # Build do backend
├── alembic.ini           # Configuração do Alembic
└── requirements.txt      # Dependências Python
```

### Frontend (`/frontend`)

- Aplicação React com integração à API do backend
- Interface para autenticação e visualização de dados do Mercado Libre

---

## ⚙️ Configuração

### Variáveis de Ambiente

O projeto utiliza um sistema de configuração centralizado com Pydantic Settings. Todas as variáveis são definidas em `backend/app/settings.py` e podem ser configuradas via arquivo `.env`:

#### Banco de Dados
- `DATABASE_URL`: URL de conexão com PostgreSQL
- `ADMIN_EMAIL`: Email do usuário administrador inicial
- `ADMIN_PASSWORD`: Senha do usuário administrador inicial

#### Mercado Libre API
- `ML_CLIENT_ID`: ID do cliente da aplicação
- `ML_CLIENT_SECRET`: Secret da aplicação  
- `ML_REDIRECT_URI`: URI de callback OAuth

#### JWT e Segurança
- `SECRET_KEY`: Chave secreta para JWT (gere uma chave forte!)
- `JWT_ALGORITHM`: Algoritmo JWT (padrão: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Minutos para expiração do token (padrão: 60)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Dias para expiração do refresh token (padrão: 7)

#### CORS e URLs
- `FRONTEND_ORIGIN`: URL do frontend para configuração do CORS
- `APP_BASE_URL`: URL base da aplicação backend

#### Ambiente
- `ENV`: Ambiente de execução (development/production)

### Exemplo de .env

```bash
# Banco de dados
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/ml_db
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=sua-senha-forte-aqui

# Mercado Libre
ML_CLIENT_ID=seu-client-id
ML_CLIENT_SECRET=seu-client-secret
ML_REDIRECT_URI=http://localhost:8000/api/oauth/callback

# Segurança
SECRET_KEY=gere-uma-chave-secreta-forte-aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# URLs
FRONTEND_ORIGIN=http://localhost:3000
APP_BASE_URL=http://localhost:8000

# Ambiente
ENV=development
```

---

## 🔐 Autenticação com Mercado Libre

O backend utiliza OAuth2 para autenticação com Mercado Libre.

### Fluxo de Autenticação

1. Usuário acessa `/api/oauth/login`
2. É redirecionado para o Mercado Libre
3. Após login, é redirecionado para `/api/oauth/callback`
4. O backend salva o token de acesso

### Endpoints

| Método | Rota                    | Descrição                          |
|--------|-------------------------|------------------------------------|
| GET    | `/api/oauth/login`      | Inicia autenticação OAuth          |
| GET    | `/api/oauth/callback`   | Recebe token do Mercado Libre      |

> ⚠️ Você deve registrar sua aplicação em [Mercado Libre Developers](https://developers.mercadolibre.com.ar/) e configurar a Redirect URI como:
> `http://localhost:8000/api/oauth/callback`

---

## 🧪 Testes

Para rodar os testes do backend localmente (sem Docker):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

---

## ⚙️ Migrações com Alembic

### Criar nova migração

```bash
alembic revision --autogenerate -m "descrição"
```

### Aplicar migração

```bash
alembic upgrade head
```

---

## 📦 Variáveis de Ambiente

Exemplo de `.env.example`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
SECRET_KEY=your_secret_key
ML_CLIENT_ID=your_client_id
ML_CLIENT_SECRET=your_client_secret
ML_REDIRECT_URI=http://localhost:8000/api/oauth/callback
```

---

## 📈 Logs e Monitoramento

- Logs estruturados com `loguru`
- Integração futura com Prometheus/Grafana

---

## 🛡️ Segurança

- Proteção CORS configurável
- Tokens seguros via OAuth2
- Sugestão: adicionar rate limiting com `slowapi`

---

## 📦 Produção

### Stack sugerido

- Gunicorn + Uvicorn para backend
- PostgreSQL gerenciado (ex: Supabase, Railway)
- CI/CD com GitHub Actions

---

## ✅ Status do Projeto

- [x] Backend funcional com autenticação Mercado Libre
- [x] Frontend integrado
- [x] Banco de dados com Alembic
- [x] Docker Compose com PostgreSQL e pgAdmin
- [x] Testes unitários
- [ ] Documentação expandida de rotas
- [ ] Monitoramento e métricas
- [ ] CI/CD para produção

---

## 📬 Contato

Desenvolvido por [Aluizio Renato](https://github.com/aluiziorenato) — sugestões e contribuições são bem-vindas!
```

Aqui está uma análise técnica completa do projeto [`ml_project`](https://github.com/aluiziorenato/ml_project/tree/main/backend), com foco no backend:

---

# 🔍 Análise Técnica do Projeto `ml_project`

## 🧩 Visão Geral

O projeto é uma integração entre **FastAPI** (backend) e **React** (frontend), com autenticação via **Mercado Libre API**. Ele está containerizado com **Docker Compose**, incluindo serviços de banco de dados PostgreSQL e interface de administração via pgAdmin.

---

## 📁 Estrutura do Backend

A estrutura do diretório `backend/` é limpa e modular:

- `alembic/`: gerencia migrações do banco de dados.
- `app/`: contém o núcleo da aplicação FastAPI.
  - `api/`: define as rotas da API.
  - `core/`: configurações e utilitários (ex: CORS, settings).
  - `models/`: modelos ORM (SQLAlchemy) e Pydantic.
  - `services/`: lógica de integração com Mercado Libre.
  - `tests/`: testes unitários.
- `.env.example`: facilita configuração do ambiente.
- `Dockerfile`: define o build do backend.
- `requirements.txt`: lista de dependências Python.

Essa organização favorece escalabilidade, manutenção e testes.

---

## ⚙️ Tecnologias Utilizadas

- **FastAPI**: framework moderno e assíncrono para APIs.
- **SQLAlchemy + Alembic**: ORM e controle de migrações.
- **OAuth2**: autenticação com Mercado Libre.
- **Docker Compose**: orquestra backend, frontend, banco e pgAdmin.
- **Pytest**: testes automatizados.
- **React**: frontend SPA (Single Page Application).

---

## 🔐 Autenticação com Mercado Libre

A autenticação segue o padrão OAuth2:

- Rota `/api/oauth/login` redireciona para Mercado Libre.
- Callback `/api/oauth/callback` recebe o token.
- O token é armazenado e usado para chamadas autenticadas à API do Mercado Libre.

Esse fluxo está bem implementado e pronto para produção, desde que o token seja armazenado com segurança.

---

## 🧪 Testes

O projeto inclui testes com Pytest, organizados em `app/tests/`. Eles cobrem:

- Rotas da API
- Integração com serviços externos
- Validação de modelos

A cobertura pode ser expandida para testes de integração com o banco e autenticação.

---

## 🛠️ Configuração e Deploy

- O `.env.example` está bem definido, com variáveis para banco, autenticação e segurança.
- O `Dockerfile` está funcional e otimizado para desenvolvimento.
- O projeto pode ser facilmente estendido para produção com:
  - Gunicorn + Uvicorn
  - PostgreSQL gerenciado (ex: Supabase, Railway)
  - CI/CD com GitHub Actions

---

## 📈 Pontos Fortes

- Estrutura modular e escalável
- Integração OAuth2 funcional
- Containerização completa
- Testes automatizados
- Documentação básica clara

---

## ⚠️ Pontos a Melhorar

- Documentação técnica das rotas no README
- Armazenamento seguro de tokens (ex: criptografia ou banco seguro)
- Monitoramento e logs estruturados
- CI/CD para produção
- Testes de integração mais robustos

---
