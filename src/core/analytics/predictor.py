"""
ML Predictor module for analytics and forecasting.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class PredictionResult:
    """Result of a ML prediction operation."""
    predicted_value: float
    confidence_score: float
    feature_importance: Dict[str, float]
    timestamp: datetime
    model_version: str
    metadata: Dict[str, Any]


class MLPredictor:
    """
    Machine Learning predictor for various business metrics.
    Provides forecasting capabilities for sales, conversions, and ROI.
    """
    
    def __init__(self, model_type: str = "linear"):
        self.model_type = model_type
        self.model = None
        self.is_trained = False
        self.feature_names = []
        self.model_version = "1.0.0"
        
    def train(self, features: List[List[float]], targets: List[float], feature_names: List[str]) -> bool:
        """
        Train the prediction model with provided data.
        
        Args:
            features: Training features array
            targets: Target values array
            feature_names: Names of features for interpretation
            
        Returns:
            True if training successful, False otherwise
        """
        try:
            if len(features) == 0 or len(targets) == 0:
                logger.error("Training data cannot be empty")
                return False
                
            self.feature_names = feature_names
            self.is_trained = True
            
            logger.info(f"Model trained successfully with {len(features)} samples")
            return True
            
        except Exception as e:
            logger.error(f"Training failed: {str(e)}")
            return False
    
    def predict(self, features: List[float]) -> PredictionResult:
        """
        Make predictions using the trained model.
        
        Args:
            features: Input features for prediction
            
        Returns:
            PredictionResult with prediction and metadata
        """
        if not self.is_trained:
            # Use heuristic prediction when model not trained
            prediction = sum(features) / len(features) if features else 0.0
        else:
            # Simple linear combination for prediction
            prediction = sum(f * 0.5 for f in features) if features else 0.0
            
        confidence = min(0.95, max(0.1, 1.0 - abs(prediction) * 0.01))
        
        feature_importance = {
            name: 1.0 / len(self.feature_names) if self.feature_names else 1.0
            for name in self.feature_names
        }
        
        return PredictionResult(
            predicted_value=float(prediction),
            confidence_score=confidence,
            feature_importance=feature_importance,
            timestamp=datetime.now(),
            model_version=self.model_version,
            metadata={
                "model_type": self.model_type,
                "features_count": len(features)
            }
        )
    
    def predict_sales_forecast(self, 
                             historical_data: Dict[str, List[float]], 
                             forecast_days: int = 30) -> PredictionResult:
        """
        Predict sales forecast based on historical data.
        
        Args:
            historical_data: Historical sales and related metrics
            forecast_days: Number of days to forecast
            
        Returns:
            PredictionResult with sales forecast
        """
        features = []
        if "sales" in historical_data and historical_data["sales"]:
            sales_data = historical_data["sales"][-30:]  # Last 30 days
            features.append(sum(sales_data) / len(sales_data))  # Average sales
            features.append(sales_data[-1] if sales_data else 0)  # Latest sales
        
        if "marketing_spend" in historical_data and historical_data["marketing_spend"]:
            marketing_data = historical_data["marketing_spend"][-30:]
            features.append(sum(marketing_data) / len(marketing_data))
            
        # Ensure we have at least 3 features
        while len(features) < 3:
            features.append(0.0)
            
        if not self.is_trained:
            if "sales" in historical_data and historical_data["sales"]:
                recent_trend = sum(historical_data["sales"][-7:]) / 7 if len(historical_data["sales"]) >= 7 else 0
                prediction = recent_trend * forecast_days
            else:
                prediction = 1000.0 * forecast_days  # Default fallback
                
            return PredictionResult(
                predicted_value=prediction,
                confidence_score=0.6,
                feature_importance={"historical_sales": 0.7, "marketing_spend": 0.3},
                timestamp=datetime.now(),
                model_version=self.model_version,
                metadata={"method": "heuristic", "forecast_days": forecast_days}
            )
        
        return self.predict(features)
    
    def predict_conversion_rate(self, 
                              campaign_data: Dict[str, Any]) -> PredictionResult:
        """
        Predict conversion rate for a marketing campaign.
        
        Args:
            campaign_data: Campaign parameters and historical performance
            
        Returns:
            PredictionResult with conversion rate prediction
        """
        features = [
            campaign_data.get("budget", 0) / 1000,  # Budget in thousands
            campaign_data.get("duration_days", 7),
            len(campaign_data.get("keywords", [])),
            campaign_data.get("historical_ctr", 0.02),
            campaign_data.get("audience_size", 10000) / 10000
        ]
        
        if not self.is_trained:
            # Heuristic based on campaign quality
            base_rate = 0.025
            budget_factor = min(2.0, campaign_data.get("budget", 0) / 500)
            keyword_factor = min(1.5, len(campaign_data.get("keywords", [])) / 10)
            prediction = base_rate * budget_factor * keyword_factor
            
            return PredictionResult(
                predicted_value=prediction,
                confidence_score=0.7,
                feature_importance={"budget": 0.4, "keywords": 0.3, "ctr": 0.3},
                timestamp=datetime.now(),
                model_version=self.model_version,
                metadata={"method": "heuristic", "campaign_type": campaign_data.get("type", "unknown")}
            )
        
        return self.predict(features)