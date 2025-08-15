import pytest
import sys
import os

# Add the parent directory to the Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_campaign_request():
    """Sample campaign request for testing"""
    return {
        "product_name": "iPhone 15 Pro",
        "category": "electronics",
        "budget": 1000.0,
        "duration_days": 30,
        "target_audience": "young_adults",
        "keywords": ["iphone", "smartphone", "apple", "mobile"]
    }

@pytest.fixture
def sample_campaign_update():
    """Sample campaign update for testing"""
    return {
        "budget": 1500.0,
        "duration_days": 45,
        "status": "paused"
    }