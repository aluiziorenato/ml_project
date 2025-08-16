import httpx
import asyncio
from typing import Dict, Any, List
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

class IntegrationService:
    """Service for integrating with external services"""
    
    def __init__(self):
        self.acos_service_url = settings.ACOS_SERVICE_URL
        self.campaign_service_url = settings.CAMPAIGN_SERVICE_URL
        self.discount_service_url = settings.DISCOUNT_SERVICE_URL
        self.timeout = 30
    
    async def check_service_status(self, service_url: str, service_name: str) -> Dict[str, Any]:
        """Check status of a specific service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{service_url}/health")
                if response.status_code == 200:
                    return {
                        "service": service_name,
                        "status": "healthy",
                        "url": service_url,
                        "response_time": response.elapsed.total_seconds()
                    }
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "url": service_url,
                        "error": f"HTTP {response.status_code}"
                    }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "url": service_url,
                "error": str(e)
            }
    
    async def check_acos_service(self) -> Dict[str, Any]:
        """Check ACOS service status"""
        return await self.check_service_status(self.acos_service_url, "acos")
    
    async def check_campaign_service(self) -> Dict[str, Any]:
        """Check Campaign Automation service status"""
        return await self.check_service_status(self.campaign_service_url, "campaign_automation")
    
    async def check_discount_service(self) -> Dict[str, Any]:
        """Check Discount Campaign Scheduler service status"""
        return await self.check_service_status(self.discount_service_url, "discount_scheduler")
    
    async def check_all_services_status(self) -> Dict[str, Any]:
        """Check status of all integrated services"""
        tasks = [
            self.check_acos_service(),
            self.check_campaign_service(),
            self.check_discount_service()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        services_status = []
        healthy_count = 0
        
        for result in results:
            if isinstance(result, Exception):
                services_status.append({
                    "service": "unknown",
                    "status": "error",
                    "error": str(result)
                })
            else:
                services_status.append(result)
                if result.get("status") == "healthy":
                    healthy_count += 1
        
        return {
            "overall_status": "healthy" if healthy_count == len(tasks) else "degraded",
            "healthy_services": healthy_count,
            "total_services": len(tasks),
            "services": services_status
        }
    
    async def apply_strategy_to_acos(self, strategy_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Apply strategy configuration to ACOS service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "user_id": user_id,
                    "strategy": strategy_data,
                    "acos_thresholds": {
                        "min": strategy_data.get("acos_min", 10),
                        "max": strategy_data.get("acos_max", 25)
                    },
                    "automation_rules": strategy_data.get("automation_rules", {}),
                    "alert_thresholds": strategy_data.get("alert_thresholds", {})
                }
                
                response = await client.post(
                    f"{self.acos_service_url}/api/strategy/apply",
                    json=payload
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            logger.error(f"Failed to apply strategy to ACOS service: {e}")
            return {"success": False, "error": str(e)}
    
    async def apply_strategy_to_campaign(self, strategy_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Apply strategy configuration to Campaign Automation service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "user_id": user_id,
                    "strategy": strategy_data,
                    "budget_multiplier": strategy_data.get("budget_multiplier", 1.0),
                    "bid_adjustment": strategy_data.get("bid_adjustment", 0),
                    "automation_rules": strategy_data.get("automation_rules", {})
                }
                
                response = await client.post(
                    f"{self.campaign_service_url}/api/strategy/configure",
                    json=payload
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            logger.error(f"Failed to apply strategy to Campaign service: {e}")
            return {"success": False, "error": str(e)}
    
    async def apply_strategy_to_discount(self, strategy_data: Dict[str, Any], user_id: int) -> Dict[str, Any]:
        """Apply strategy configuration to Discount Campaign Scheduler"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "user_id": user_id,
                    "strategy": strategy_data,
                    "margin_threshold": strategy_data.get("margin_threshold", 25),
                    "automation_rules": strategy_data.get("automation_rules", {})
                }
                
                response = await client.post(
                    f"{self.discount_service_url}/api/strategy/schedule",
                    json=payload
                )
                
                return {
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response": response.json() if response.status_code == 200 else response.text
                }
        except Exception as e:
            logger.error(f"Failed to apply strategy to Discount service: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_acos_campaigns(self, user_id: int) -> Dict[str, Any]:
        """Get campaigns data from ACOS service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.acos_service_url}/api/campaigns/{user_id}")
                return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            logger.error(f"Failed to get ACOS campaigns: {e}")
            return {"error": str(e)}
    
    async def get_campaign_automations(self, user_id: int) -> Dict[str, Any]:
        """Get automation data from Campaign service"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.campaign_service_url}/api/automations/{user_id}")
                return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            logger.error(f"Failed to get campaign automations: {e}")
            return {"error": str(e)}
    
    async def get_discount_campaigns(self, user_id: int) -> Dict[str, Any]:
        """Get discount campaigns from Discount Scheduler"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.discount_service_url}/api/campaigns/{user_id}")
                return response.json() if response.status_code == 200 else {"error": response.text}
        except Exception as e:
            logger.error(f"Failed to get discount campaigns: {e}")
            return {"error": str(e)}
    
    async def sync_all_services(self, user_id: int) -> Dict[str, Any]:
        """Synchronize data with all integrated services"""
        tasks = [
            self.get_acos_campaigns(user_id),
            self.get_campaign_automations(user_id),
            self.get_discount_campaigns(user_id)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "acos_campaigns": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
            "campaign_automations": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
            "discount_campaigns": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}
        }
    
    async def comprehensive_health_check(self) -> Dict[str, Any]:
        """Comprehensive health check of all integrations"""
        services_status = await self.check_all_services_status()
        
        # Additional checks can be added here
        return {
            "timestamp": asyncio.get_event_loop().time(),
            "services": services_status,
            "integration_status": "operational" if services_status.get("overall_status") == "healthy" else "degraded"
        }