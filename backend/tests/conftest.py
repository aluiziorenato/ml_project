"""
Enhanced Test configuration and fixtures for comprehensive test suite.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.pool import StaticPool
import httpx
import logging
from unittest.mock import Mock, AsyncMock
import psutil
import os
from datetime import datetime, timedelta

from app.main import app
from app.db import get_session
from app.models import User
from app.core.security import get_password_hash, create_access_token
from app.settings import Settings

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def settings():
    """Test settings configuration."""
    import os
    # Override environment for testing
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    os.environ["ENV"] = "testing"
    os.environ["SECRET_KEY"] = "test_secret_key"
    os.environ["ML_CLIENT_ID"] = "test_client_id"
    os.environ["ML_CLIENT_SECRET"] = "test_client_secret"
    os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
    os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "1"
    os.environ["ADMIN_EMAIL"] = "admin@test.com"
    os.environ["ADMIN_PASSWORD"] = "test_admin_password"
    
    return Settings()


@pytest.fixture(scope="session")
def engine(settings):
    """Create test database engine."""
    if "sqlite" in settings.database_url.lower():
        engine = create_engine(
            settings.database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool
        )
    else:
        # For PostgreSQL or other databases
        engine = create_engine(settings.database_url)
        
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db(engine):
    """Database session with transaction rollback."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db, settings):
    """Enhanced test client with dependency overrides."""
    def get_test_db():
        try:
            yield db
        finally:
            logger.debug("Cleaning up test database session")

    def get_test_settings():
        return settings

    app.dependency_overrides[get_session] = get_test_db
    
    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client):
    """Authentication headers for protected endpoints."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test_user@example.com",
            "password": "test_password_123",
            "is_active": True
        }
    )
    assert response.status_code in [200, 201, 409]  # Handle existing user
    
    response = client.post(
        "/api/auth/token",
        data={"username": "test_user@example.com", "password": "test_password_123"}
    )
    if response.status_code == 200:
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    else:
        # Return dummy headers if auth not working properly
        return {"Authorization": "Bearer test_token"}


# Performance monitoring fixtures
@pytest.fixture
def memory_monitor():
    """Monitor memory usage during tests."""
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    yield {
        'initial': initial_memory,
        'process': process
    }
    
    final_memory = process.memory_info().rss
    memory_diff = (final_memory - initial_memory) / 1024 / 1024  # MB
    logger.info(f"Memory difference: {memory_diff:.2f} MB")


@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    start_time = datetime.now()
    
    yield start_time
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"Test duration: {duration:.3f} seconds")


# Enhanced Mock data fixtures
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


@pytest.fixture
def mock_ml_products():
    """Mock Mercado Libre products response."""
    return {
        "seller_id": 123456789,
        "paging": {
            "total": 150,
            "offset": 0,
            "limit": 50
        },
        "results": [
            {
                "id": "MLB123456789",
                "title": "Test Product 1",
                "category_id": "MLB1132",
                "price": 299.99,
                "currency_id": "BRL",
                "available_quantity": 10,
                "condition": "new",
                "listing_type_id": "gold_special",
                "permalink": "https://produto.mercadolivre.com.br/MLB123456789",
                "thumbnail": "https://http2.mlstatic.com/test.jpg",
                "status": "active"
            },
            {
                "id": "MLB987654321",
                "title": "Test Product 2",
                "category_id": "MLB1144",
                "price": 599.99,
                "currency_id": "BRL",
                "available_quantity": 5,
                "condition": "new",
                "listing_type_id": "gold_pro",
                "permalink": "https://produto.mercadolivre.com.br/MLB987654321",
                "thumbnail": "https://http2.mlstatic.com/test2.jpg",
                "status": "active"
            }
        ]
    }


@pytest.fixture
def mock_ml_error_responses():
    """Mock error responses from Mercado Libre API."""
    return {
        "unauthorized": {
            "message": "Invalid access token",
            "error": "forbidden",
            "status": 401,
            "cause": []
        },
        "rate_limit": {
            "message": "Too many requests",
            "error": "too_many_requests", 
            "status": 429,
            "cause": []
        },
        "server_error": {
            "message": "Internal server error",
            "error": "internal_server_error",
            "status": 500,
            "cause": []
        },
        "timeout": {
            "message": "Request timeout",
            "error": "timeout",
            "status": 408,
            "cause": []
        }
    }


# Database test fixtures
@pytest.fixture
def db_user_factory():
    """Factory for creating test users."""
    def _create_user(session: Session, **kwargs):
        default_data = {
            "email": f"user_{datetime.now().microsecond}@example.com",
            "hashed_password": get_password_hash("testpassword"),
            "is_active": True,
            "is_superuser": False
        }
        default_data.update(kwargs)
        
        user = User(**default_data)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    return _create_user


# External API mocking fixtures
@pytest.fixture
def mock_httpx_client():
    """Mock httpx client for external API calls."""
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"mocked": True}
    mock_client.get.return_value = mock_response
    mock_client.post.return_value = mock_response
    mock_client.put.return_value = mock_response
    mock_client.delete.return_value = mock_response
    return mock_client


# Load testing fixtures
@pytest.fixture
def concurrent_requests_config():
    """Configuration for concurrent request testing."""
    return {
        "max_workers": 10,
        "requests_per_worker": 5,
        "timeout": 30,
        "base_url": "http://test"
    }


# Error simulation fixtures
@pytest.fixture
def database_error_simulator():
    """Simulate database errors for testing."""
    def _simulate_error(error_type="connection"):
        if error_type == "connection":
            from sqlalchemy.exc import OperationalError
            raise OperationalError("Database connection failed", None, None)
        elif error_type == "integrity":
            from sqlalchemy.exc import IntegrityError
            raise IntegrityError("Integrity constraint violated", None, None)
        elif error_type == "timeout":
            from sqlalchemy.exc import TimeoutError
            raise TimeoutError("Database timeout")
    
    return _simulate_error


# Authentication test fixtures
@pytest.fixture
def expired_token():
    """Generate an expired JWT token for testing."""
    from datetime import datetime, timedelta
    return create_access_token(
        {"sub": "test@example.com"}, 
        expires_delta=timedelta(seconds=-1)
    )


@pytest.fixture
def invalid_token():
    """Generate an invalid JWT token for testing."""
    return "invalid.jwt.token"


# Session management fixtures  
@pytest.fixture
def oauth_session_data():
    """Mock OAuth session data for testing."""
    return {
        "state": "test_state_123",
        "code_verifier": "test_code_verifier_123",
        "redirect_uri": "http://localhost:8000/oauth/callback",
        "scope": "offline_access read write"
    }