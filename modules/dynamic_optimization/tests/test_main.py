import pytest
from fastapi.testclient import TestClient
from modules.dynamic_optimization.app.main import app

client = TestClient(app)

def test_optimize_title():
    payload = {
        "original_title": "Smartphone Samsung Galaxy",
        "category": "electronics",
        "keywords": ["smartphone", "samsung", "galaxy"],
        "target_audience": "young_adults",
        "current_ctr": 0.12,
        "optimization_goal": "ctr"
    }
    response = client.post("/api/optimize-title", json=payload)
    assert response.status_code == 200
    assert "best_title" in response.json()


def test_optimize_price():
    payload = {
        "product_title": "Smartphone Samsung Galaxy",
        "category": "electronics",
        "current_price": 1200,
        "keywords": ["smartphone", "samsung", "galaxy"],
        "competitor_prices": [1100, 1250, 1300],
        "target_margin": 0.15
    }
    response = client.post("/api/optimize-price", json=payload)
    assert response.status_code == 200
    assert "optimal_price" in response.json()
