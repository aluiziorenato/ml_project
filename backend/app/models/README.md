# 🧱 Models — ORM SQLAlchemy

Define os modelos de dados que representam as tabelas do banco de dados.

## 📌 Objetivo

- Mapear entidades do domínio para tabelas SQL.
- Facilitar manipulação de dados com SQLAlchemy.

## 📁 Estrutura

- `base.py`: base declarativa para herança.
- `user.py`, `product.py`: modelos específicos.

## 🧪 Exemplo

```python
class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    price = Column(Float)
