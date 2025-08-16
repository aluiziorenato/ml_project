"""AI integration service for campaign optimization."""

import httpx
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..utils.config import settings
from ..utils.logger import logger, log_error


class AIIntegrationService:
    """Integration with existing AI services for campaign optimization."""
    
    def __init__(self):
        self.simulator_url = settings.simulator_service_url
        self.optimizer_url = settings.optimizer_ai_url
        self.learning_url = settings.learning_service_url
        self.timeout = 30
    
    async def optimize_campaign_copy(
        self,
        campaign_id: int,
        current_copy: str,
        target_audience: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Optimize campaign copy using AI copywriting service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "text": current_copy,
                    "target_audience": target_audience.get("demographics", "general"),
                    "category": category,
                    "optimization_goal": "conversions",
                    "tone": target_audience.get("tone", "professional"),
                    "campaign_id": str(campaign_id)
                }
                
                response = await client.post(
                    f"{self.optimizer_url}/api/optimize-copy",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info(
                        "Copy optimization completed",
                        campaign_id=campaign_id,
                        improvement_score=result.get("improvement_score", 0)
                    )
                    
                    return {
                        "success": True,
                        "optimized_copy": result.get("optimized_text", current_copy),
                        "improvement_score": result.get("improvement_score", 0),
                        "seo_score": result.get("seo_score", 0),
                        "readability_score": result.get("readability_score", 0),
                        "suggestions": result.get("suggestions", []),
                        "keywords": result.get("keywords", [])
                    }
                else:
                    logger.warning(
                        "Copy optimization failed",
                        campaign_id=campaign_id,
                        status_code=response.status_code
                    )
                    return {"success": False, "error": f"Service returned {response.status_code}"}
                    
        except httpx.TimeoutException:
            log_error(Exception("Timeout"), {"service": "optimizer_ai", "campaign_id": campaign_id})
            return {"success": False, "error": "Service timeout"}
        except Exception as e:
            log_error(e, {"service": "optimizer_ai", "campaign_id": campaign_id})
            return {"success": False, "error": str(e)}
    
    async def simulate_campaign_performance(
        self,
        campaign_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Simulate campaign performance using the simulator service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Prepare simulation payload
                payload = {
                    "product_name": campaign_data.get("name", "Campaign Product"),
                    "category": campaign_data.get("category", "general"),
                    "budget": campaign_data.get("daily_budget", 100),
                    "duration_days": campaign_data.get("duration_days", 7),
                    "target_audience": campaign_data.get("target_audience", "general"),
                    "keywords": campaign_data.get("keywords", [])
                }
                
                response = await client.post(
                    f"{self.simulator_url}/api/simulate",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info(
                        "Campaign simulation completed",
                        campaign_id=campaign_data.get("id"),
                        estimated_roi=result.get("roi_percentage", 0)
                    )
                    
                    return {
                        "success": True,
                        "simulation_id": result.get("campaign_id"),
                        "estimated_impressions": result.get("estimated_reach", 0),
                        "estimated_clicks": result.get("estimated_clicks", 0),
                        "estimated_conversions": result.get("estimated_conversions", 0),
                        "estimated_cost": result.get("estimated_cost", 0),
                        "estimated_revenue": result.get("estimated_revenue", 0),
                        "roi_percentage": result.get("roi_percentage", 0),
                        "cpc": result.get("cost_per_click", 0),
                        "ctr": result.get("click_through_rate", 0),
                        "recommendations": result.get("recommendations", [])
                    }
                else:
                    logger.warning(
                        "Campaign simulation failed",
                        status_code=response.status_code
                    )
                    return {"success": False, "error": f"Service returned {response.status_code}"}
                    
        except httpx.TimeoutException:
            log_error(Exception("Timeout"), {"service": "simulator_service"})
            return {"success": False, "error": "Service timeout"}
        except Exception as e:
            log_error(e, {"service": "simulator_service"})
            return {"success": False, "error": str(e)}
    
    async def get_learning_insights(
        self,
        campaign_id: int,
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Get learning insights from the learning service."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "campaign_id": campaign_id,
                    "performance_metrics": performance_data,
                    "analysis_type": "campaign_optimization"
                }
                
                response = await client.post(
                    f"{self.learning_url}/api/analyze",
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    logger.info(
                        "Learning insights generated",
                        campaign_id=campaign_id,
                        insights_count=len(result.get("insights", []))
                    )
                    
                    return {
                        "success": True,
                        "insights": result.get("insights", []),
                        "optimization_suggestions": result.get("optimization_suggestions", []),
                        "predicted_improvements": result.get("predicted_improvements", {}),
                        "confidence_score": result.get("confidence_score", 0),
                        "model_version": result.get("model_version", "v1.0")
                    }
                else:
                    logger.warning(
                        "Learning insights failed",
                        campaign_id=campaign_id,
                        status_code=response.status_code
                    )
                    return {"success": False, "error": f"Service returned {response.status_code}"}
                    
        except httpx.TimeoutException:
            log_error(Exception("Timeout"), {"service": "learning_service", "campaign_id": campaign_id})
            return {"success": False, "error": "Service timeout"}
        except Exception as e:
            log_error(e, {"service": "learning_service", "campaign_id": campaign_id})
            return {"success": False, "error": str(e)}
    
    async def create_ab_test_variants(
        self,
        campaign_id: int,
        base_copy: str,
        target_audience: Dict[str, Any],
        variant_count: int = 3
    ) -> Dict[str, Any]:
        """Create A/B test variants using AI optimization."""
        try:
            variants = []
            
            # Generate multiple variants using the optimizer
            for i in range(variant_count):
                variant_result = await self.optimize_campaign_copy(
                    campaign_id=campaign_id,
                    current_copy=base_copy,
                    target_audience=target_audience,
                    category=target_audience.get("category", "general")
                )
                
                if variant_result["success"]:
                    variants.append({
                        "variant_id": f"variant_{i+1}",
                        "copy": variant_result["optimized_copy"],
                        "improvement_score": variant_result["improvement_score"],
                        "keywords": variant_result["keywords"]
                    })
                    
                # Add slight delay between requests
                await asyncio.sleep(0.5)
            
            if variants:
                logger.info(
                    "A/B test variants created",
                    campaign_id=campaign_id,
                    variant_count=len(variants)
                )
                
                return {
                    "success": True,
                    "variants": variants,
                    "test_setup": {
                        "traffic_split": 100 // len(variants),  # Equal split
                        "duration_days": 14,
                        "confidence_level": 95
                    }
                }
            else:
                return {"success": False, "error": "Failed to generate variants"}
                
        except Exception as e:
            log_error(e, {"action": "create_ab_test_variants", "campaign_id": campaign_id})
            return {"success": False, "error": str(e)}
    
    async def predict_campaign_performance(
        self,
        campaign_data: Dict[str, Any],
        historical_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Predict campaign performance using ML models."""
        try:
            # Combine simulation and learning service insights
            simulation_result = await self.simulate_campaign_performance(campaign_data)
            
            if not simulation_result["success"]:
                return simulation_result
            
            # If we have historical data, get additional insights
            learning_result = {"success": True, "insights": []}
            if historical_data:
                learning_result = await self.get_learning_insights(
                    campaign_data.get("id", 0),
                    historical_data
                )
            
            # Combine results
            prediction = {
                "success": True,
                "prediction_timestamp": datetime.utcnow().isoformat(),
                "estimated_performance": {
                    "impressions": simulation_result["estimated_impressions"],
                    "clicks": simulation_result["estimated_clicks"],
                    "conversions": simulation_result["estimated_conversions"],
                    "cost": simulation_result["estimated_cost"],
                    "revenue": simulation_result["estimated_revenue"],
                    "roi": simulation_result["roi_percentage"],
                    "cpc": simulation_result["cpc"],
                    "ctr": simulation_result["ctr"]
                },
                "confidence_level": "medium",  # Default confidence
                "recommendations": simulation_result.get("recommendations", []),
                "risk_factors": []
            }
            
            # Add learning insights if available
            if learning_result["success"]:
                prediction["ai_insights"] = learning_result["insights"]
                prediction["optimization_suggestions"] = learning_result.get("optimization_suggestions", [])
                prediction["confidence_level"] = self._determine_confidence_level(
                    learning_result.get("confidence_score", 0.5)
                )
            
            # Add risk assessment
            prediction["risk_factors"] = self._assess_campaign_risks(campaign_data, prediction["estimated_performance"])
            
            logger.info(
                "Campaign performance predicted",
                campaign_id=campaign_data.get("id"),
                confidence=prediction["confidence_level"]
            )
            
            return prediction
            
        except Exception as e:
            log_error(e, {"action": "predict_campaign_performance"})
            return {"success": False, "error": str(e)}
    
    async def optimize_bidding_strategy(
        self,
        campaign_id: int,
        current_performance: Dict[str, Any],
        optimization_goal: str
    ) -> Dict[str, Any]:
        """Optimize bidding strategy based on performance data."""
        try:
            # Analyze current performance
            current_cpc = current_performance.get("cpc", 0)
            current_roas = current_performance.get("roas", 0)
            current_conversions = current_performance.get("conversions", 0)
            
            recommendations = []
            adjustments = {}
            
            # CPC optimization
            if optimization_goal == "conversions" and current_roas < 2.0:
                if current_cpc > 1.5:
                    recommendations.append("Reduce max CPC to improve ROAS")
                    adjustments["max_cpc_change"] = -0.2
                else:
                    recommendations.append("Optimize for Quality Score to reduce costs")
            
            elif optimization_goal == "clicks" and current_cpc > 1.0:
                recommendations.append("Consider reducing bids to increase click volume")
                adjustments["max_cpc_change"] = -0.15
            
            elif optimization_goal == "impressions":
                recommendations.append("Increase bids to improve ad rank and impressions")
                adjustments["max_cpc_change"] = 0.1
            
            # Budget optimization
            if current_conversions > 0:
                cpa = current_performance.get("cost", 0) / current_conversions
                if cpa > 0:
                    target_cpa = cpa * 0.8  # Target 20% improvement
                    adjustments["target_cpa"] = target_cpa
                    recommendations.append(f"Set target CPA to ${target_cpa:.2f} for better efficiency")
            
            # Bidding strategy recommendations
            strategy_recommendations = []
            if optimization_goal == "conversions":
                strategy_recommendations.append("Consider using Target CPA or Maximize Conversions bidding")
            elif optimization_goal == "revenue":
                strategy_recommendations.append("Consider using Target ROAS bidding strategy")
            elif optimization_goal == "clicks":
                strategy_recommendations.append("Consider using Maximize Clicks bidding strategy")
            
            logger.info(
                "Bidding strategy optimized",
                campaign_id=campaign_id,
                optimization_goal=optimization_goal,
                recommendations_count=len(recommendations)
            )
            
            return {
                "success": True,
                "optimization_goal": optimization_goal,
                "current_performance": current_performance,
                "recommendations": recommendations,
                "suggested_adjustments": adjustments,
                "strategy_recommendations": strategy_recommendations,
                "estimated_improvement": self._estimate_bidding_improvement(adjustments),
                "optimized_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log_error(e, {"action": "optimize_bidding_strategy", "campaign_id": campaign_id})
            return {"success": False, "error": str(e)}
    
    def _determine_confidence_level(self, confidence_score: float) -> str:
        """Determine confidence level based on score."""
        if confidence_score >= 0.8:
            return "high"
        elif confidence_score >= 0.6:
            return "medium"
        else:
            return "low"
    
    def _assess_campaign_risks(
        self,
        campaign_data: Dict[str, Any],
        estimated_performance: Dict[str, Any]
    ) -> List[str]:
        """Assess potential risks for the campaign."""
        risks = []
        
        # Budget risk
        daily_budget = campaign_data.get("daily_budget", 0)
        estimated_cost = estimated_performance.get("cost", 0)
        if estimated_cost > daily_budget * 1.2:
            risks.append("Campaign may exceed daily budget")
        
        # ROI risk
        roi = estimated_performance.get("roi", 0)
        if roi < 20:
            risks.append("Low estimated ROI - review targeting and copy")
        
        # Competition risk
        keywords = campaign_data.get("keywords", [])
        if len(keywords) < 5:
            risks.append("Limited keyword targeting may reduce reach")
        
        # Audience risk
        target_audience = campaign_data.get("target_audience", {})
        if not target_audience:
            risks.append("Broad targeting may lead to low relevance")
        
        return risks
    
    def _estimate_bidding_improvement(self, adjustments: Dict[str, Any]) -> Dict[str, float]:
        """Estimate improvement from bidding adjustments."""
        improvements = {}
        
        if "max_cpc_change" in adjustments:
            cpc_change = adjustments["max_cpc_change"]
            if cpc_change < 0:  # Reducing CPC
                improvements["cost_reduction"] = abs(cpc_change) * 0.8  # 80% of CPC reduction
                improvements["roas_improvement"] = abs(cpc_change) * 0.5  # 50% ROAS improvement
            else:  # Increasing CPC
                improvements["impression_increase"] = cpc_change * 1.2  # 120% impression increase
                improvements["click_increase"] = cpc_change * 1.0  # 100% click increase
        
        if "target_cpa" in adjustments:
            improvements["conversion_efficiency"] = 0.15  # 15% efficiency improvement
        
        return improvements