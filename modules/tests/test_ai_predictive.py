import pytest
from fastapi.testclient import TestClient
from modules.ai_predictive.app.main import app

client = TestClient(app)

def test_predict_seasonal_demand():
    payload = {
        "product_category": "electronics",
        "keywords": ["smartphone"]
    }
    response = client.post("/api/predict-seasonal-demand", json=payload)
    assert response.status_code == 200
    assert "prediction" in response.json()
