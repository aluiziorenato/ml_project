# ⚙️ Documentação Técnica — Módulo Core

Este módulo centraliza configurações globais e inicialização da aplicação FastAPI.

---

## 🔹 Finalidade

- Gerenciar variáveis de ambiente
- Inicializar a aplicação FastAPI
- Configurar CORS, rotas e middlewares

---

## 🔹 Arquivos

### `config.py`

#### Para que serve
Carrega variáveis de ambiente usando `pydantic.BaseSettings`.

#### Código relevante
```python
class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ML_CLIENT_ID: str
    ML_CLIENT_SECRET: str
    ML_REDIRECT_URI: str
```

---

### `main.py`

#### Para que serve
Inicializa a aplicação FastAPI e registra as rotas.

#### Código relevante
```python
app = FastAPI()
app.include_router(oauth_router, prefix="/api/oauth")
```

---

Criado por Aluizio Renato
