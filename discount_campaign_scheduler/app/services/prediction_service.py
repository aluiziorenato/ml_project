import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
from app.models import (
    DiscountCampaign, CampaignMetric, PerformancePrediction,
    PredictionResponse
)
from app.core.config import settings

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for performance prediction based on historical data"""
    
    def __init__(self):
        self.model_version = settings.prediction_model_version
        self.confidence_threshold = settings.prediction_confidence_threshold
    
    def generate_performance_prediction(
        self, 
        session: Session, 
        campaign_id: int, 
        prediction_days: int = 30
    ) -> PredictionResponse:
        """Generate performance prediction for a campaign"""
        try:
            # Get historical data
            historical_data = self._get_historical_data(session, campaign_id)
            
            if len(historical_data) < 7:  # Need at least 7 days of data
                return self._generate_baseline_prediction(campaign_id, prediction_days)
            
            # Train prediction model
            predictions, confidence = self._train_and_predict(
                historical_data, prediction_days
            )
            
            # Store prediction in database
            prediction_record = self._store_prediction(
                session, campaign_id, predictions, confidence, prediction_days
            )
            
            return PredictionResponse(
                campaign_id=campaign_id,
                predicted_clicks=predictions["clicks"],
                predicted_impressions=predictions["impressions"],
                predicted_conversions=predictions["conversions"],
                predicted_sales=predictions["sales"],
                confidence_score=confidence,
                prediction_period_days=prediction_days
            )
            
        except Exception as e:
            logger.error(f"Error generating prediction for campaign {campaign_id}: {e}")
            return self._generate_baseline_prediction(campaign_id, prediction_days)
    
    def _get_historical_data(self, session: Session, campaign_id: int) -> List[Dict]:
        """Get historical metrics data for a campaign"""
        # Get metrics from last 90 days
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        
        statement = select(CampaignMetric).where(
            CampaignMetric.campaign_id == campaign_id,
            CampaignMetric.period_start >= cutoff_date
        ).order_by(CampaignMetric.period_start)
        
        metrics = session.exec(statement).all()
        
        return [
            {
                "date": metric.period_start,
                "clicks": metric.clicks,
                "impressions": metric.impressions,
                "conversions": metric.conversions,
                "sales": metric.sales_amount,
                "conversion_rate": metric.conversion_rate,
                "engagement_score": metric.engagement_score or 0,
                "performance_index": metric.performance_index or 0
            }
            for metric in metrics
        ]
    
    def _train_and_predict(
        self, 
        historical_data: List[Dict], 
        prediction_days: int
    ) -> tuple[Dict, float]:
        """Train model and generate predictions"""
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        # Create features
        features = self._create_features(df)
        
        # Train models for each metric
        predictions = {}
        confidences = []
        
        for metric in ['clicks', 'impressions', 'conversions', 'sales']:
            if metric in df.columns and len(df) >= 7:
                pred_value, confidence = self._train_metric_model(
                    features, df[metric].values, prediction_days
                )
                predictions[metric] = max(0, int(pred_value)) if metric != 'sales' else max(0, pred_value)
                confidences.append(confidence)
            else:
                predictions[metric] = 0
                confidences.append(0.5)
        
        # Average confidence across all metrics
        avg_confidence = np.mean(confidences) if confidences else 0.5
        
        return predictions, min(1.0, max(0.0, avg_confidence))
    
    def _create_features(self, df: pd.DataFrame) -> np.ndarray:
        """Create feature matrix for training"""
        features = []
        
        for i in range(len(df)):
            feature_row = [
                i,  # Time index
                df.iloc[i]['engagement_score'],
                df.iloc[i]['performance_index'],
                df.iloc[i]['conversion_rate']
            ]
            
            # Add moving averages if enough data
            if i >= 3:
                feature_row.extend([
                    df.iloc[max(0, i-3):i+1]['clicks'].mean(),
                    df.iloc[max(0, i-3):i+1]['impressions'].mean(),
                    df.iloc[max(0, i-3):i+1]['conversions'].mean()
                ])
            else:
                feature_row.extend([0, 0, 0])
            
            # Add trend indicators
            if i >= 7:
                recent_avg = df.iloc[max(0, i-3):i+1]['clicks'].mean()
                older_avg = df.iloc[max(0, i-7):max(1, i-3)]['clicks'].mean()
                trend = (recent_avg - older_avg) / older_avg if older_avg > 0 else 0
                feature_row.append(trend)
            else:
                feature_row.append(0)
            
            features.append(feature_row)
        
        return np.array(features)
    
    def _train_metric_model(
        self, 
        features: np.ndarray, 
        target: np.ndarray, 
        prediction_days: int
    ) -> tuple[float, float]:
        """Train model for a specific metric"""
        try:
            # Prepare training data
            X = features[:-1] if len(features) > 1 else features
            y = target[1:] if len(target) > 1 else target
            
            if len(X) < 3:
                # Not enough data for training
                return float(np.mean(target)), 0.5
            
            # Scale features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Train linear regression model
            model = LinearRegression()
            model.fit(X_scaled, y)
            
            # Calculate confidence based on R² score
            confidence = max(0.3, min(1.0, model.score(X_scaled, y)))
            
            # Generate prediction
            # Use last known values to predict next period
            last_features = features[-1:].copy()
            last_features_scaled = scaler.transform(last_features)
            
            prediction = model.predict(last_features_scaled)[0]
            
            # Apply growth factor for multi-day predictions
            if prediction_days > 1:
                # Calculate average daily growth rate
                daily_growth = self._calculate_daily_growth(target)
                prediction *= (1 + daily_growth) ** prediction_days
            
            return float(prediction), confidence
            
        except Exception as e:
            logger.warning(f"Error training model: {e}")
            # Fallback to simple average
            return float(np.mean(target)), 0.5
    
    def _calculate_daily_growth(self, values: np.ndarray) -> float:
        """Calculate average daily growth rate"""
        if len(values) < 2:
            return 0.0
        
        growth_rates = []
        for i in range(1, len(values)):
            if values[i-1] > 0:
                growth_rate = (values[i] - values[i-1]) / values[i-1]
                growth_rates.append(growth_rate)
        
        return np.mean(growth_rates) if growth_rates else 0.0
    
    def _generate_baseline_prediction(
        self, 
        campaign_id: int, 
        prediction_days: int
    ) -> PredictionResponse:
        """Generate baseline prediction when insufficient data"""
        # Use industry averages as baseline
        baseline_daily_clicks = 50
        baseline_daily_impressions = 200
        baseline_conversion_rate = 0.02
        baseline_avg_sale = 45.0
        
        predicted_clicks = baseline_daily_clicks * prediction_days
        predicted_impressions = baseline_daily_impressions * prediction_days
        predicted_conversions = int(predicted_clicks * baseline_conversion_rate)
        predicted_sales = predicted_conversions * baseline_avg_sale
        
        return PredictionResponse(
            campaign_id=campaign_id,
            predicted_clicks=predicted_clicks,
            predicted_impressions=predicted_impressions,
            predicted_conversions=predicted_conversions,
            predicted_sales=predicted_sales,
            confidence_score=0.5,  # Medium confidence for baseline
            prediction_period_days=prediction_days
        )
    
    def _store_prediction(
        self,
        session: Session,
        campaign_id: int,
        predictions: Dict,
        confidence: float,
        prediction_days: int
    ) -> PerformancePrediction:
        """Store prediction in database"""
        prediction_record = PerformancePrediction(
            campaign_id=campaign_id,
            predicted_clicks=predictions["clicks"],
            predicted_impressions=predictions["impressions"],
            predicted_conversions=predictions["conversions"],
            predicted_sales=predictions["sales"],
            confidence_score=confidence,
            prediction_period_days=prediction_days,
            model_version=self.model_version,
            features_used={
                "historical_days": 90,
                "features": ["time_index", "engagement_score", "performance_index", 
                           "conversion_rate", "moving_averages", "trends"],
                "model_type": "linear_regression"
            }
        )
        
        session.add(prediction_record)
        session.commit()
        session.refresh(prediction_record)
        
        return prediction_record
    
    def compare_prediction_vs_actual(
        self, 
        session: Session, 
        campaign_id: int, 
        days_back: int = 30
    ) -> Dict:
        """Compare predictions vs actual performance"""
        # Get predictions made in the past
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        predictions_statement = select(PerformancePrediction).where(
            PerformancePrediction.campaign_id == campaign_id,
            PerformancePrediction.prediction_date >= cutoff_date
        ).order_by(PerformancePrediction.prediction_date)
        
        predictions = session.exec(predictions_statement).all()
        
        if not predictions:
            return {"status": "no_predictions", "comparisons": []}
        
        comparisons = []
        
        for prediction in predictions:
            # Get actual metrics for the predicted period
            actual_start = prediction.prediction_date
            actual_end = actual_start + timedelta(days=prediction.prediction_period_days)
            
            actual_metrics = self._get_actual_metrics_for_period(
                session, campaign_id, actual_start, actual_end
            )
            
            if actual_metrics:
                comparison = {
                    "prediction_date": prediction.prediction_date,
                    "period_days": prediction.prediction_period_days,
                    "predicted": {
                        "clicks": prediction.predicted_clicks,
                        "impressions": prediction.predicted_impressions,
                        "conversions": prediction.predicted_conversions,
                        "sales": prediction.predicted_sales
                    },
                    "actual": actual_metrics,
                    "accuracy": self._calculate_accuracy(prediction, actual_metrics),
                    "confidence": prediction.confidence_score
                }
                comparisons.append(comparison)
        
        return {
            "status": "success",
            "total_predictions": len(predictions),
            "comparisons": comparisons,
            "average_accuracy": np.mean([c["accuracy"] for c in comparisons]) if comparisons else 0
        }
    
    def _get_actual_metrics_for_period(
        self, 
        session: Session, 
        campaign_id: int, 
        start_date: datetime, 
        end_date: datetime
    ) -> Optional[Dict]:
        """Get actual metrics for a specific period"""
        statement = select(CampaignMetric).where(
            CampaignMetric.campaign_id == campaign_id,
            CampaignMetric.period_start >= start_date,
            CampaignMetric.period_end <= end_date
        )
        
        metrics = session.exec(statement).all()
        
        if not metrics:
            return None
        
        return {
            "clicks": sum(m.clicks for m in metrics),
            "impressions": sum(m.impressions for m in metrics),
            "conversions": sum(m.conversions for m in metrics),
            "sales": sum(m.sales_amount for m in metrics)
        }
    
    def _calculate_accuracy(self, prediction: PerformancePrediction, actual: Dict) -> float:
        """Calculate prediction accuracy"""
        accuracies = []
        
        # Calculate accuracy for each metric
        metrics = ["clicks", "impressions", "conversions", "sales"]
        pred_values = [
            prediction.predicted_clicks,
            prediction.predicted_impressions,
            prediction.predicted_conversions,
            prediction.predicted_sales
        ]
        
        for i, metric in enumerate(metrics):
            pred_val = pred_values[i]
            actual_val = actual.get(metric, 0)
            
            if actual_val > 0:
                # Calculate percentage error
                error = abs(pred_val - actual_val) / actual_val
                accuracy = max(0, 1 - error)  # Convert error to accuracy
                accuracies.append(accuracy)
        
        return np.mean(accuracies) if accuracies else 0.0


# Global instance
prediction_service = PredictionService()