"""
Integration test configuration with PostgreSQL database.
"""
import os
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import httpx

from app.main import app
from app.db import get_session
from app.models import User, OAuthToken, OAuthSession, ApiEndpoint
from app.core.security import get_password_hash, create_access_token


# Database configuration - use SQLite for local dev, PostgreSQL for CI
def get_test_database_url():
    """Get test database URL based on environment."""
    if os.getenv("CI") or os.getenv("USE_POSTGRES"):
        return os.getenv(
            "DATABASE_URL", 
            "postgresql+psycopg2://test_user:test_password@localhost:5432/test_db"
        )
    else:
        # Use in-memory SQLite for local development
        return "sqlite:///./test_db.sqlite"


TEST_DATABASE_URL = get_test_database_url()


@pytest.fixture(name="test_engine")
def test_engine_fixture():
    """Create database engine for testing."""
    if "sqlite" in TEST_DATABASE_URL:
        # SQLite configuration
        engine = create_engine(
            TEST_DATABASE_URL,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False
        )
    else:
        # PostgreSQL configuration
        engine = create_engine(TEST_DATABASE_URL, echo=False)
    return engine


@pytest.fixture(name="pg_session")
def pg_session_fixture(test_engine):
    """Create database session for testing."""
    # Create all tables
    SQLModel.metadata.create_all(test_engine)
    
    with Session(test_engine) as session:
        yield session
    
    # Clean up - drop all tables after test
    SQLModel.metadata.drop_all(test_engine)


@pytest.fixture(name="pg_client")
def pg_client_fixture(pg_session: Session):
    """Create test client with database session."""
    def get_session_override():
        return pg_session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="pg_async_client")
async def pg_async_client_fixture(pg_session: Session) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Create async test client with database session."""
    def get_session_override():
        return pg_session

    app.dependency_overrides[get_session] = get_session_override
    
    async with httpx.AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture(name="pg_test_user")
def pg_test_user_fixture(pg_session: Session) -> User:
    """Create a test user in database."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword"),
        is_active=True
    )
    pg_session.add(user)
    pg_session.commit()
    pg_session.refresh(user)
    return user


@pytest.fixture(name="pg_test_admin_user")
def pg_test_admin_user_fixture(pg_session: Session) -> User:
    """Create a test admin user in database."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword"),
        is_active=True,
        is_superuser=True
    )
    pg_session.add(user)
    pg_session.commit()
    pg_session.refresh(user)
    return user


@pytest.fixture(name="pg_access_token")
def pg_access_token_fixture(pg_test_user: User) -> str:
    """Generate access token for test user."""
    return create_access_token({"sub": pg_test_user.email})


@pytest.fixture(name="pg_admin_access_token")
def pg_admin_access_token_fixture(pg_test_admin_user: User) -> str:
    """Generate access token for admin user."""
    return create_access_token({"sub": pg_test_admin_user.email})


@pytest.fixture(name="pg_auth_headers")
def pg_auth_headers_fixture(pg_access_token: str) -> dict:
    """Generate authentication headers."""
    return {"Authorization": f"Bearer {pg_access_token}"}


@pytest.fixture(name="pg_admin_auth_headers")
def pg_admin_auth_headers_fixture(pg_admin_access_token: str) -> dict:
    """Generate admin authentication headers."""
    return {"Authorization": f"Bearer {pg_admin_access_token}"}


@pytest.fixture(name="oauth_session_data")
def oauth_session_data_fixture(pg_session: Session) -> OAuthSession:
    """Create OAuth session data for testing."""
    oauth_session = OAuthSession(
        state="test_state_123",
        code_verifier="test_code_verifier",
        endpoint_id=1
    )
    pg_session.add(oauth_session)
    pg_session.commit()
    pg_session.refresh(oauth_session)
    return oauth_session


@pytest.fixture(name="oauth_token_data")
def oauth_token_data_fixture(pg_session: Session, pg_test_user: User) -> OAuthToken:
    """Create OAuth token data for testing."""
    oauth_token = OAuthToken(
        user_id=pg_test_user.id,
        access_token="APP_USR-test-access-token",
        refresh_token="TG-test-refresh-token",
        token_type="Bearer",
        expires_in=21600,
        scope="offline_access read write"
    )
    pg_session.add(oauth_token)
    pg_session.commit()
    pg_session.refresh(oauth_token)
    return oauth_token


# Mock data fixtures for external API testing
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
        "status": {
            "site_status": "active"
        }
    }


@pytest.fixture
def mock_ml_products():
    """Mock Mercado Libre products for testing."""
    return {
        "results": [
            "MLB123456789",
            "MLB987654321",
            "MLB555666777"
        ],
        "paging": {
            "total": 3,
            "offset": 0,
            "limit": 50
        }
    }


@pytest.fixture
def mock_ml_categories():
    """Mock Mercado Libre categories for testing."""
    return [
        {"id": "MLB1132", "name": "Telefones e Celulares"},
        {"id": "MLB1144", "name": "Eletrodomésticos"},
        {"id": "MLB1196", "name": "Música, Filmes e Seriados"},
        {"id": "MLB1051", "name": "Livros, Revistas e Comics"},
        {"id": "MLB1367", "name": "Beleza e Cuidado Pessoal"}
    ]


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()