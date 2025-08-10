Com base no repositório principal [`ml_project`](https://github.com/aluiziorenato/ml_project) e na estrutura do diretório `backend`, aqui está a documentação completa e detalhada dos testes do projeto:

---

# 🧪 Documentação de Testes — `ml_project/backend`

Este documento descreve a estrutura, ferramentas, escopo e boas práticas adotadas para os testes automatizados do backend do projeto `ml_project`.

---

## 🧰 Ferramentas Utilizadas

- **Pytest**: framework principal para testes unitários e de integração.
- **FastAPI TestClient**: simula chamadas HTTP à API.
- **PostgreSQL (via Docker)**: banco de dados real para testes de integração.
- **Coverage.py** (opcional): mede cobertura de código.

---

## 📁 Estrutura dos Testes

Os testes estão localizados em:

```
backend/app/tests/
```

### Organização sugerida:

```
tests/
├── __init__.py
├── test_auth.py          # Testes de autenticação OAuth
├── test_products.py      # Testes de rotas de produtos
├── test_services.py      # Testes de integração com Mercado Libre
├── conftest.py           # Fixtures globais
```

---

## 🧪 Exemplos de Testes

### 🔐 Teste de Autenticação

```python
def test_login_redirect(client):
    response = client.get("/api/oauth/login")
    assert response.status_code == 307  # Redirecionamento para Mercado Libre
```

---

### 📦 Teste de Criação de Produto

```python
def test_create_product(client, token):
    payload = {
        "title": "Produto Teste",
        "price": 99.90,
        "category": "Eletrônicos"
    }
    response = client.post("/products", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert response.json()["message"] == "Produto criado com sucesso"
```

---

## ⚙️ Como Executar os Testes

### Ambiente local (sem Docker):

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

### Com cobertura:

```bash
pytest --cov=app --cov-report=term-missing
```

---

## 🧪 Tipos de Testes

| Tipo              | Descrição                                      |
|-------------------|-----------------------------------------------|
| Unitário          | Testa funções isoladas (ex: validação de dados) |
| Integração        | Testa comunicação entre módulos (ex: API + DB) |
| Funcional         | Testa comportamento completo de uma rota       |
| Externo (mockado) | Simula chamadas à API do Mercado Libre         |

---

## 🧱 Boas Práticas

- Use **fixtures** para setup de dados e autenticação.
- Teste **casos positivos e negativos**.
- Mantenha os testes **rápidos e independentes**.
- Nomeie os testes com clareza (`test_create_product_success`, `test_invalid_token`).
- Evite dependência entre testes.

---

## ✅ Status Atual

- [x] Testes básicos de autenticação
- [x] Testes de rotas de produtos
- [ ] Testes de integração com Mercado Libre
- [ ] Testes de falhas e erros
- [ ] Cobertura mínima de 80%
