import httpx
import logging
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class MercadoLibreAPIService:
    """Service for integrating with Mercado Libre API"""
    
    def __init__(self):
        self.base_url = settings.ml_api_url
        self.client_id = settings.ml_client_id
        self.client_secret = settings.ml_client_secret
    
    async def create_seller_promotion(self, access_token: str, item_id: str, discount_percentage: float) -> Dict:
        """Create a seller promotion via ML API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        promotion_data = {
            "item_id": item_id,
            "type": "percentage",
            "value": discount_percentage,
            "name": f"Discount {discount_percentage}%",
            "start_date": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Creating seller promotion for item {item_id}")
                response = await client.post(
                    f"{self.base_url}/seller-promotions",
                    headers=headers,
                    json=promotion_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error creating seller promotion: {e}")
                raise
    
    async def pause_seller_promotion(self, access_token: str, promotion_id: str) -> Dict:
        """Pause a seller promotion via ML API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        update_data = {"status": "paused"}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Pausing seller promotion {promotion_id}")
                response = await client.put(
                    f"{self.base_url}/seller-promotions/{promotion_id}",
                    headers=headers,
                    json=update_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error pausing seller promotion: {e}")
                raise
    
    async def activate_seller_promotion(self, access_token: str, promotion_id: str) -> Dict:
        """Activate a seller promotion via ML API"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        update_data = {"status": "active"}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Activating seller promotion {promotion_id}")
                response = await client.put(
                    f"{self.base_url}/seller-promotions/{promotion_id}",
                    headers=headers,
                    json=update_data
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error activating seller promotion: {e}")
                raise
    
    async def get_seller_promotions(self, access_token: str, seller_id: str) -> List[Dict]:
        """Get all seller promotions"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Getting seller promotions for seller {seller_id}")
                response = await client.get(
                    f"{self.base_url}/seller-promotions",
                    headers=headers,
                    params={"seller_id": seller_id}
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except httpx.HTTPError as e:
                logger.error(f"Error getting seller promotions: {e}")
                raise
    
    async def get_item_visits(self, access_token: str, item_id: str, period_days: int = 30) -> Dict:
        """Get item visit statistics"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=period_days)
        
        params = {
            "date_from": start_date.strftime("%Y-%m-%d"),
            "date_to": end_date.strftime("%Y-%m-%d")
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Getting item visits for item {item_id}")
                response = await client.get(
                    f"{self.base_url}/visits/items/{item_id}",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error getting item visits: {e}")
                raise
    
    async def get_seller_items(self, access_token: str, seller_id: str, offset: int = 0, limit: int = 50) -> List[Dict]:
        """Get seller items with engagement data"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        params = {
            "seller_id": seller_id,
            "offset": offset,
            "limit": limit
        }
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Getting items for seller {seller_id}")
                response = await client.get(
                    f"{self.base_url}/sites/MLB/search",
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except httpx.HTTPError as e:
                logger.error(f"Error getting seller items: {e}")
                raise
    
    async def get_item_details(self, access_token: str, item_id: str) -> Dict:
        """Get detailed item information"""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                logger.info(f"Getting item details for {item_id}")
                response = await client.get(
                    f"{self.base_url}/items/{item_id}",
                    headers=headers
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as e:
                logger.error(f"Error getting item details: {e}")
                raise


# Global instance
ml_api_service = MercadoLibreAPIService()