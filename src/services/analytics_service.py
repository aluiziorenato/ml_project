"""
Analytics service layer for ML predictions and optimizations.
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.analytics import MLPredictor, MLOptimizer, PredictionResult, OptimizationResult
from core.analytics.genetic_optimizer import GeneticOptimizer, GeneticConfig
from core.storage import DataManager, DataQuery

logger = logging.getLogger(__name__)


class AnalyticsService:
    """
    Service layer for analytics operations.
    Provides high-level interface for ML predictions and optimizations.
    """
    
    def __init__(self, data_manager: Optional[DataManager] = None):
        self.predictor = MLPredictor()
        self.optimizer = MLOptimizer()
        self.genetic_optimizer = GeneticOptimizer()
        self.data_manager = data_manager or DataManager()
        self.models = {
            "linear": MLPredictor("linear"),
            "sales_forecast": MLPredictor("sales"),
            "conversion": MLPredictor("conversion")
        }
        
    async def predict(self, features: List[float], model_type: str = "linear") -> PredictionResult:
        """
        Make a prediction using specified model.
        
        Args:
            features: Input features for prediction
            model_type: Type of model to use
            
        Returns:
            PredictionResult with prediction data
        """
        try:
            # Get or create model
            if model_type not in self.models:
                self.models[model_type] = MLPredictor(model_type)
            
            model = self.models[model_type]
            result = model.predict(features)
            
            # Store prediction result
            await self._store_prediction_result(result, model_type)
            
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise
    
    async def forecast_sales(self, 
                           historical_data: Dict[str, List[float]], 
                           forecast_days: int = 30) -> PredictionResult:
        """
        Forecast sales based on historical data.
        
        Args:
            historical_data: Historical sales and related metrics
            forecast_days: Number of days to forecast
            
        Returns:
            PredictionResult with sales forecast
        """
        try:
            model = self.models["sales_forecast"]
            result = model.predict_sales_forecast(historical_data, forecast_days)
            
            # Store forecast result
            await self._store_prediction_result(result, "sales_forecast", {
                "forecast_days": forecast_days,
                "data_points": sum(len(v) for v in historical_data.values())
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Sales forecasting failed: {str(e)}")
            raise
    
    async def predict_conversion_rate(self, campaign_data: Dict[str, Any]) -> PredictionResult:
        """
        Predict conversion rate for a marketing campaign.
        
        Args:
            campaign_data: Campaign parameters and historical performance
            
        Returns:
            PredictionResult with conversion rate prediction
        """
        try:
            model = self.models["conversion"]
            result = model.predict_conversion_rate(campaign_data)
            
            # Store prediction result
            await self._store_prediction_result(result, "conversion", {
                "campaign_budget": campaign_data.get("budget", 0),
                "campaign_type": campaign_data.get("type", "unknown")
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Conversion rate prediction failed: {str(e)}")
            raise
    
    async def optimize_budget_allocation(self, 
                                       campaigns: List[Dict[str, Any]], 
                                       total_budget: float,
                                       objective: str = "maximize_roi",
                                       optimization_method: str = "greedy") -> OptimizationResult:
        """
        Optimize budget allocation across campaigns.
        
        Args:
            campaigns: List of campaign configurations
            total_budget: Total budget to allocate
            objective: Optimization objective
            optimization_method: "greedy" or "genetic" 
            
        Returns:
            OptimizationResult with optimized allocation
        """
        try:
            if optimization_method == "genetic":
                result = self.genetic_optimizer.optimize_budget_allocation(
                    campaigns, total_budget, objective
                )
            else:
                result = self.optimizer.optimize_budget_allocation(
                    campaigns, total_budget, objective
                )
            
            # Store optimization result
            await self._store_optimization_result(result, "budget_allocation", {
                "total_budget": total_budget,
                "campaigns_count": len(campaigns),
                "objective": objective,
                "optimization_method": optimization_method
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Budget allocation optimization failed: {str(e)}")
            raise
    
    async def optimize_keyword_selection(self, 
                                       available_keywords: List[Dict[str, Any]], 
                                       max_keywords: int = 20,
                                       budget_constraint: float = 5000) -> OptimizationResult:
        """
        Optimize keyword selection for campaigns.
        
        Args:
            available_keywords: List of keywords with metrics
            max_keywords: Maximum number of keywords to select
            budget_constraint: Budget constraint for keyword costs
            
        Returns:
            OptimizationResult with optimized keyword selection
        """
        try:
            result = self.optimizer.optimize_keyword_selection(
                available_keywords, max_keywords, budget_constraint
            )
            
            # Store optimization result
            await self._store_optimization_result(result, "keyword_selection", {
                "available_keywords": len(available_keywords),
                "max_keywords": max_keywords,
                "budget_constraint": budget_constraint
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Keyword selection optimization failed: {str(e)}")
            raise
    
    async def optimize_campaign_parameters(self, 
                                         current_params: Dict[str, Any],
                                         performance_history: List[Dict[str, Any]],
                                         optimization_method: str = "greedy") -> OptimizationResult:
        """
        Optimize campaign parameters based on performance history.
        
        Args:
            current_params: Current campaign parameters
            performance_history: Historical performance data
            optimization_method: "greedy" or "genetic"
            
        Returns:
            OptimizationResult with optimized parameters
        """
        try:
            if optimization_method == "genetic":
                result = self.genetic_optimizer.optimize_campaign_parameters(
                    current_params, performance_history
                )
            else:
                result = self.optimizer.optimize_campaign_parameters(
                    current_params, performance_history
                )
            
            # Store optimization result
            await self._store_optimization_result(result, "parameter_optimization", {
                "history_data_points": len(performance_history),
                "parameters_count": len(current_params),
                "optimization_method": optimization_method
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {str(e)}")
            raise
    
    async def train_model(self, 
                         model_type: str, 
                         features: List[List[float]], 
                         targets: List[float],
                         feature_names: List[str]) -> bool:
        """
        Train a specific model with provided data.
        
        Args:
            model_type: Type of model to train
            features: Training features
            targets: Target values
            feature_names: Names of features
            
        Returns:
            True if training successful
        """
        try:
            if model_type not in self.models:
                self.models[model_type] = MLPredictor(model_type)
            
            model = self.models[model_type]
            success = model.train(features, targets, feature_names)
            
            if success:
                logger.info(f"Model {model_type} trained successfully with {len(features)} samples")
            
            return success
            
        except Exception as e:
            logger.error(f"Model training failed: {str(e)}")
            return False
    
    async def get_models_status(self) -> Dict[str, Any]:
        """
        Get status of all analytics models.
        
        Returns:
            Dictionary with model status information
        """
        try:
            status = {
                "models": {},
                "total_models": len(self.models),
                "trained_models": 0,
                "timestamp": datetime.now().isoformat()
            }
            
            for model_name, model in self.models.items():
                model_status = {
                    "name": model_name,
                    "type": model.model_type,
                    "is_trained": model.is_trained,
                    "version": model.model_version,
                    "features_count": len(model.feature_names)
                }
                
                if model.is_trained:
                    status["trained_models"] += 1
                
                status["models"][model_name] = model_status
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get models status: {str(e)}")
            raise
    
    async def get_prediction_history(self, 
                                   model_type: Optional[str] = None,
                                   limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get prediction history from storage.
        
        Args:
            model_type: Filter by model type
            limit: Maximum number of results
            
        Returns:
            List of prediction records
        """
        try:
            query = DataQuery(
                table="predictions",
                limit=limit,
                order_by="created_at",
                order_direction="DESC"
            )
            
            if model_type:
                query.filters = {"model_type": model_type}
            
            result = self.data_manager.query_data(query)
            
            if result.success:
                return result.data
            else:
                logger.error(f"Failed to query prediction history: {result.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get prediction history: {str(e)}")
            return []
    
    async def get_optimization_history(self, 
                                     optimization_type: Optional[str] = None,
                                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get optimization history from storage.
        
        Args:
            optimization_type: Filter by optimization type
            limit: Maximum number of results
            
        Returns:
            List of optimization records
        """
        try:
            query = DataQuery(
                table="optimizations",
                limit=limit,
                order_by="created_at", 
                order_direction="DESC"
            )
            
            if optimization_type:
                query.filters = {"optimization_type": optimization_type}
            
            result = self.data_manager.query_data(query)
            
            if result.success:
                return result.data
            else:
                logger.error(f"Failed to query optimization history: {result.error_message}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to get optimization history: {str(e)}")
            return []
    
    async def _store_prediction_result(self, 
                                     result: PredictionResult, 
                                     model_type: str,
                                     additional_metadata: Optional[Dict[str, Any]] = None):
        """Store prediction result in database."""
        try:
            metadata = result.metadata.copy()
            if additional_metadata:
                metadata.update(additional_metadata)
            
            data = {
                "prediction_id": f"pred_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "model_type": model_type,
                "predicted_value": result.predicted_value,
                "confidence_score": result.confidence_score,
                "feature_importance": result.feature_importance,
                "metadata": metadata
            }
            
            self.data_manager.store_data("predictions", data)
            
        except Exception as e:
            logger.error(f"Failed to store prediction result: {str(e)}")
    
    async def _store_optimization_result(self, 
                                       result: OptimizationResult, 
                                       optimization_type: str,
                                       additional_metadata: Optional[Dict[str, Any]] = None):
        """Store optimization result in database."""
        try:
            metadata = result.metadata.copy()
            if additional_metadata:
                metadata.update(additional_metadata)
            
            data = {
                "optimization_id": f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                "optimization_type": optimization_type,
                "parameters": result.optimized_parameters,
                "expected_improvement": result.expected_improvement,
                "confidence_score": result.confidence_score,
                "metadata": metadata
            }
            
            self.data_manager.store_data("optimizations", data)
            
        except Exception as e:
            logger.error(f"Failed to store optimization result: {str(e)}")
    
    async def configure_genetic_algorithm(self, config: Dict[str, Any]) -> bool:
        """
        Configure genetic algorithm parameters.
        
        Args:
            config: Configuration parameters for genetic algorithm
            
        Returns:
            True if configuration successful
        """
        try:
            genetic_config = GeneticConfig(
                population_size=config.get("population_size", 50),
                max_generations=config.get("max_generations", 100),
                crossover_rate=config.get("crossover_rate", 0.8),
                mutation_rate=config.get("mutation_rate", 0.1),
                tournament_size=config.get("tournament_size", 3),
                elitism_rate=config.get("elitism_rate", 0.1),
                convergence_threshold=config.get("convergence_threshold", 1e-6),
                max_stagnant_generations=config.get("max_stagnant_generations", 20)
            )
            
            self.genetic_optimizer = GeneticOptimizer(genetic_config)
            logger.info(f"Genetic algorithm configured with {config}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to configure genetic algorithm: {str(e)}")
            return False
    
    async def set_optimization_constraints(self, constraints: Dict[str, Dict[str, float]]) -> bool:
        """
        Set optimization constraints for both optimizers.
        
        Args:
            constraints: Dict with parameter names and their min/max bounds
            
        Returns:
            True if constraints set successfully
        """
        try:
            self.optimizer.set_constraints(constraints)
            self.genetic_optimizer.set_constraints(constraints)
            logger.info(f"Optimization constraints set for {len(constraints)} parameters")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set optimization constraints: {str(e)}")
            return False
    
    async def get_genetic_algorithm_status(self) -> Dict[str, Any]:
        """
        Get status and performance metrics of the genetic algorithm.
        
        Returns:
            Dictionary with genetic algorithm status
        """
        try:
            status = {
                "configured": self.genetic_optimizer is not None,
                "config": {
                    "population_size": self.genetic_optimizer.config.population_size,
                    "max_generations": self.genetic_optimizer.config.max_generations,
                    "crossover_rate": self.genetic_optimizer.config.crossover_rate,
                    "mutation_rate": self.genetic_optimizer.config.mutation_rate,
                    "tournament_size": self.genetic_optimizer.config.tournament_size,
                    "elitism_rate": self.genetic_optimizer.config.elitism_rate
                },
                "current_generation": self.genetic_optimizer.generation,
                "population_size": len(self.genetic_optimizer.population),
                "best_fitness": self.genetic_optimizer.best_chromosome.fitness if self.genetic_optimizer.best_chromosome else None,
                "fitness_history_length": len(self.genetic_optimizer.fitness_history),
                "parameter_bounds_count": len(self.genetic_optimizer.parameter_bounds),
                "constraints_count": len(self.genetic_optimizer.constraints),
                "timestamp": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get genetic algorithm status: {str(e)}")
            return {"error": str(e), "configured": False}
    
    async def get_optimization_comparison(self, 
                                        campaigns: List[Dict[str, Any]], 
                                        total_budget: float,
                                        objective: str = "maximize_roi") -> Dict[str, Any]:
        """
        Compare optimization results between greedy and genetic algorithms.
        
        Args:
            campaigns: List of campaign configurations
            total_budget: Total budget to allocate
            objective: Optimization objective
            
        Returns:
            Dictionary comparing both optimization methods
        """
        try:
            # Run both optimizations
            greedy_result = await self.optimize_budget_allocation(
                campaigns, total_budget, objective, "greedy"
            )
            
            genetic_result = await self.optimize_budget_allocation(
                campaigns, total_budget, objective, "genetic"
            )
            
            comparison = {
                "greedy": {
                    "optimized_parameters": greedy_result.optimized_parameters,
                    "expected_improvement": greedy_result.expected_improvement,
                    "confidence_score": greedy_result.confidence_score,
                    "iterations_used": greedy_result.iterations_used,
                    "metadata": greedy_result.metadata
                },
                "genetic": {
                    "optimized_parameters": genetic_result.optimized_parameters,
                    "expected_improvement": genetic_result.expected_improvement,
                    "confidence_score": genetic_result.confidence_score,
                    "iterations_used": genetic_result.iterations_used,
                    "metadata": genetic_result.metadata
                },
                "comparison": {
                    "improvement_difference": genetic_result.expected_improvement - greedy_result.expected_improvement,
                    "confidence_difference": genetic_result.confidence_score - greedy_result.confidence_score,
                    "genetic_better": genetic_result.expected_improvement > greedy_result.expected_improvement,
                    "genetic_more_confident": genetic_result.confidence_score > greedy_result.confidence_score
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare optimization methods: {str(e)}")
            raise