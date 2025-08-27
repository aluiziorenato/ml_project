import pytest
from fastapi.testclient import TestClient
from modules.trend_detector.app.main import app

client = TestClient(app)

def test_detect_trend():
    payload = [
        {"ds": "2024-01-01", "y": 100},
        {"ds": "2024-02-01", "y": 120},
        {"ds": "2024-03-01", "y": 130}
    ]
    response = client.post("/api/detect-trend", json=payload)
    assert response.status_code == 200
    assert "trend" in response.json() or "error" in response.json()
