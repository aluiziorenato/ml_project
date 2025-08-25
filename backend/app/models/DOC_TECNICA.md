# 🧱 Documentação Técnica — Modelos e Esquemas

Este módulo define os modelos ORM (SQLAlchemy) e os esquemas de validação (Pydantic).

---

## 🔹 Finalidade

- Representar tabelas do banco de dados
- Validar dados de entrada e saída da API

---

## 🔹 Arquivos

### `models.py`

#### Para que serve
Define estrutura das tabelas no banco via SQLAlchemy.

#### Código relevante
```python
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
```

---

### `schemas.py`

#### Para que serve
Define os modelos de dados usados nas rotas da API.

#### Código relevante
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
```

---

Criado por Aluizio Renato
