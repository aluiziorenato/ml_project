"""
Shipments Service for Mercado Libre Integration

Handles shipping management, tracking, and logistics optimization.
Integrates with orders and inventory services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class ShipmentsService(BaseMeliService):
    """
    Serviço para gerenciamento de envios do Mercado Libre.
    
    Funcionalidades:
    - Listar envios
    - Tracking de envios
    - Gerenciar etiquetas
    - Analytics de logística
    - Otimização de custos de envio
    """
    
    def __init__(self):
        super().__init__("shipments_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista envios do vendedor."""
        try:
            params = {
                "seller_id": user_id,
                "offset": offset,
                "limit": limit
            }
            
            # Filtros específicos para envios
            if filters:
                if "status" in filters:
                    params["status"] = filters["status"]
                if "shipping_method" in filters:
                    params["method"] = filters["shipping_method"]
                if "date_from" in filters:
                    params["date_created.from"] = filters["date_from"]
                if "date_to" in filters:
                    params["date_created.to"] = filters["date_to"]
            
            response = await self._make_ml_request(
                "GET",
                "/shipments/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                
                # Analytics de envios
                await self._send_analytics_event("shipments_listed", {
                    "user_id": user_id,
                    "total_shipments": data.get("paging", {}).get("total", 0),
                    "filters": filters
                })
                
                return MeliPaginatedResponse(
                    success=True,
                    data=data.get("results", []),
                    total=data.get("paging", {}).get("total"),
                    offset=data.get("paging", {}).get("offset"),
                    limit=data.get("paging", {}).get("limit"),
                    has_next=data.get("paging", {}).get("offset", 0) + limit < data.get("paging", {}).get("total", 0)
                )
            
            return MeliPaginatedResponse(
                success=False,
                error=response.error
            )
            
        except Exception as e:
            self.logger.error(f"Error listing shipments: {e}")
            return MeliPaginatedResponse(
                success=False,
                error=str(e)
            )
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes completos de um envio."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/shipments/{item_id}",
                access_token
            )
            
            if response.success:
                await self._send_analytics_event("shipment_details_viewed", {
                    "shipment_id": item_id,
                    "status": response.data.get("status")
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting shipment details: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_tracking_info(
        self, 
        access_token: str, 
        shipment_id: str
    ) -> MeliResponse:
        """Obtém informações de rastreamento de um envio."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/shipments/{shipment_id}/tracking",
                access_token
            )
            
            if response.success:
                await self._send_analytics_event("tracking_viewed", {
                    "shipment_id": shipment_id
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting tracking info: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def update_shipment_status(
        self, 
        access_token: str, 
        shipment_id: str, 
        status: str
    ) -> MeliResponse:
        """Atualiza o status de um envio."""
        try:
            response = await self._make_ml_request(
                "PUT",
                f"/shipments/{shipment_id}",
                access_token,
                json_data={"status": status}
            )
            
            if response.success:
                await self._send_analytics_event("shipment_status_updated", {
                    "shipment_id": shipment_id,
                    "new_status": status
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error updating shipment status: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_shipping_options(
        self, 
        access_token: str, 
        item_id: str, 
        zip_code: str
    ) -> MeliResponse:
        """Obtém opções de envio para um item e CEP."""
        try:
            params = {
                "item_id": item_id,
                "zip_code": zip_code
            }
            
            response = await self._make_ml_request(
                "GET",
                "/shipping_options",
                access_token,
                params=params
            )
            
            if response.success:
                # Busca otimizações de custo de envio
                optimization_context = {
                    "item_id": item_id,
                    "zip_code": zip_code,
                    "shipping_options": response.data.get("options", [])
                }
                
                optimizer_suggestions = await self._get_optimizer_suggestions(optimization_context)
                
                result = response.data
                if optimizer_suggestions:
                    result["optimization_suggestions"] = optimizer_suggestions
                
                return MeliResponse(
                    success=True,
                    data=result
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting shipping options: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def create_shipping_label(
        self, 
        access_token: str, 
        shipment_data: Dict[str, Any]
    ) -> MeliResponse:
        """Cria etiqueta de envio."""
        try:
            response = await self._make_ml_request(
                "POST",
                "/shipment_labels",
                access_token,
                json_data=shipment_data
            )
            
            if response.success:
                await self._send_analytics_event("shipping_label_created", {
                    "shipment_id": shipment_data.get("shipment_id"),
                    "service_type": shipment_data.get("service_type")
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating shipping label: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_shipping_analytics(
        self, 
        access_token: str, 
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> MeliResponse:
        """Obtém analytics de envios."""
        try:
            # Busca envios do período
            shipments_response = await self.list_items(
                access_token,
                user_id,
                offset=0,
                limit=200,
                filters={
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            
            if not shipments_response.success:
                return MeliResponse(
                    success=False,
                    error=shipments_response.error
                )
            
            shipments = shipments_response.data or []
            
            # Calcula métricas
            analytics = self._calculate_shipping_metrics(shipments)
            
            # Busca insights e otimizações
            context = {
                "shipments_count": len(shipments),
                "metrics": analytics
            }
            
            optimizer_suggestions = await self._get_optimizer_suggestions(context)
            learning_insights = await self._get_learning_insights(context)
            
            result = {
                "analytics": analytics,
                "optimization_suggestions": optimizer_suggestions,
                "learning_insights": learning_insights,
                "period": {"from": date_from, "to": date_to}
            }
            
            return MeliResponse(
                success=True,
                data=result
            )
            
        except Exception as e:
            self.logger.error(f"Error getting shipping analytics: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    def _calculate_shipping_metrics(self, shipments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas de envios."""
        if not shipments:
            return {
                "total_shipments": 0,
                "total_shipping_cost": 0,
                "avg_shipping_cost": 0,
                "status_distribution": {},
                "method_distribution": {},
                "delivery_time_avg": 0
            }
        
        total_cost = sum(float(ship.get("shipping_cost", {}).get("list_cost", 0)) for ship in shipments)
        avg_cost = total_cost / len(shipments) if shipments else 0
        
        # Distribuições
        status_dist = {}
        method_dist = {}
        
        for shipment in shipments:
            status = shipment.get("status", "unknown")
            status_dist[status] = status_dist.get(status, 0) + 1
            
            method = shipment.get("shipping_method", {}).get("name", "unknown")
            method_dist[method] = method_dist.get(method, 0) + 1
        
        return {
            "total_shipments": len(shipments),
            "total_shipping_cost": total_cost,
            "avg_shipping_cost": avg_cost,
            "status_distribution": status_dist,
            "method_distribution": method_dist
        }
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        """Endpoints disponíveis do serviço de envios."""
        base_endpoints = super()._get_available_endpoints()
        shipments_endpoints = {
            "list_shipments": f"/meli/{self.service_name}/shipments",
            "shipment_details": f"/meli/{self.service_name}/shipments/{{shipment_id}}",
            "tracking": f"/meli/{self.service_name}/shipments/{{shipment_id}}/tracking",
            "shipping_options": f"/meli/{self.service_name}/shipping_options",
            "create_label": f"/meli/{self.service_name}/labels",
            "analytics": f"/meli/{self.service_name}/analytics"
        }
        return {**base_endpoints, **shipments_endpoints}


# Instância global do serviço
shipments_service = ShipmentsService()