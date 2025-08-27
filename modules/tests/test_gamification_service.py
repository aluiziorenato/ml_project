import pytest
from fastapi.testclient import TestClient
from modules.gamification_service.app.main import app

client = TestClient(app)

def test_gamification_score():
    payload = {
        "user_id": "user1",
        "activity_score": 80,
        "engagement": 0.7
    }
    response = client.post("/api/gamification-score", json=payload)
    assert response.status_code == 200
    assert "cluster" in response.json()
    assert "score" in response.json()
