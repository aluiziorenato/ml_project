"""
Pytest configuration and fixtures for Simulator Service tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

@pytest.fixture
def sample_campaign_request():
    """Sample campaign simulation request for testing."""
    return {
        "product_name": "Smartphone Premium Test",
        "category": "electronics",
        "budget": 2000.0,
        "duration_days": 30,
        "target_audience": "tech_enthusiasts",
        "keywords": ["smartphone", "premium", "technology", "innovation"]
    }

@pytest.fixture
def sample_historical_data():
    """Sample historical data for testing."""
    from main import HistoricalData
    return [
        HistoricalData(
            date="2024-01-01",
            impressions=1000,
            clicks=50,
            conversions=2,
            spend=100.0,
            category="MLB1051"
        ),
        HistoricalData(
            date="2024-01-02", 
            impressions=1200,
            clicks=60,
            conversions=3,
            spend=120.0,
            category="MLB1051"
        ),
        HistoricalData(
            date="2024-01-03",
            impressions=800,
            clicks=40,
            conversions=1,
            spend=80.0,
            category="MLB1051"
        )
    ]

@pytest.fixture
def sample_ab_test_variations():
    """Sample A/B test variations for testing."""
    from main import CampaignSimulationRequest
    
    variation_a = CampaignSimulationRequest(
        product_name="Product A - Original",
        category="electronics",
        budget=1000.0,
        duration_days=30,
        target_audience="professionals",
        keywords=["professional", "business", "efficient"]
    )
    
    variation_b = CampaignSimulationRequest(
        product_name="Product B - Optimized",
        category="electronics",
        budget=1000.0,
        duration_days=30,
        target_audience="professionals", 
        keywords=["enterprise", "productivity", "premium", "solution"]
    )
    
    return [variation_a, variation_b]

@pytest.fixture
def mock_random_deterministic():
    """Mock random module for deterministic testing."""
    with patch('main.random') as mock:
        mock.uniform.return_value = 0.5
        mock.randint.return_value = 123456
        mock.choice.return_value = "medium"
        mock.sin.return_value = 0.5
        yield mock

@pytest.fixture
def mock_datetime():
    """Mock datetime for predictable testing."""
    with patch('main.datetime') as mock:
        fixed_datetime = datetime(2024, 1, 15, 12, 0, 0)
        mock.now.return_value = fixed_datetime
        mock.return_value = fixed_datetime
        mock.side_effect = lambda *args, **kw: datetime(*args, **kw)
        yield mock