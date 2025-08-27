import pytest
from fastapi.testclient import TestClient
from modules.market_pulse.app.main import app

client = TestClient(app)

def test_classify_keyword():
    payload = {"heat": 0.8, "volume": 1200, "keyword": "smartphone"}
    response = client.post("/api/classify-keyword", json=payload)
    assert response.status_code == 200
    assert "classification" in response.json()
    assert "confidence" in response.json()
