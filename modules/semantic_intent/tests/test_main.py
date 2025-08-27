import pytest
from fastapi.testclient import TestClient
from modules.semantic_intent.app.main import app

client = TestClient(app)

def test_intent_analysis():
    payload = {"text": "Quero comprar um celular"}
    response = client.post("/api/intent-analysis", json=payload)
    assert response.status_code == 200
    assert "intent" in response.json()
    assert "type" in response.json()["intent"]
    assert "confidence" in response.json()["intent"]
