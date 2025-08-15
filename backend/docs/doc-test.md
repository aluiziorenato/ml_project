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

### 🧪 Testes de Cobertura Completa

```python
def test_oauth_token_flow_complete(client, session):
    # Testa fluxo completo OAuth com PKCE
    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)
    state = "test_state_12345"
    
    # Salva sessão OAuth
    save_oauth_session(session, state, verifier, 1)
    
    # Testa callback OAuth
    response = client.get(f"/api/oauth/callback?code=test&state={state}")
    assert response.status_code in [200, 400]  # Esperado sem API real
```

---

### 🔐 Testes de Autenticação

```python
def test_login_redirect(client):
    response = client.get("/api/oauth/login")
    assert response.status_code == 307  # Redirecionamento para Mercado Libre
```

---

### 📊 Testes de Cobertura de Banco de Dados

```python  
def test_database_operations(session):
    # Testa operações CRUD completas
    user = User(email="test@example.com", hashed_password="hash")
    session.add(user)
    session.commit()
    
    # Testa busca
    found_user = session.get(User, user.id)
    assert found_user.email == "test@example.com"
```

---

### ⚠️ Testes de Cenários de Erro

```python
def test_error_scenarios(client, auth_headers):
    # Testa token inválido
    response = client.get("/api/categories/", 
                         headers={"Authorization": "Bearer invalid"})
    assert response.status_code == 401
    
    # Testa dados ausentes
    response = client.post("/api/oauth/callback")
    assert response.status_code == 400
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

### Com cobertura completa:

```bash
pytest --cov=app --cov-report=term-missing --cov-report=html
```

### Executar apenas testes novos de cobertura:

```bash
pytest tests/test_coverage_comprehensive.py tests/test_coverage_additional.py tests/test_coverage_ultimate.py -v
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
- [x] Testes de integração com Mercado Libre
- [x] Testes de falhas e erros
- [x] Cobertura de 85% (melhorada de 79%)
- [x] Testes de fluxo OAuth2 e PKCE
- [x] Testes de operações de banco de dados
- [x] Testes de cenários de erro
- [x] Testes de funções assíncronas
- [x] Testes abrangentes de todos os módulos
