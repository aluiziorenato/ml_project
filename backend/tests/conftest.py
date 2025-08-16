"""
Test configuration and fixtures.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import httpx

from app.main import app
from app.db import get_session
from app.models import User
from app.core.security import get_password_hash, create_access_token
from app.settings import Settings


@pytest.fixture(scope="session")
def settings():
    return Settings(
        database_url="sqlite:///:memory:",
        testing=True,
        secret_key="test_secret_key",
        ml_client_id="test_client_id",
        ml_client_secret="test_client_secret"
    )


@pytest.fixture(scope="session")
def engine(settings):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


# Create in-memory SQLite database for testing
@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session, settings):
    def get_session_override():
        return session

    def get_settings_override():
        return settings

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="async_client")
async def async_client_fixture(session: Session, settings) -> AsyncGenerator[httpx.AsyncClient, None]:
    def get_session_override():
        return session

    def get_settings_override():
        return settings

    app.dependency_overrides[get_session] = get_session_override
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="test_admin_user")
def test_admin_user_fixture(session: Session) -> User:
    """Create a test admin user."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture(name="access_token")
def access_token_fixture(test_user: User) -> str:
    """Generate access token for test user."""
    return create_access_token({"sub": test_user.email})


@pytest.fixture(name="admin_access_token")
def admin_access_token_fixture(test_admin_user: User) -> str:
    """Generate access token for admin user."""
    return create_access_token({"sub": test_admin_user.email})


@pytest.fixture(name="auth_headers")
def auth_headers_fixture(access_token: str) -> dict:
    """Generate authentication headers."""
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(admin_access_token: str) -> dict:
    """Generate admin authentication headers."""
    return {"Authorization": f"Bearer {admin_access_token}"}


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Mock data fixtures
@pytest.fixture
def sample_seo_text():
    """Sample text for SEO optimization testing."""
    return "This is a sample product description for testing SEO optimization. It contains multiple words and should be optimized for search engines."


@pytest.fixture
def sample_categories():
    """Sample categories data for testing."""
    return [
        {"id": "MLB1132", "name": "Telefones e Celulares"},
        {"id": "MLB1144", "name": "Eletrodomésticos"},
        {"id": "MLB1196", "name": "Música, Filmes e Seriados"},
    ]


@pytest.fixture
def mock_ml_token():
    """Mock Mercado Libre token for testing."""
    return {
        "access_token": "APP_USR-123456789-test-token",
        "token_type": "Bearer",
        "expires_in": 21600,
        "scope": "offline_access read write",
        "user_id": "123456789",
        "refresh_token": "TG-123456789-test-refresh-token"
    }


@pytest.fixture
def mock_ml_user_info():
    """Mock Mercado Libre user info for testing."""
    return {
        "id": 123456789,
        "nickname": "TEST_USER",
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User",
        "country_id": "BR",
        "address": {
            "city": "São Paulo",
            "state": "SP"
        },
        "phone": {
            "area_code": "11",
            "number": "999999999"
        },
        "user_type": "normal",
        "tags": ["normal"],
        "logo": None,
        "points": 100,
        "site_id": "MLB",
        "permalink": "http://perfil.mercadolivre.com.br/TEST_USER",
        "seller_reputation": {
            "level_id": "5_green",
            "power_seller_status": "silver",
            "transactions": {
                "period": "60 days",
                "total": 200,
                "completed": 190,
                "canceled": 10,
                "ratings": {
                    "positive": 0.95,
                    "negative": 0.02,
                    "neutral": 0.03
                }
            }
        },
        "buyer_reputation": {
            "canceled_transactions": 1,
            "transactions": {
                "period": "60 days",
                "total": 50,
                "completed": 49,
                "canceled": 1,
                "unrated": {
                    "total": None,
                    "paid": None,
                    "units": None
                },
                "not_yet_rated": {
                    "total": None,
                    "paid": None,
                    "units": None
                }
            },
            "tags": []
        },
        "status": {
            "site_status": "active"
        }
    }