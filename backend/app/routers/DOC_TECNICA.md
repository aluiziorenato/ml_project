# 🌐 Documentação Técnica — Módulo Routers

Este módulo organiza as rotas da aplicação FastAPI por funcionalidade, separando endpoints em arquivos distintos para facilitar manutenção e escalabilidade.

---

## 🔹 Finalidade

- Centralizar e modularizar os endpoints da API.
- Facilitar o versionamento e a separação por domínio (ex: produtos, usuários, autenticação).

---

## 🔹 Estrutura

Cada arquivo `.py` dentro de `routers/` representa um conjunto de rotas relacionadas a um recurso específico.

Exemplo:
- `auth.py`: rotas de autenticação
- `products.py`: rotas de produtos (se existirem)
- `main.py`: ponto de entrada que inclui todos os routers

---

## 🔹 Código relevante

### Inclusão de rotas no `main.py`
```python
from fastapi import APIRouter
from .auth import router as auth_router

router = APIRouter()
router.include_router(auth_router, prefix="/auth", tags=["auth"])
```

### Exemplo de rota em `auth.py`
```python
@router.post("/login")
def login(user: UserLogin):
    # lógica de autenticação
    return {"access_token": "token"}
```

---

## 🔹 Observações

- Todas as rotas devem ser registradas no `main.py` para serem incluídas na aplicação.
- O uso de `tags` facilita a organização da documentação Swagger.
- Prefixos como `/auth`, `/products` ajudam na clareza da API.

---

Criado por Aluizio Renato
