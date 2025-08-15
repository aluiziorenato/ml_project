import pytest
import sys
import os

# Add the parent directory to the Python path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_model_request():
    """Sample model creation request for testing"""
    return {
        "name": "Campaign Performance Predictor",
        "description": "Predicts campaign performance based on historical data",
        "model_type": "random_forest",
        "hyperparameters": {"n_estimators": 100, "max_depth": 10},
        "features": ["budget", "duration", "keywords_count", "audience_size"]
    }

@pytest.fixture
def sample_model_update_request():
    """Sample model update request for testing"""
    return {
        "campaign_id": "CAM_12345678",
        "actual_clicks": 1500,
        "actual_conversions": 45,
        "actual_revenue": 2250.0,
        "predicted_clicks": 1400,
        "predicted_conversions": 50,
        "predicted_revenue": 2500.0,
        "notes": "Campaign performed well despite seasonal factors"
    }

@pytest.fixture
def sample_training_request():
    """Sample training job request for testing"""
    return {
        "model_id": "MDL_TEST123",
        "training_data_source": "campaign_results_2024.csv",
        "validation_split": 0.2,
        "epochs": 100,
        "batch_size": 32
    }

@pytest.fixture
def sample_prediction_request():
    """Sample prediction request for testing"""
    return {
        "model_id": "MDL_TEST123",
        "features": {
            "budget": 1000.0,
            "duration": 30,
            "keywords_count": 5,
            "audience_size": 10000
        }
    }