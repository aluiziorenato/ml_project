import pytest
from fastapi.testclient import TestClient
from modules.seo_intelligence.app.main import app

client = TestClient(app)

def test_seo_inference():
    payload = {
        "url": "https://site.com",
        "keyword": "otimização"
    }
    response = client.post("/api/seo-inference", json=payload)
    assert response.status_code == 200
    assert "score" in response.json()
    assert "recommendations" in response.json()
