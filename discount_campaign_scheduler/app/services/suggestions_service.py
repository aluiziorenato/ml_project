import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlmodel import Session, select
import numpy as np
from app.models import (
    ItemSuggestion, DiscountCampaign, SuggestionResponse
)
from app.services.ml_api_service import ml_api_service
from app.core.config import settings

logger = logging.getLogger(__name__)


class SuggestionsService:
    """Service for generating strategic ad suggestions for discount campaigns"""
    
    async def generate_suggestions(self, session: Session, seller_id: str, access_token: str) -> List[SuggestionResponse]:
        """Generate top 5 strategic suggestions for discount campaigns"""
        try:
            # Clear old suggestions
            self._clear_old_suggestions(session, seller_id)
            
            # Get seller items with engagement data
            items = await self._get_seller_items_with_engagement(seller_id, access_token)
            
            # Calculate potential scores for each item
            scored_items = await self._calculate_potential_scores(items, access_token)
            
            # Select top suggestions
            top_suggestions = self._select_top_suggestions(scored_items, settings.max_suggestions)
            
            # Store suggestions in database
            stored_suggestions = self._store_suggestions(session, seller_id, top_suggestions)
            
            # Convert to response format
            return [self._to_suggestion_response(suggestion) for suggestion in stored_suggestions]
            
        except Exception as e:
            logger.error(f"Error generating suggestions for seller {seller_id}: {e}")
            raise
    
    async def _get_seller_items_with_engagement(self, seller_id: str, access_token: str) -> List[Dict]:
        """Get seller items with recent engagement data"""
        # Get basic item list
        items = await ml_api_service.get_seller_items(
            access_token=access_token,
            seller_id=seller_id,
            limit=100  # Get more items to filter from
        )
        
        # Enrich with engagement data
        enriched_items = []
        for item in items:
            try:
                # Get item details
                item_details = await ml_api_service.get_item_details(
                    access_token=access_token,
                    item_id=item["id"]
                )
                
                # Get visit statistics
                visits_data = await ml_api_service.get_item_visits(
                    access_token=access_token,
                    item_id=item["id"],
                    period_days=30
                )
                
                enriched_item = {
                    "id": item["id"],
                    "title": item.get("title", ""),
                    "price": item.get("price", 0),
                    "category_id": item.get("category_id", ""),
                    "thumbnail": item.get("thumbnail", ""),
                    "permalink": item.get("permalink", ""),
                    "sold_quantity": item.get("sold_quantity", 0),
                    "available_quantity": item.get("available_quantity", 0),
                    "visits": visits_data.get("total_visits", 0),
                    "unique_visits": visits_data.get("unique_visits", 0),
                    "condition": item_details.get("condition", "new"),
                    "listing_type_id": item_details.get("listing_type_id", ""),
                    "attributes": item_details.get("attributes", [])
                }
                
                enriched_items.append(enriched_item)
                
            except Exception as e:
                logger.warning(f"Error enriching item {item['id']}: {e}")
                continue
        
        return enriched_items
    
    async def _calculate_potential_scores(self, items: List[Dict], access_token: str) -> List[Dict]:
        """Calculate potential scores for discount campaign success"""
        scored_items = []
        
        for item in items:
            try:
                score_data = self._calculate_item_score(item)
                
                scored_item = {
                    **item,
                    "potential_score": score_data["potential_score"],
                    "engagement_trend": score_data["engagement_trend"],
                    "score_factors": score_data["factors"]
                }
                
                scored_items.append(scored_item)
                
            except Exception as e:
                logger.warning(f"Error calculating score for item {item['id']}: {e}")
                continue
        
        return scored_items
    
    def _calculate_item_score(self, item: Dict) -> Dict:
        """Calculate potential score based on various factors"""
        factors = {}
        
        # Engagement factor (0-1)
        visits = item.get("visits", 0)
        unique_visits = item.get("unique_visits", 0)
        engagement_factor = min(1.0, (visits + unique_visits * 2) / 1000.0)
        factors["engagement"] = engagement_factor
        
        # Sales velocity factor (0-1)
        sold_quantity = item.get("sold_quantity", 0)
        velocity_factor = min(1.0, sold_quantity / 100.0)
        factors["velocity"] = velocity_factor
        
        # Price attractiveness factor (0-1)
        # Items in $20-$200 range tend to perform better with discounts
        price = item.get("price", 0)
        if 20 <= price <= 200:
            price_factor = 1.0
        elif price < 20:
            price_factor = 0.6
        elif price <= 500:
            price_factor = 0.8
        else:
            price_factor = 0.5
        factors["price"] = price_factor
        
        # Stock availability factor (0-1)
        available_quantity = item.get("available_quantity", 0)
        stock_factor = min(1.0, available_quantity / 50.0)
        factors["stock"] = stock_factor
        
        # Category factor (some categories perform better)
        category_id = item.get("category_id", "")
        category_factor = self._get_category_factor(category_id)
        factors["category"] = category_factor
        
        # Condition factor (new items generally perform better)
        condition = item.get("condition", "new")
        condition_factor = 1.0 if condition == "new" else 0.7
        factors["condition"] = condition_factor
        
        # Calculate weighted score
        weights = {
            "engagement": 0.3,
            "velocity": 0.25,
            "price": 0.15,
            "stock": 0.15,
            "category": 0.1,
            "condition": 0.05
        }
        
        potential_score = sum(factors[factor] * weights[factor] for factor in factors)
        
        # Calculate engagement trend (simplified)
        engagement_trend = np.random.uniform(0.7, 1.3)  # Mock trend calculation
        
        return {
            "potential_score": round(potential_score, 3),
            "engagement_trend": round(engagement_trend, 3),
            "factors": factors
        }
    
    def _get_category_factor(self, category_id: str) -> float:
        """Get category performance factor"""
        # High-performing categories for discount campaigns
        high_perf_categories = [
            "MLB1051",  # Electronics
            "MLB1648",  # Home & Garden
            "MLB1276",  # Sports
            "MLB1430",  # Fashion
        ]
        
        if any(cat in category_id for cat in high_perf_categories):
            return 1.0
        else:
            return 0.8
    
    def _select_top_suggestions(self, scored_items: List[Dict], max_suggestions: int) -> List[Dict]:
        """Select top suggestions based on potential score"""
        # Filter out items that already have active campaigns
        # Sort by potential score
        sorted_items = sorted(
            scored_items,
            key=lambda x: x["potential_score"],
            reverse=True
        )
        
        # Apply additional filters
        filtered_items = []
        for item in sorted_items:
            # Minimum criteria
            if (item["potential_score"] >= 0.5 and 
                item["available_quantity"] > 0 and
                item["price"] > 0):
                filtered_items.append(item)
        
        return filtered_items[:max_suggestions]
    
    def _store_suggestions(self, session: Session, seller_id: str, suggestions: List[Dict]) -> List[ItemSuggestion]:
        """Store suggestions in database"""
        stored_suggestions = []
        
        for suggestion in suggestions:
            item_suggestion = ItemSuggestion(
                seller_id=seller_id,
                item_id=suggestion["id"],
                title=suggestion["title"],
                image_url=suggestion.get("thumbnail"),
                current_price=suggestion["price"],
                category_id=suggestion["category_id"],
                recent_clicks=suggestion.get("visits", 0),
                recent_impressions=suggestion.get("unique_visits", 0) * 2,
                recent_views=suggestion.get("visits", 0),
                potential_score=suggestion["potential_score"],
                engagement_trend=suggestion["engagement_trend"]
            )
            
            session.add(item_suggestion)
            stored_suggestions.append(item_suggestion)
        
        session.commit()
        
        for suggestion in stored_suggestions:
            session.refresh(suggestion)
        
        logger.info(f"Stored {len(stored_suggestions)} suggestions for seller {seller_id}")
        return stored_suggestions
    
    def _clear_old_suggestions(self, session: Session, seller_id: str):
        """Clear old suggestions for seller"""
        cutoff_time = datetime.utcnow() - timedelta(hours=settings.suggestion_refresh_hours)
        
        statement = select(ItemSuggestion).where(
            ItemSuggestion.seller_id == seller_id,
            ItemSuggestion.suggested_at < cutoff_time
        )
        old_suggestions = session.exec(statement).all()
        
        for suggestion in old_suggestions:
            session.delete(suggestion)
        
        session.commit()
        
        if old_suggestions:
            logger.info(f"Cleared {len(old_suggestions)} old suggestions for seller {seller_id}")
    
    def _to_suggestion_response(self, suggestion: ItemSuggestion) -> SuggestionResponse:
        """Convert ItemSuggestion to SuggestionResponse"""
        return SuggestionResponse(
            item_id=suggestion.item_id,
            title=suggestion.title,
            image_url=suggestion.image_url,
            current_price=suggestion.current_price,
            recent_clicks=suggestion.recent_clicks,
            potential_score=suggestion.potential_score,
            engagement_trend=suggestion.engagement_trend
        )
    
    def get_stored_suggestions(self, session: Session, seller_id: str) -> List[SuggestionResponse]:
        """Get stored suggestions for a seller"""
        statement = select(ItemSuggestion).where(
            ItemSuggestion.seller_id == seller_id,
            ItemSuggestion.is_active == True
        ).order_by(ItemSuggestion.potential_score.desc())
        
        suggestions = session.exec(statement).all()
        
        return [self._to_suggestion_response(suggestion) for suggestion in suggestions]
    
    async def refresh_suggestions_if_needed(
        self, 
        session: Session, 
        seller_id: str, 
        access_token: str
    ) -> List[SuggestionResponse]:
        """Refresh suggestions if they are outdated"""
        # Check if we have recent suggestions
        cutoff_time = datetime.utcnow() - timedelta(hours=settings.suggestion_refresh_hours)
        
        statement = select(ItemSuggestion).where(
            ItemSuggestion.seller_id == seller_id,
            ItemSuggestion.suggested_at >= cutoff_time,
            ItemSuggestion.is_active == True
        )
        recent_suggestions = session.exec(statement).all()
        
        if recent_suggestions:
            # Return existing suggestions
            return [self._to_suggestion_response(s) for s in recent_suggestions]
        else:
            # Generate new suggestions
            return await self.generate_suggestions(session, seller_id, access_token)


# Global instance
suggestions_service = SuggestionsService()