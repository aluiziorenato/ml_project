import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database import get_db, Base

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    """Set up test database"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "strategic-mode"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Strategic Mode Service" in data["message"]

def test_get_strategies():
    """Test get strategies endpoint"""
    response = client.get("/api/strategies/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_default_strategies():
    """Test get default strategies presets"""
    response = client.get("/api/strategies/presets/default")
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data
    assert len(data["strategies"]) == 4  # Four default strategies

def test_get_special_dates():
    """Test get special dates endpoint"""
    response = client.get("/api/special-dates/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_default_special_dates():
    """Test get default special dates presets"""
    response = client.get("/api/special-dates/presets/default")
    assert response.status_code == 200
    data = response.json()
    assert "special_dates" in data
    assert len(data["special_dates"]) >= 5  # At least 5 default special dates

def test_integration_status():
    """Test integration status endpoint"""
    response = client.get("/api/integrations/status")
    assert response.status_code == 200
    data = response.json()
    assert "services" in data
    assert "overall_status" in data

if __name__ == "__main__":
    pytest.main([__file__])