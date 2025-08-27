import pytest
from fastapi.testclient import TestClient
from modules.roi_prediction.app.main import app

client = TestClient(app)

def test_predict_roi():
    payload = {"investimento": 1000, "cliques": 500, "conversoes": 50, "impressoes": 10000}
    response = client.post("/api/predict-roi", json=payload)
    assert response.status_code == 200
    assert "roi_prediction" in response.json() or "error" in response.json()
