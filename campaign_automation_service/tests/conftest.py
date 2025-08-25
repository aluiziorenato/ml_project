"""
Pytest configuration and fixtures for Campaign Automation Service tests.
"""
import pytest
import sys
import os

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_campaign_data():
    """Sample campaign data for testing."""
    return {
        "name": "Test Campaign",
        "description": "A test campaign for unit testing",
        "status": "draft",
        "campaign_type": "sponsored_ads",
        "optimization_goal": "conversions"
    }