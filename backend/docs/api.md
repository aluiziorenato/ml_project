Aqui está o conteúdo completo para o arquivo `docs/api.md`, com base na estrutura típica de uma API FastAPI e nos arquivos presentes no diretório [`ml_project/backend`](https://github.com/aluiziorenato/ml_project/tree/main/backend):

---

```markdown
# 📚 Documentação da API

Este documento descreve os principais endpoints da API do projeto `ml_project/backend`, incluindo autenticação, operações com produtos e exemplos de uso.

---

## 🔐 Autenticação

A API utiliza autenticação via token JWT. Para acessar endpoints protegidos, inclua o header:

```http
Authorization: Bearer <seu_token>
```

---

## 📦 Endpoints de Produtos

### `GET /products/{product_id}`

Retorna os dados de um produto específico.

- **Parâmetros:**
  - `product_id` (int): ID do produto
- **Resposta:**
  ```json
  {
    "id": 123,
    "title": "Produto Exemplo",
    "price": 99.90,
    "category": "Eletrônicos"
  }
  ```

---

### `POST /products`

Cria um novo produto.

- **Body (JSON):**
  ```json
  {
    "title": "Novo Produto",
    "price": 49.90,
    "category": "Livros"
  }
  ```
- **Resposta:**
  ```json
  {
    "id": 124,
    "message": "Produto criado com sucesso"
  }
  ```

---

### `PUT /products/{product_id}`

Atualiza os dados de um produto existente.

- **Parâmetros:**
  - `product_id` (int): ID do produto
- **Body (JSON):**
  ```json
  {
    "title": "Produto Atualizado",
    "price": 59.90
  }
  ```
- **Resposta:**
  ```json
  {
    "message": "Produto atualizado com sucesso"
  }
  ```

---

### `DELETE /products/{product_id}`

Remove um produto do sistema.

- **Parâmetros:**
  - `product_id` (int): ID do produto
- **Resposta:**
  ```json
  {
    "message": "Produto removido com sucesso"
  }
  ```

---

## 🔐 Endpoints de Autenticação

### `POST /auth/login`

Autentica o usuário e retorna o token JWT.

- **Body (JSON):**
  ```json
  {
    "username": "usuario",
    "password": "senha"
  }
  ```
- **Resposta:**
  ```json
  {
    "access_token": "jwt_token",
    "token_type": "bearer"
  }
  ```

---

## 🧪 Exemplos com `curl`

### Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123456"}'
```

### Criar Produto

```bash
curl -X POST http://localhost:8000/products \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Livro", "price": 29.90, "category": "Educação"}'
```

---

## 📎 Observações

- Todos os endpoints seguem o padrão REST.
- Os dados são retornados em formato JSON.
- Para testes locais, utilize o comando `uvicorn app.main:app --reload`.
