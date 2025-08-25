"""
Pytest configuration and fixtures for Optimizer AI tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

@pytest.fixture
def sample_copywriting_request():
    """Sample copywriting request for testing."""
    return {
        "original_text": "Produto de qualidade superior",
        "target_audience": "young_adults",
        "product_category": "electronics",
        "optimization_goal": "clicks",
        "keywords": ["smartphone", "qualidade", "premium"],
        "segment": "b2c_premium",
        "budget_range": "high",
        "priority_metrics": ["seo", "readability", "sentiment"]
    }

@pytest.fixture
def sample_compliance_text():
    """Sample text for compliance testing."""
    return "Smartphone Android com garantia do fabricante e voltagem 110/220V"

@pytest.fixture
def sample_non_compliant_text():
    """Sample non-compliant text for testing."""
    return "MELHOR DO BRASIL produto milagroso que CURA todos os problemas"

@pytest.fixture
def mock_textstat():
    """Mock textstat module for testing."""
    with patch('app.main.textstat') as mock:
        mock.flesch_reading_ease.return_value = 75.0
        yield mock

@pytest.fixture
def mock_random():
    """Mock random module for deterministic testing."""
    with patch('app.main.random') as mock:
        mock.uniform.return_value = 0.5
        mock.randint.return_value = 123456
        mock.choice.return_value = "medium"
        yield mock

@pytest.fixture
def sample_keywords_response():
    """Sample keywords response for testing."""
    return [
        {"keyword": "smartphone", "score": 0.9, "volume_estimate": 5000, "competition": "high"},
        {"keyword": "android", "score": 0.85, "volume_estimate": 3000, "competition": "medium"},
        {"keyword": "qualidade", "score": 0.8, "volume_estimate": 2000, "competition": "low"}
    ]