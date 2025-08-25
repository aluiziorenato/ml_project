"""
Unit tests for core analytics modules.
"""

import pytest
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from core.analytics.predictor import MLPredictor, PredictionResult
from core.analytics.optimizer import MLOptimizer, OptimizationResult


class TestMLPredictor:
    """Test cases for MLPredictor class."""
    
    def test_init(self):
        """Test predictor initialization."""
        predictor = MLPredictor()
        assert predictor.model_type == "linear"
        assert not predictor.is_trained
        assert predictor.feature_names == []
        assert predictor.model_version == "1.0.0"
        
        # Test with custom model type
        predictor = MLPredictor("custom")
        assert predictor.model_type == "custom"
    
    def test_train_success(self):
        """Test successful model training."""
        predictor = MLPredictor()
        features = [[1, 2, 3], [4, 5, 6]]
        targets = [10, 20]
        feature_names = ["feat1", "feat2", "feat3"]
        
        result = predictor.train(features, targets, feature_names)
        
        assert result is True
        assert predictor.is_trained is True
        assert predictor.feature_names == feature_names
    
    def test_predict_untrained_model(self):
        """Test prediction with untrained model."""
        predictor = MLPredictor()
        features = [1, 2, 3]
        
        result = predictor.predict(features)
        
        assert isinstance(result, PredictionResult)
        assert result.predicted_value == 2.0  # Average of features
        assert 0.1 <= result.confidence_score <= 0.95
        assert result.model_version == "1.0.0"
    
    def test_predict_sales_forecast(self):
        """Test sales forecasting."""
        predictor = MLPredictor()
        historical_data = {
            "sales": [100, 120, 110, 130, 140],
            "marketing_spend": [50, 60, 55, 65, 70]
        }
        
        result = predictor.predict_sales_forecast(historical_data, 7)
        
        assert isinstance(result, PredictionResult)
        assert result.predicted_value >= 0  # Can be 0 for heuristic method
        assert result.metadata["forecast_days"] == 7
    
    def test_predict_conversion_rate(self):
        """Test conversion rate prediction."""
        predictor = MLPredictor()
        campaign_data = {
            "budget": 1000,
            "duration_days": 14,
            "keywords": ["keyword1", "keyword2"],
            "historical_ctr": 0.03,
            "audience_size": 50000
        }
        
        result = predictor.predict_conversion_rate(campaign_data)
        
        assert isinstance(result, PredictionResult)
        assert result.predicted_value > 0
        assert result.metadata["method"] == "heuristic"


class TestMLOptimizer:
    """Test cases for MLOptimizer class."""
    
    def test_init(self):
        """Test optimizer initialization."""
        optimizer = MLOptimizer()
        assert optimizer.optimization_method == "greedy"
        assert optimizer.optimization_history == []
        assert optimizer.constraints == {}
    
    def test_optimize_budget_allocation(self):
        """Test budget optimization."""
        optimizer = MLOptimizer()
        campaigns = [
            {"historical_roi": 2.5, "historical_conversion_rate": 0.03},
            {"historical_roi": 1.8, "historical_conversion_rate": 0.02}
        ]
        
        result = optimizer.optimize_budget_allocation(campaigns, 10000, "maximize_roi")
        
        assert isinstance(result, OptimizationResult)
        assert result.expected_improvement >= 0
        assert "campaign_0_budget" in result.optimized_parameters
        assert "campaign_1_budget" in result.optimized_parameters
    
    def test_optimize_keyword_selection(self):
        """Test keyword optimization."""
        optimizer = MLOptimizer()
        keywords = [
            {"keyword": "test1", "cpc": 1.0, "search_volume": 1000, "competition_score": 5, "relevance_score": 8},
            {"keyword": "test2", "cpc": 1.5, "search_volume": 800, "competition_score": 3, "relevance_score": 9}
        ]
        
        result = optimizer.optimize_keyword_selection(keywords, 5, 1000)
        
        assert isinstance(result, OptimizationResult)
        assert result.expected_improvement >= 0
        assert "selected_keywords" in result.optimized_parameters
    
    def test_optimize_campaign_parameters(self):
        """Test campaign parameter optimization."""
        optimizer = MLOptimizer()
        current_params = {"max_cpc": 1.0, "location_radius": 25}
        performance_history = [
            {"roi": 2.5, "conversion_rate": 0.03},
            {"roi": 2.2, "conversion_rate": 0.025}
        ]
        
        result = optimizer.optimize_campaign_parameters(current_params, performance_history)
        
        assert isinstance(result, OptimizationResult)
        assert result.expected_improvement >= 0
        assert "max_cpc" in result.optimized_parameters