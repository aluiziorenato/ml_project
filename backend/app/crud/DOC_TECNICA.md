# 🛠️ Documentação Técnica — Módulo CRUD

Este módulo implementa operações de banco de dados usando SQLAlchemy, como criar, ler, atualizar e deletar registros.

---

## 🔹 Finalidade

- Abstrair a lógica de acesso ao banco de dados.
- Garantir reutilização e separação entre camada de dados e rotas.

---

## 🔹 Estrutura

- `db.py`: inicializa a sessão de banco de dados.
- `database.py`: configura a engine e cria as tabelas.
- Funções específicas para cada modelo podem ser adicionadas (ex: `get_user_by_email`, `create_product`).

---

## 🔹 Código relevante

### Sessão de banco (`db.py`)
```python
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Criação de usuário (`crud_user.py`)
```python
def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

---

## 🔹 Observações

- Todas as funções CRUD devem receber `db: Session` como argumento.
- A separação por modelo (`crud_user.py`, `crud_product.py`) é recomendada para organização.
- O uso de `SessionLocal` garante controle transacional.

---

Criado por Aluizio Renato
