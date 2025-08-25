"""
Inventory Service for Mercado Libre Integration

Handles inventory management, stock control, and automated restocking.
Integrates with sales prediction and optimization services.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from ..base import BaseMeliService
from ..interfaces import MeliResponse, MeliPaginatedResponse


class InventoryService(BaseMeliService):
    """
    Serviço para gerenciamento de inventário do Mercado Libre.
    
    Funcionalidades:
    - Controle de estoque
    - Previsão de demanda
    - Alertas de estoque baixo
    - Integração com vendas
    - Otimização de reposição
    """
    
    def __init__(self):
        super().__init__("inventory_service")
    
    async def list_items(
        self, 
        access_token: str, 
        user_id: str, 
        offset: int = 0, 
        limit: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> MeliPaginatedResponse:
        """Lista items do inventário."""
        try:
            params = {
                "seller_id": user_id,
                "offset": offset,
                "limit": limit
            }
            
            if filters:
                if "category_id" in filters:
                    params["category"] = filters["category_id"]
                if "status" in filters:
                    params["status"] = filters["status"]
                if "low_stock" in filters and filters["low_stock"]:
                    params["available_quantity.lt"] = 10
            
            response = await self._make_ml_request(
                "GET",
                f"/users/{user_id}/items/search",
                access_token,
                params=params
            )
            
            if response.success:
                data = response.data
                items = data.get("results", [])
                
                # Analisa estoque e gera alertas
                stock_analysis = await self._analyze_stock_levels(access_token, items)
                
                await self._send_analytics_event("inventory_listed", {
                    "user_id": user_id,
                    "total_items": len(items),
                    "low_stock_items": stock_analysis.get("low_stock_count", 0)
                })
                
                return MeliPaginatedResponse(
                    success=True,
                    data=items,
                    total=data.get("paging", {}).get("total"),
                    offset=data.get("paging", {}).get("offset"),
                    limit=data.get("paging", {}).get("limit"),
                    has_next=data.get("paging", {}).get("offset", 0) + limit < data.get("paging", {}).get("total", 0),
                    metadata=stock_analysis
                )
            
            return MeliPaginatedResponse(success=False, error=response.error)
            
        except Exception as e:
            self.logger.error(f"Error listing inventory: {e}")
            return MeliPaginatedResponse(success=False, error=str(e))
    
    async def get_item_details(
        self, 
        access_token: str, 
        item_id: str
    ) -> MeliResponse:
        """Obtém detalhes de estoque de um item."""
        try:
            response = await self._make_ml_request(
                "GET",
                f"/items/{item_id}",
                access_token
            )
            
            if response.success:
                item_data = response.data
                
                # Adiciona previsões e sugestões
                predictions = await self._get_demand_predictions(item_id, item_data)
                optimization = await self._get_restock_suggestions(item_id, item_data)
                
                result = {
                    **item_data,
                    "demand_predictions": predictions,
                    "restock_suggestions": optimization
                }
                
                return MeliResponse(success=True, data=result)
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error getting inventory details: {e}")
            return MeliResponse(success=False, error=str(e))
    
    async def update_stock(
        self, 
        access_token: str, 
        item_id: str, 
        new_quantity: int
    ) -> MeliResponse:
        """Atualiza quantidade em estoque."""
        try:
            response = await self._make_ml_request(
                "PUT",
                f"/items/{item_id}",
                access_token,
                json_data={"available_quantity": new_quantity}
            )
            
            if response.success:
                await self._send_analytics_event("stock_updated", {
                    "item_id": item_id,
                    "new_quantity": new_quantity
                })
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error updating stock: {e}")
            return MeliResponse(success=False, error=str(e))
    
    async def get_stock_alerts(
        self, 
        access_token: str, 
        user_id: str
    ) -> MeliResponse:
        """Obtém alertas de estoque baixo."""
        try:
            inventory_response = await self.list_items(
                access_token, user_id, limit=200,
                filters={"low_stock": True}
            )
            
            if inventory_response.success:
                low_stock_items = inventory_response.data
                
                alerts = []
                for item in low_stock_items:
                    alert = {
                        "item_id": item.get("id"),
                        "title": item.get("title"),
                        "current_stock": item.get("available_quantity", 0),
                        "recommended_restock": await self._calculate_restock_amount(item),
                        "urgency": self._calculate_urgency(item),
                        "estimated_stockout_days": await self._estimate_stockout_date(item)
                    }
                    alerts.append(alert)
                
                return MeliResponse(
                    success=True,
                    data={
                        "alerts": alerts,
                        "total_alerts": len(alerts),
                        "critical_alerts": len([a for a in alerts if a["urgency"] == "critical"])
                    }
                )
            
            return MeliResponse(success=False, error=inventory_response.error)
            
        except Exception as e:
            self.logger.error(f"Error getting stock alerts: {e}")
            return MeliResponse(success=False, error=str(e))
    
    async def _analyze_stock_levels(
        self, 
        access_token: str, 
        items: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analisa níveis de estoque."""
        low_stock_items = []
        out_of_stock_items = []
        
        for item in items:
            quantity = item.get("available_quantity", 0)
            if quantity == 0:
                out_of_stock_items.append(item)
            elif quantity < 10:  # Threshold configurável
                low_stock_items.append(item)
        
        return {
            "low_stock_count": len(low_stock_items),
            "out_of_stock_count": len(out_of_stock_items),
            "low_stock_items": low_stock_items[:5],  # Top 5
            "out_of_stock_items": out_of_stock_items[:5]
        }
    
    async def _get_demand_predictions(
        self, 
        item_id: str, 
        item_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtém previsões de demanda."""
        context = {
            "item_id": item_id,
            "current_stock": item_data.get("available_quantity", 0),
            "sales_data": item_data.get("sold_quantity", 0)
        }
        
        predictions = await self._get_learning_insights(context)
        return predictions.get("demand_forecast") if predictions else None
    
    async def _get_restock_suggestions(
        self, 
        item_id: str, 
        item_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Obtém sugestões de reposição."""
        context = {
            "item_id": item_id,
            "current_stock": item_data.get("available_quantity", 0),
            "sales_velocity": item_data.get("sold_quantity", 0)
        }
        
        suggestions = await self._get_optimizer_suggestions(context)
        return suggestions
    
    async def _calculate_restock_amount(self, item: Dict[str, Any]) -> int:
        """Calcula quantidade recomendada para reposição."""
        # Lógica simplificada
        sold_quantity = item.get("sold_quantity", 0)
        return max(30, sold_quantity // 10)  # Pelo menos 30, ou 10% das vendas
    
    def _calculate_urgency(self, item: Dict[str, Any]) -> str:
        """Calcula urgência do alerta."""
        quantity = item.get("available_quantity", 0)
        if quantity == 0:
            return "critical"
        elif quantity < 5:
            return "high"
        elif quantity < 10:
            return "medium"
        return "low"
    
    async def _estimate_stockout_date(self, item: Dict[str, Any]) -> int:
        """Estima dias até ficar sem estoque."""
        # Lógica simplificada
        return max(1, item.get("available_quantity", 0) * 2)
    
    def _get_available_endpoints(self) -> Dict[str, str]:
        base_endpoints = super()._get_available_endpoints()
        inventory_endpoints = {
            "inventory": f"/meli/{self.service_name}/inventory",
            "stock_alerts": f"/meli/{self.service_name}/alerts",
            "update_stock": f"/meli/{self.service_name}/items/{{item_id}}/stock",
            "item_details": f"/meli/{self.service_name}/items/{{item_id}}"
        }
        return {**base_endpoints, **inventory_endpoints}


# Instância global do serviço
inventory_service = InventoryService()