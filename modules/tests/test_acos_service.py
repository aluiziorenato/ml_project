import pytest
from fastapi.testclient import TestClient
from modules.acos_service.app.main import app

client = TestClient(app)

def test_optimize_acos():
    payload = {
        "campaign_id": "camp1",
        "spend": 100,
        "sales": 500,
        "target_acos": 0.2
    }
    response = client.post("/api/optimize-acos", json=payload)
    assert response.status_code == 200
    assert "optimized_bid" in response.json()
    assert "expected_acos" in response.json()
