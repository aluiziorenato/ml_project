import httpx
import asyncio
from typing import Dict, Optional, List, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class MicroserviceIntegrationService:
    """Service for orchestrating HTTP calls to other microservices"""
    
    def __init__(self):
        self.simulator_url = getattr(settings, 'SIMULATOR_SERVICE_URL', 'http://simulator_service:8001')
        self.optimizer_url = getattr(settings, 'OPTIMIZER_AI_URL', 'http://optimizer_ai:8003')
        self.learning_url = getattr(settings, 'LEARNING_SERVICE_URL', 'http://learning_service:8002')
        self.performance_detector_url = getattr(settings, 'PERFORMANCE_DETECTOR_URL', 'http://backend:8000')
        
        self.timeout = 30.0
        self.max_retries = 3

    async def simulate_campaign_performance(self, campaign_data: Dict) -> Optional[Dict]:
        """Call simulator service to predict campaign performance"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.simulator_url}/api/simulate/campaign-performance",
                    json=campaign_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to simulate campaign performance: {e}")
            return None

    async def optimize_copy_with_keywords(
        self, 
        product_data: Dict, 
        keywords: List[str], 
        target_audience: Optional[str] = None
    ) -> Optional[Dict]:
        """Call optimizer AI to enhance product copy with keywords"""
        try:
            optimization_request = {
                "product_data": product_data,
                "target_keywords": keywords,
                "target_audience": target_audience or "general",
                "optimization_type": "seo_copywriting",
                "include_keywords": True
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.optimizer_url}/api/optimize/copywriting",
                    json=optimization_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to optimize copy with keywords: {e}")
            return None

    async def detect_subperformance(self, item_ids: List[str], seller_id: str) -> Optional[Dict]:
        """Call performance detection service to identify underperforming items"""
        try:
            detection_request = {
                "seller_id": seller_id,
                "item_ids": item_ids,
                "analysis_period_days": 30,
                "metrics": ["clicks", "impressions", "conversions", "sales"]
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.performance_detector_url}/api/analytics/detect-subperformance",
                    json=detection_request
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to detect subperformance: {e}")
            return None

    async def generate_ai_suggestions(self, request_data: Dict) -> Optional[Dict]:
        """Call learning service for AI-enhanced suggestions"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.learning_url}/api/suggestions/ai-enhanced",
                    json=request_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to generate AI suggestions: {e}")
            return None

    async def schedule_campaign_activation(self, campaign_data: Dict) -> Optional[Dict]:
        """Schedule campaign activation via ML API integration"""
        try:
            # This would typically call the backend service which handles ML API integration
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.performance_detector_url}/api/campaigns/schedule-activation",
                    json=campaign_data
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to schedule campaign activation: {e}")
            return None

    async def get_keyword_insights(self, keywords: List[str]) -> Optional[Dict]:
        """Get insights about keywords from various services"""
        try:
            # Call multiple services in parallel for comprehensive keyword analysis
            tasks = []
            
            # Get SEO insights
            if hasattr(settings, 'SEO_SERVICE_URL'):
                seo_task = self._get_seo_insights(keywords)
                tasks.append(('seo', seo_task))
            
            # Get competitive analysis
            if hasattr(settings, 'COMPETITOR_SERVICE_URL'):
                comp_task = self._get_competitor_insights(keywords)
                tasks.append(('competitor', comp_task))
            
            # Execute in parallel
            results = {}
            if tasks:
                responses = await asyncio.gather(
                    *[task[1] for task in tasks],
                    return_exceptions=True
                )
                
                for i, (service_name, _) in enumerate(tasks):
                    if i < len(responses) and not isinstance(responses[i], Exception):
                        results[service_name] = responses[i]
            
            return results if results else None
            
        except Exception as e:
            logger.error(f"Failed to get keyword insights: {e}")
            return None

    async def _get_seo_insights(self, keywords: List[str]) -> Optional[Dict]:
        """Get SEO insights for keywords"""
        try:
            seo_url = getattr(settings, 'SEO_SERVICE_URL', f"{self.performance_detector_url}/api/seo")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{seo_url}/analyze-keywords",
                    json={"keywords": keywords}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"SEO insights unavailable: {e}")
            return None

    async def _get_competitor_insights(self, keywords: List[str]) -> Optional[Dict]:
        """Get competitor insights for keywords"""
        try:
            comp_url = getattr(settings, 'COMPETITOR_SERVICE_URL', f"{self.performance_detector_url}/api/competitor")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{comp_url}/analyze-keywords",
                    json={"keywords": keywords}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.warning(f"Competitor insights unavailable: {e}")
            return None

    async def orchestrate_campaign_creation(
        self, 
        campaign_base_data: Dict, 
        keywords: List[str],
        seller_id: str
    ) -> Dict:
        """Orchestrate the complete campaign creation process with multiple services"""
        
        orchestration_result = {
            "campaign_data": campaign_base_data,
            "optimization_applied": False,
            "performance_predicted": False,
            "scheduling_configured": False,
            "errors": []
        }
        
        try:
            # Step 1: Optimize copy with keywords
            logger.info("Step 1: Optimizing copy with keywords")
            product_data = {
                "item_id": campaign_base_data.get("item_id"),
                "title": campaign_base_data.get("title", ""),
                "description": campaign_base_data.get("description", ""),
                "category": campaign_base_data.get("category", "")
            }
            
            optimized_copy = await self.optimize_copy_with_keywords(
                product_data=product_data,
                keywords=keywords
            )
            
            if optimized_copy:
                orchestration_result["optimized_copy"] = optimized_copy
                orchestration_result["optimization_applied"] = True
                # Update campaign data with optimized copy
                if "optimized_title" in optimized_copy:
                    campaign_base_data["optimized_title"] = optimized_copy["optimized_title"]
                if "optimized_description" in optimized_copy:
                    campaign_base_data["optimized_description"] = optimized_copy["optimized_description"]
            
            # Step 2: Simulate performance
            logger.info("Step 2: Simulating campaign performance")
            simulation_data = {
                **campaign_base_data,
                "keywords": keywords,
                "simulation_period_days": 30
            }
            
            performance_prediction = await self.simulate_campaign_performance(simulation_data)
            if performance_prediction:
                orchestration_result["performance_prediction"] = performance_prediction
                orchestration_result["performance_predicted"] = True
            
            # Step 3: Check for subperformance indicators
            logger.info("Step 3: Checking subperformance indicators")
            subperf_analysis = await self.detect_subperformance(
                item_ids=[campaign_base_data.get("item_id")],
                seller_id=seller_id
            )
            
            if subperf_analysis:
                orchestration_result["subperformance_analysis"] = subperf_analysis
            
            # Step 4: Configure scheduling recommendations
            logger.info("Step 4: Generating scheduling recommendations")
            if performance_prediction and "optimal_timing" in performance_prediction:
                orchestration_result["scheduling_recommendations"] = performance_prediction["optimal_timing"]
                orchestration_result["scheduling_configured"] = True
            
            logger.info(f"Campaign orchestration completed for {campaign_base_data.get('item_id')}")
            
        except Exception as e:
            logger.error(f"Error in campaign orchestration: {e}")
            orchestration_result["errors"].append(str(e))
        
        return orchestration_result


# Global service instance
microservice_integration = MicroserviceIntegrationService()