# 🔧 Documentação Técnica — Serviços Mercado Libre

Este módulo implementa a comunicação com a API do Mercado Libre.

---

## 🔹 Finalidade

- Buscar dados do usuário autenticado
- Listar produtos do vendedor
- Utilizar token OAuth2 para chamadas autenticadas

---

## 🔹 Funções

### `get_user_info(token: str)`

#### Para que serve
Retorna dados do perfil do usuário autenticado.

#### Código relevante
```python
async def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ML_API_URL}/users/me", headers=headers)
        return response.json()
```

---

### `get_products(token: str)`

#### Para que serve
Retorna lista de produtos do vendedor autenticado.

#### Código relevante
```python
async def get_products(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{ML_API_URL}/users/me/products", headers=headers)
        return response.json()
```

---

Criado por Aluizio Renato
