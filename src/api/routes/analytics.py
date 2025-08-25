"""
Analytics API routes for ML predictions and optimizations.
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from ...core.analytics import MLPredictor, MLOptimizer, PredictionResult, OptimizationResult
from ...services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    features: List[float]
    model_type: Optional[str] = "linear"


class SalesForecastRequest(BaseModel):
    historical_data: Dict[str, List[float]]
    forecast_days: int = 30


class ConversionRateRequest(BaseModel):
    campaign_data: Dict[str, Any]


class BudgetOptimizationRequest(BaseModel):
    campaigns: List[Dict[str, Any]]
    total_budget: float
    objective: str = "maximize_roi"
    optimization_method: str = "greedy"  # "greedy" or "genetic"


class KeywordOptimizationRequest(BaseModel):
    available_keywords: List[Dict[str, Any]]
    max_keywords: int = 20
    budget_constraint: float = 5000


class ParameterOptimizationRequest(BaseModel):
    current_params: Dict[str, Any]
    performance_history: List[Dict[str, Any]]
    optimization_method: str = "greedy"  # "greedy" or "genetic"


class GeneticConfigRequest(BaseModel):
    population_size: Optional[int] = 50
    max_generations: Optional[int] = 100
    crossover_rate: Optional[float] = 0.8
    mutation_rate: Optional[float] = 0.1
    tournament_size: Optional[int] = 3
    elitism_rate: Optional[float] = 0.1
    convergence_threshold: Optional[float] = 1e-6
    max_stagnant_generations: Optional[int] = 20


class OptimizationConstraintsRequest(BaseModel):
    constraints: Dict[str, Dict[str, float]]


class OptimizationComparisonRequest(BaseModel):
    campaigns: List[Dict[str, Any]]
    total_budget: float
    objective: str = "maximize_roi"


def get_analytics_service() -> AnalyticsService:
    """Dependency to get analytics service instance."""
    return AnalyticsService()


@router.post("/predict", response_model=Dict[str, Any])
async def predict(
    request: PredictionRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Make a general prediction using ML model.
    """
    try:
        result = await service.predict(request.features, request.model_type)
        return {
            "prediction_id": f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "predicted_value": result.predicted_value,
            "confidence_score": result.confidence_score,
            "feature_importance": result.feature_importance,
            "model_version": result.model_version,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/forecast/sales", response_model=Dict[str, Any])
async def forecast_sales(
    request: SalesForecastRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Forecast sales based on historical data.
    """
    try:
        result = await service.forecast_sales(
            request.historical_data, 
            request.forecast_days
        )
        return {
            "forecast_id": f"forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "forecasted_sales": result.predicted_value,
            "confidence_score": result.confidence_score,
            "forecast_days": request.forecast_days,
            "feature_importance": result.feature_importance,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sales forecasting failed: {str(e)}")


@router.post("/predict/conversion-rate", response_model=Dict[str, Any])
async def predict_conversion_rate(
    request: ConversionRateRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Predict conversion rate for a marketing campaign.
    """
    try:
        result = await service.predict_conversion_rate(request.campaign_data)
        return {
            "prediction_id": f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "predicted_conversion_rate": result.predicted_value,
            "confidence_score": result.confidence_score,
            "feature_importance": result.feature_importance,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion rate prediction failed: {str(e)}")


@router.post("/optimize/budget", response_model=Dict[str, Any])
async def optimize_budget(
    request: BudgetOptimizationRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Optimize budget allocation across campaigns.
    """
    try:
        result = await service.optimize_budget_allocation(
            request.campaigns,
            request.total_budget,
            request.objective,
            request.optimization_method
        )
        return {
            "optimization_id": f"budget_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "optimized_allocation": result.optimized_parameters,
            "expected_improvement": result.expected_improvement,
            "confidence_score": result.confidence_score,
            "optimization_method": result.optimization_method,
            "iterations_used": result.iterations_used,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Budget optimization failed: {str(e)}")


@router.post("/optimize/keywords", response_model=Dict[str, Any])
async def optimize_keywords(
    request: KeywordOptimizationRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Optimize keyword selection for campaigns.
    """
    try:
        result = await service.optimize_keyword_selection(
            request.available_keywords,
            request.max_keywords,
            request.budget_constraint
        )
        return {
            "optimization_id": f"keywords_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "selected_keywords": result.optimized_parameters.get("selected_keywords", []),
            "selected_indices": result.optimized_parameters.get("selected_keyword_indices", []),
            "total_cost": result.optimized_parameters.get("total_estimated_cost", 0),
            "keywords_count": result.optimized_parameters.get("keywords_count", 0),
            "expected_improvement": result.expected_improvement,
            "confidence_score": result.confidence_score,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Keyword optimization failed: {str(e)}")


@router.post("/optimize/parameters", response_model=Dict[str, Any])
async def optimize_parameters(
    request: ParameterOptimizationRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Optimize campaign parameters based on performance history.
    """
    try:
        result = await service.optimize_campaign_parameters(
            request.current_params,
            request.performance_history,
            request.optimization_method
        )
        return {
            "optimization_id": f"params_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "optimized_parameters": result.optimized_parameters,
            "expected_improvement": result.expected_improvement,
            "confidence_score": result.confidence_score,
            "optimization_method": result.optimization_method,
            "timestamp": result.timestamp.isoformat(),
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parameter optimization failed: {str(e)}")


@router.get("/models/status", response_model=Dict[str, Any])
async def get_models_status(
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Get status of all analytics models.
    """
    try:
        status = await service.get_models_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models status: {str(e)}")


@router.post("/models/train", response_model=Dict[str, Any])
async def train_model(
    model_type: str,
    features: List[List[float]],
    targets: List[float],
    feature_names: List[str],
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Train a specific model with provided data.
    """
    try:
        success = await service.train_model(model_type, features, targets, feature_names)
        return {
            "model_type": model_type,
            "training_success": success,
            "samples_count": len(features),
            "features_count": len(feature_names),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model training failed: {str(e)}")


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for analytics service.
    """
    return {
        "status": "healthy",
        "service": "analytics",
        "timestamp": datetime.now().isoformat()
    }


@router.post("/genetic/configure", response_model=Dict[str, Any])
async def configure_genetic_algorithm(
    request: GeneticConfigRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Configure genetic algorithm parameters.
    """
    try:
        config = request.dict(exclude_unset=True)
        success = await service.configure_genetic_algorithm(config)
        
        return {
            "success": success,
            "message": "Genetic algorithm configured successfully" if success else "Configuration failed",
            "config": config,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Genetic algorithm configuration failed: {str(e)}")


@router.post("/constraints/set", response_model=Dict[str, Any])
async def set_optimization_constraints(
    request: OptimizationConstraintsRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Set optimization constraints for parameters.
    """
    try:
        success = await service.set_optimization_constraints(request.constraints)
        
        return {
            "success": success,
            "message": "Constraints set successfully" if success else "Failed to set constraints",
            "constraints_count": len(request.constraints),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set constraints: {str(e)}")


@router.get("/genetic/status", response_model=Dict[str, Any])
async def get_genetic_algorithm_status(
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Get status and configuration of the genetic algorithm.
    """
    try:
        status = await service.get_genetic_algorithm_status()
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get genetic algorithm status: {str(e)}")


@router.post("/optimize/compare", response_model=Dict[str, Any])
async def compare_optimization_methods(
    request: OptimizationComparisonRequest,
    service: AnalyticsService = Depends(get_analytics_service)
) -> Dict[str, Any]:
    """
    Compare optimization results between greedy and genetic algorithms.
    """
    try:
        comparison = await service.get_optimization_comparison(
            request.campaigns,
            request.total_budget,
            request.objective
        )
        
        return {
            "comparison_id": f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            **comparison
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization comparison failed: {str(e)}")