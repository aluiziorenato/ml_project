"""
Orders Service for Mercado Libre Integration

Handles order management, status tracking, and order analytics.
Integrates with pricing optimization and campaign automation services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class OrdersService(BaseMeliService):
    """
    Serviço para gerenciamento de pedidos do Mercado Libre.
    
    Funcionalidades:
    - Listar pedidos
    - Obter detalhes de pedidos
    - Atualizar status de pedidos
    - Analytics de vendas
    - Integração com serviços de otimização
    """
    
    def __init__(self):
        super().__init__("orders_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista pedidos do vendedor."""
        try:
            params = {
                "seller": user_id,
                "offset": offset,
                "limit": limit
            }
            
            # Adiciona filtros específicos
            if filters:
                if "status" in filters:
                    params["order.status"] = filters["status"]
                if "date_from" in filters:
                    params["order.date_created.from"] = filters["date_from"]
                if "date_to" in filters:
                    params["order.date_created.to"] = filters["date_to"]
            
            response = await self._make_ml_request(
                "GET",
                "/orders/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                
                # Envia dados para analytics
                await self._send_analytics_event("orders_listed", {
                    "user_id": user_id,
                    "total_orders": data.get("paging", {}).get("total", 0),
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
            self.logger.error(f"Error listing orders: {e}")
            return MeliPaginatedResponse(
                success=False,
                error=str(e)
            )
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes completos de um pedido."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/orders/{item_id}",
                access_token
            )
            
            if response.success:
                # Envia evento para analytics
                await self._send_analytics_event("order_details_viewed", {
                    "order_id": item_id,
                    "status": response.data.get("status"),
                    "total_amount": response.data.get("total_amount")
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting order details: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def update_order_status(
        self, 
        access_token: str, 
        order_id: str, 
        status: str
    ) -> MeliResponse:
        """Atualiza o status de um pedido."""
        try:
            response = await self._make_ml_request(
                "PUT",
                f"/orders/{order_id}",
                access_token,
                json_data={"status": status}
            )
            
            if response.success:
                await self._send_analytics_event("order_status_updated", {
                    "order_id": order_id,
                    "new_status": status
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error updating order status: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    async def get_order_analytics(
        self, 
        access_token: str, 
        user_id: str,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> MeliResponse:
        """Obtém analytics detalhados dos pedidos."""
        try:
            # Define período padrão (últimos 30 dias)
            if not date_from:
                date_from = (datetime.now() - timedelta(days=30)).isoformat()
            if not date_to:
                date_to = datetime.now().isoformat()
            
            # Busca pedidos do período
            orders_response = await self.list_items(
                access_token, 
                user_id, 
                offset=0, 
                limit=200,  # Busca mais pedidos para analytics
                filters={
                    "date_from": date_from,
                    "date_to": date_to
                }
            )
            
            if not orders_response.success:
                return MeliResponse(
                    success=False,
                    error=orders_response.error
                )
            
            orders = orders_response.data or []
            
            # Calcula métricas
            analytics = self._calculate_order_metrics(orders)
            
            # Busca sugestões de otimização
            optimization_context = {
                "orders_count": len(orders),
                "avg_order_value": analytics.get("avg_order_value", 0),
                "conversion_metrics": analytics
            }
            optimizer_suggestions = await self._get_optimizer_suggestions(optimization_context)
            
            # Busca insights de aprendizado
            learning_insights = await self._get_learning_insights({
                "service": "orders",
                "metrics": analytics,
                "time_range": {"from": date_from, "to": date_to}
            })
            
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
            self.logger.error(f"Error getting order analytics: {e}")
            return MeliResponse(
                success=False,
                error=str(e)
            )
    
    def _calculate_order_metrics(self, orders: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcula métricas dos pedidos."""
        if not orders:
            return {
                "total_orders": 0,
                "total_revenue": 0,
                "avg_order_value": 0,
                "status_distribution": {},
                "payment_methods": {}
            }
        
        total_revenue = sum(float(order.get("total_amount", 0)) for order in orders)
        avg_order_value = total_revenue / len(orders) if orders else 0
        
        # Distribuição por status
        status_dist = {}
        payment_methods = {}
        
        for order in orders:
            status = order.get("status", "unknown")
            status_dist[status] = status_dist.get(status, 0) + 1
            
            # Método de pagamento
            payments = order.get("payments", [])
            for payment in payments:
                method = payment.get("payment_method_id", "unknown")
                payment_methods[method] = payment_methods.get(method, 0) + 1
        
        return {
            "total_orders": len(orders),
            "total_revenue": total_revenue,
            "avg_order_value": avg_order_value,
            "status_distribution": status_dist,
            "payment_methods": payment_methods
        }
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        """Endpoints disponíveis do serviço de pedidos."""
        base_endpoints = super()._get_available_endpoints()
        orders_endpoints = {
            "list_orders": f"/meli/{self.service_name}/orders",
            "order_details": f"/meli/{self.service_name}/orders/{{order_id}}",
            "update_status": f"/meli/{self.service_name}/orders/{{order_id}}/status",
            "analytics": f"/meli/{self.service_name}/analytics"
        }
        return {**base_endpoints, **orders_endpoints}


# Instância global do serviço
orders_service = OrdersService()