"""
SEO optimization routes.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.services.seo import optimize_text
from app.core.security import get_current_user
from app.models import User
import logging

logger = logging.getLogger("app.routers.seo")
router = APIRouter(prefix="/api/seo", tags=["seo"])


class OptimizeTextRequest(BaseModel):
    text: str
    keywords: Optional[List[str]] = None
    max_length: int = 160


class OptimizeTextResponse(BaseModel):
    original: str
    cleaned: str
    title: str
    meta_description: str
    keywords: List[str]
    slug: str


@router.post("/optimize", response_model=OptimizeTextResponse)
def optimize_text_endpoint(
    request: OptimizeTextRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize text for SEO purposes.
    
    Returns optimized versions including title, meta description, keywords and slug.
    """
    try:
        result = optimize_text(
            text=request.text,
            keywords=request.keywords,
            max_length=request.max_length
        )
        
        logger.info(f"SEO optimization completed for user {current_user.email}")
        return OptimizeTextResponse(**result)
        
    except ValueError as e:
        logger.error(f"SEO optimization error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected SEO optimization error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")