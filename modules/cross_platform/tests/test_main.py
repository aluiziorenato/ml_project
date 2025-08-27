import pytest
from fastapi.testclient import TestClient
from modules.cross_platform.app.main import app

client = TestClient(app)

def test_platform_performance():
    response = client.get("/api/platform-performance")
    assert response.status_code == 200
    assert "platforms" in response.json()
