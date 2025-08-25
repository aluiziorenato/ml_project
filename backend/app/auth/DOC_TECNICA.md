# 🔐 Documentação Técnica — Módulo Auth

Este módulo implementa autenticação e autorização de usuários, incluindo geração e validação de tokens JWT.

---

## 🔹 Finalidade

- Proteger rotas da API com autenticação baseada em token.
- Validar credenciais de login.
- Gerar tokens seguros para sessões autenticadas.

---

## 🔹 Estrutura

- `auth.py`: lógica de autenticação (login, verificação de senha).
- `dependencies.py`: dependências para rotas protegidas (ex: `get_current_user`).

---

## 🔹 Código relevante

### Geração de token (`auth.py`)
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

### Verificação de usuário (`dependencies.py`)
```python
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    return get_user_by_id(user_id)
```

---

## 🔹 Observações

- O token é gerado com tempo de expiração e assinado com `SECRET_KEY`.
- A dependência `get_current_user` pode ser usada em qualquer rota protegida.
- O uso de `OAuth2PasswordBearer` permite integração com Swagger UI.

---

Criado por Aluizio Renato
