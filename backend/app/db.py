# backend/app/db.py
from time import sleep
from typing import Generator
from sqlmodel import create_engine, SQLModel, Session, select
from sqlalchemy.exc import OperationalError

from app.config import settings

# Engine usado por toda a app
engine = create_engine(settings.database_url, echo=False)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency generator para rotas - use: Depends(get_session)
    """
    with Session(engine) as session:
        yield session

def _wait_for_db(max_retries: int = 10, delay: float = 1.0):
    """
    Tenta efetuar uma conexão simples com o banco até obter sucesso,
    para lidar com a janela de startup do container Postgres.
    """
    last_exc = None
    for _ in range(max_retries):
        try:
            with engine.connect() as conn:
                conn.execute(select(1))  # apenas para forçar a conexão
            return
        except OperationalError as e:
            last_exc = e
            sleep(delay)
    # se não conseguiu, re-raise para que o processo falhe com erro útil
    raise last_exc or RuntimeError("Could not connect to database")

def init_db():
    """
    Cria as tabelas (se não existirem) e cria um usuário admin de teste
    caso não exista. Chamado na startup da aplicação.
    """
    # espera DB ficar pronto (melhora estabilidade no Docker)
    _wait_for_db(max_retries=20, delay=1.0)

    # importa modelos aqui (evita import circular)
    from app.models import User

    # cria tabelas
    SQLModel.metadata.create_all(engine)

    # cria usuário admin padrão se não existir
    with Session(engine) as session:
        existing = session.exec(select(User).where(User.email == settings.admin_email)).first()
        if not existing and settings.admin_password:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed = pwd_context.hash(settings.admin_password)
            user = User(email=settings.admin_email, hashed_password=hashed, is_superuser=True)
            session.add(user)
            session.commit()
            print(f"Created default admin user: {settings.admin_email}")
