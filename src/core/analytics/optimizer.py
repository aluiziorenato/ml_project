"""
ML Optimizer module for campaign and performance optimization.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    """Result of an optimization operation."""
    optimized_parameters: Dict[str, Any]
    expected_improvement: float
    confidence_score: float
    optimization_method: str
    iterations_used: int
    timestamp: datetime
    metadata: Dict[str, Any]


class MLOptimizer:
    """
    Machine Learning optimizer for campaign parameters and performance.
    Provides optimization for budget allocation, keyword selection, and targeting.
    """
    
    def __init__(self, optimization_method: str = "greedy"):
        self.optimization_method = optimization_method
        self.optimization_history = []
        self.constraints = {}
        
    def set_constraints(self, constraints: Dict[str, Dict[str, float]]):
        """
        Set optimization constraints for parameters.
        
        Args:
            constraints: Dict with parameter names and their min/max bounds
        """
        self.constraints = constraints
        logger.info(f"Set constraints for {len(constraints)} parameters")
    
    def optimize_budget_allocation(self, 
                                 campaigns: List[Dict[str, Any]], 
                                 total_budget: float,
                                 objective: str = "maximize_roi") -> OptimizationResult:
        """
        Optimize budget allocation across multiple campaigns.
        
        Args:
            campaigns: List of campaign configurations
            total_budget: Total budget to allocate
            objective: Optimization objective ('maximize_roi', 'maximize_conversions')
            
        Returns:
            OptimizationResult with optimized budget allocation
        """
        try:
            if not campaigns:
                raise ValueError("Campaigns list cannot be empty")
                
            n_campaigns = len(campaigns)
            
            # Simple optimization: allocate based on historical performance
            performance_scores = []
            for campaign in campaigns:
                roi = campaign.get("historical_roi", 2.0)
                conversion_rate = campaign.get("historical_conversion_rate", 0.02)
                
                if objective == "maximize_roi":
                    score = roi
                elif objective == "maximize_conversions":
                    score = conversion_rate * 100
                else:
                    score = roi * conversion_rate * 50  # Combined score
                    
                performance_scores.append(score)
            
            # Normalize scores and allocate budget proportionally
            total_score = sum(performance_scores)
            if total_score == 0:
                # Equal allocation if no historical data
                allocation = [total_budget / n_campaigns] * n_campaigns
            else:
                allocation = [
                    (score / total_score) * total_budget 
                    for score in performance_scores
                ]
            
            optimized_parameters = {
                f"campaign_{i}_budget": round(allocation[i], 2)
                for i in range(n_campaigns)
            }
            
            # Calculate expected improvement (simplified)
            current_performance = sum(c.get("current_performance", 1000) for c in campaigns)
            expected_improvement = current_performance * 0.15  # Assume 15% improvement
            
            return OptimizationResult(
                optimized_parameters=optimized_parameters,
                expected_improvement=expected_improvement,
                confidence_score=0.85,
                optimization_method=self.optimization_method,
                iterations_used=1,
                timestamp=datetime.now(),
                metadata={
                    "total_budget": total_budget,
                    "objective": objective,
                    "campaigns_count": n_campaigns
                }
            )
                
        except Exception as e:
            logger.error(f"Budget optimization failed: {str(e)}")
            raise
    
    def optimize_keyword_selection(self, 
                                 available_keywords: List[Dict[str, Any]], 
                                 max_keywords: int = 20,
                                 budget_constraint: float = 5000) -> OptimizationResult:
        """
        Optimize keyword selection for a campaign.
        
        Args:
            available_keywords: List of keywords with metrics
            max_keywords: Maximum number of keywords to select
            budget_constraint: Budget constraint for keyword costs
            
        Returns:
            OptimizationResult with optimized keyword selection
        """
        try:
            if not available_keywords:
                raise ValueError("Keywords list cannot be empty")
            
            # Score keywords based on performance metrics
            def keyword_score(kw):
                cpc = kw.get("cpc", 1.0)
                volume = kw.get("search_volume", 1000)
                competition = kw.get("competition_score", 5)  # 1-10 scale
                relevance = kw.get("relevance_score", 7)  # 1-10 scale
                
                # Higher volume and relevance is better, lower CPC and competition is better
                score = (volume * relevance) / max(1, cpc * competition)
                return score
            
            # Calculate scores and sort
            keyword_scores = [(i, keyword_score(kw)) for i, kw in enumerate(available_keywords)]
            keyword_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Select top keywords within budget
            selected_keywords = []
            total_cost = 0
            
            for idx, score in keyword_scores:
                if len(selected_keywords) >= max_keywords:
                    break
                    
                keyword = available_keywords[idx]
                daily_cost = keyword.get("cpc", 1.0) * keyword.get("estimated_daily_clicks", 10)
                
                if total_cost + daily_cost <= budget_constraint:
                    selected_keywords.append(idx)
                    total_cost += daily_cost
            
            optimized_parameters = {
                "selected_keyword_indices": selected_keywords,
                "selected_keywords": [available_keywords[idx]["keyword"] 
                                    for idx in selected_keywords if "keyword" in available_keywords[idx]],
                "total_estimated_cost": round(total_cost, 2),
                "keywords_count": len(selected_keywords)
            }
            
            # Calculate expected improvement
            expected_improvement = len(selected_keywords) * 50  # Simplified improvement metric
            
            return OptimizationResult(
                optimized_parameters=optimized_parameters,
                expected_improvement=expected_improvement,
                confidence_score=0.8,
                optimization_method="greedy_selection",
                iterations_used=1,
                timestamp=datetime.now(),
                metadata={
                    "total_keywords_available": len(available_keywords),
                    "budget_constraint": budget_constraint,
                    "max_keywords": max_keywords
                }
            )
            
        except Exception as e:
            logger.error(f"Keyword optimization failed: {str(e)}")
            raise
    
    def optimize_campaign_parameters(self, 
                                   current_params: Dict[str, Any],
                                   performance_history: List[Dict[str, Any]]) -> OptimizationResult:
        """
        Optimize general campaign parameters based on historical performance.
        
        Args:
            current_params: Current campaign parameters
            performance_history: Historical performance data
            
        Returns:
            OptimizationResult with optimized parameters
        """
        try:
            if not performance_history:
                logger.warning("No performance history provided, using defaults")
                performance_history = [{"roi": 2.0, "conversion_rate": 0.02}]
            
            # Analyze performance trends
            recent_performance = performance_history[-5:] if len(performance_history) >= 5 else performance_history
            avg_roi = sum(p.get("roi", 2.0) for p in recent_performance) / len(recent_performance)
            avg_conversion_rate = sum(p.get("conversion_rate", 0.02) for p in recent_performance) / len(recent_performance)
            
            optimized_params = current_params.copy()
            
            # Optimize bid strategy
            current_bid = current_params.get("max_cpc", 1.0)
            if avg_roi > 3.0:
                # Good ROI, can increase bid
                optimized_params["max_cpc"] = min(current_bid * 1.2, 5.0)
            elif avg_roi < 1.5:
                # Poor ROI, decrease bid
                optimized_params["max_cpc"] = max(current_bid * 0.8, 0.1)
                
            # Optimize targeting
            if avg_conversion_rate > 0.05:
                # High conversion rate, can expand targeting
                optimized_params["audience_expansion"] = True
                optimized_params["location_radius"] = min(
                    current_params.get("location_radius", 25) * 1.3, 100
                )
            elif avg_conversion_rate < 0.01:
                # Low conversion rate, narrow targeting
                optimized_params["audience_expansion"] = False
                optimized_params["location_radius"] = max(
                    current_params.get("location_radius", 25) * 0.7, 5
                )
            
            # Calculate expected improvement
            current_performance = avg_roi * 1000  # Simplified metric
            improvement_factor = 1.15 if avg_roi < 2.5 else 1.05
            expected_improvement = current_performance * (improvement_factor - 1)
            
            return OptimizationResult(
                optimized_parameters=optimized_params,
                expected_improvement=expected_improvement,
                confidence_score=0.75,
                optimization_method="rule_based",
                iterations_used=1,
                timestamp=datetime.now(),
                metadata={
                    "avg_roi": avg_roi,
                    "avg_conversion_rate": avg_conversion_rate,
                    "performance_data_points": len(performance_history)
                }
            )
            
        except Exception as e:
            logger.error(f"Parameter optimization failed: {str(e)}")
            raise