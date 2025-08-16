from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.models import SuggestionResponse
from app.services.auth_service import get_current_user, get_current_seller, auth_service
from app.services.suggestions_service import suggestions_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/suggestions", tags=["Strategic Suggestions"])


@router.get("/", response_model=List[SuggestionResponse])
async def get_suggestions(
    refresh: bool = Query(False, description="Force refresh suggestions"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get strategic ad suggestions for discount campaigns"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    try:
        # Get access token for ML API calls
        access_token = await auth_service.get_seller_access_token(seller_id)
        if not access_token:
            # Fallback to token from user data
            access_token = user.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Could not get access token")
        
        if refresh:
            # Force generation of new suggestions
            suggestions = await suggestions_service.generate_suggestions(
                session=session,
                seller_id=seller_id,
                access_token=access_token
            )
        else:
            # Get existing suggestions or refresh if needed
            suggestions = await suggestions_service.refresh_suggestions_if_needed(
                session=session,
                seller_id=seller_id,
                access_token=access_token
            )
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error getting suggestions for seller {seller_id}: {e}")
        raise HTTPException(status_code=500, detail="Error generating suggestions")


@router.post("/refresh", response_model=List[SuggestionResponse])
async def refresh_suggestions(
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Force refresh of strategic suggestions"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    try:
        # Get access token for ML API calls
        access_token = await auth_service.get_seller_access_token(seller_id)
        if not access_token:
            access_token = user.get("access_token")
            if not access_token:
                raise HTTPException(status_code=400, detail="Could not get access token")
        
        suggestions = await suggestions_service.generate_suggestions(
            session=session,
            seller_id=seller_id,
            access_token=access_token
        )
        
        return suggestions
        
    except Exception as e:
        logger.error(f"Error refreshing suggestions for seller {seller_id}: {e}")
        raise HTTPException(status_code=500, detail="Error refreshing suggestions")


@router.get("/stored", response_model=List[SuggestionResponse])
async def get_stored_suggestions(
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get stored suggestions without refreshing"""
    suggestions = suggestions_service.get_stored_suggestions(
        session=session,
        seller_id=seller_id
    )
    
    return suggestions


@router.post("/{item_id}/apply-campaign")
async def apply_campaign_to_suggestion(
    item_id: str,
    discount_percentage: float = Query(..., ge=1, le=50, description="Discount percentage (1-50)"),
    campaign_name: str = Query(..., description="Campaign name"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Apply discount campaign to a suggested item"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    # Import here to avoid circular imports
    from app.models import DiscountCampaign, CampaignStatus
    
    try:
        # Create new campaign for the suggested item
        campaign = DiscountCampaign(
            seller_id=seller_id,
            item_id=item_id,
            campaign_name=campaign_name,
            discount_percentage=discount_percentage,
            status=CampaignStatus.DRAFT
        )
        
        session.add(campaign)
        session.commit()
        session.refresh(campaign)
        
        logger.info(f"Applied campaign {campaign.id} to suggested item {item_id}")
        
        return {
            "message": "Campaign applied successfully",
            "campaign_id": campaign.id,
            "item_id": item_id,
            "discount_percentage": discount_percentage
        }
        
    except Exception as e:
        logger.error(f"Error applying campaign to item {item_id}: {e}")
        raise HTTPException(status_code=500, detail="Error applying campaign")


@router.get("/analytics")
async def get_suggestions_analytics(
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get analytics about suggestions and their performance"""
    from sqlmodel import select
    from app.models import ItemSuggestion, DiscountCampaign
    from datetime import datetime, timedelta
    
    try:
        # Get suggestion statistics
        suggestions_statement = select(ItemSuggestion).where(
            ItemSuggestion.seller_id == seller_id,
            ItemSuggestion.is_active == True
        )
        suggestions = session.exec(suggestions_statement).all()
        
        # Get campaigns created from suggestions (approximate by matching item_ids)
        suggestion_item_ids = [s.item_id for s in suggestions]
        
        campaigns_statement = select(DiscountCampaign).where(
            DiscountCampaign.seller_id == seller_id,
            DiscountCampaign.item_id.in_(suggestion_item_ids)
        )
        campaigns_from_suggestions = session.exec(campaigns_statement).all()
        
        # Calculate metrics
        total_suggestions = len(suggestions)
        applied_campaigns = len(campaigns_from_suggestions)
        application_rate = (applied_campaigns / total_suggestions) * 100 if total_suggestions > 0 else 0
        
        # Average potential score
        avg_potential_score = sum(s.potential_score for s in suggestions) / len(suggestions) if suggestions else 0
        
        # Top performing suggestions (by potential score)
        top_suggestions = sorted(suggestions, key=lambda x: x.potential_score, reverse=True)[:3]
        
        return {
            "total_suggestions": total_suggestions,
            "applied_campaigns": applied_campaigns,
            "application_rate": round(application_rate, 2),
            "avg_potential_score": round(avg_potential_score, 3),
            "top_suggestions": [
                {
                    "item_id": s.item_id,
                    "title": s.title,
                    "potential_score": s.potential_score,
                    "recent_clicks": s.recent_clicks
                }
                for s in top_suggestions
            ],
            "last_updated": suggestions[0].suggested_at if suggestions else None
        }
        
    except Exception as e:
        logger.error(f"Error getting suggestions analytics: {e}")
        raise HTTPException(status_code=500, detail="Error getting analytics")