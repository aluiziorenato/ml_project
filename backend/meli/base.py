"""
Base class for all Mercado Libre services.

Provides common functionality and patterns that all services can use.
"""

import httpx
import logging
from typing import Dict, Optional, Any
from datetime import datetime

from .interfaces import (
    MeliServiceInterface, 
    MeliResponse, 
    MeliPaginatedResponse,
    AnalyticsIntegrationInterface,
    OptimizerIntegrationInterface,
    LearningIntegrationInterface
)


class BaseMeliService(MeliServiceInterface):
    """
    Classe base para todos os serviços do Mercado Libre.
    
    Fornece funcionalidade comum como autenticação, logging,
    tratamento de erros e integração com outros serviços.
    """
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = logging.getLogger(f"meli.{service_name}")
        self.ml_api_url = "https://api.mercadolibre.com"
        self.timeout = 30
        
        # URLs dos serviços integrados (podem ser configurados via env vars)
        self.analytics_url = "http://localhost:8002"  # analytics_service
        self.optimizer_url = "http://localhost:8003"   # optimizer_ai
        self.learning_url = "http://localhost:8004"    # learning_service
        self.campaign_url = "http://localhost:8005"    # campaign_automation_service
    
    async def health_check(self) -> MeliResponse:
        """Verifica se o serviço está funcionando."""
        try:
            self.logger.info(f"Health check for {self.service_name}")
            return MeliResponse(
                success=True,
                data={
                    "service": self.service_name,
                    "status": "healthy",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_service_info(self) -> MeliResponse:
        """Retorna informações sobre o serviço."""
        return MeliResponse(
            success=True,
            data={
                "name": self.service_name,
                "version": "1.0.0",
                "description": f"Mercado Libre {self.service_name} integration service",
                "endpoints": self._get_available_endpoints()
            }
        )
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        """Override in subclasses to provide specific endpoints."""
        return {
            "health": f"/meli/{self.service_name}/health",
            "info": f"/meli/{self.service_name}/info"
        }
    
    async def _make_ml_request(
        self, 
        method: str, 
        endpoint: str, 
        access_token: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None
    ) -> MeliResponse:
        """
        Faz requisições padronizadas para a API do Mercado Livre.
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        url = f"{self.ml_api_url}{endpoint}"
        
        try:
            self.logger.info(f"Making {method} request to {endpoint}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers, params=params)
                elif method.upper() == "POST":
                    response = await client.post(url, headers=headers, json=json_data, params=params)
                elif method.upper() == "PUT":
                    response = await client.put(url, headers=headers, json=json_data, params=params)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers, params=params)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code < 300:
                    data = response.json() if response.content else {}
                    self.logger.info(f"Request successful: {response.status_code}")
                    return MeliResponse(
                        success=True,
                        data=data,
                        status_code=response.status_code
                    )
                else:
                    error_data = response.json() if response.content else {}
                    self.logger.warning(f"Request failed: {response.status_code}")
                    return MeliResponse(
                        success=False,
                        error=error_data.get("message", f"HTTP {response.status_code}"),
                        status_code=response.status_code,
                        data=error_data
                    )
                    
        except httpx.TimeoutException:
            self.logger.error("Request timeout")
            return MeliResponse(
                success=False,
                error="Request timeout"
            )
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def _send_analytics_event(
        self, 
        event_type: str, 
        event_data: Dict[str, Any]
    ) -> bool:
        """Envia eventos para o serviço de analytics."""
        try:
            payload = {
                "service": self.service_name,
                "event_type": event_type,
                "data": event_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{self.analytics_url}/api/events",
                    json=payload
                )
                return response.status_code < 300
                
        except Exception as e:
            self.logger.warning(f"Failed to send analytics event: {e}")
            return False
    
    async def _get_optimizer_suggestions(
        self, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtém sugestões do serviço de otimização."""
        try:
            payload = {
                "service": self.service_name,
                "context": context
            }
            
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{self.optimizer_url}/api/optimize",
                    json=payload
                )
                
                if response.status_code < 300:
                    return response.json()
                return None
                
        except Exception as e:
            self.logger.warning(f"Failed to get optimizer suggestions: {e}")
            return None
    
    async def _get_learning_insights(
        self, 
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtém insights do serviço de aprendizado."""
        try:
            payload = {
                "service": self.service_name,
                "context": context
            }
            
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.post(
                    f"{self.learning_url}/api/analyze",
                    json=payload
                )
                
                if response.status_code < 300:
                    return response.json()
                return None
                
        except Exception as e:
            self.logger.warning(f"Failed to get learning insights: {e}")
            return None