from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlmodel import Session
from typing import List
from app.core.database import get_session
from app.models import KeywordUploadResponse, KeywordResponse
from app.services.auth_service import get_current_user, get_current_seller
from app.services.keyword_service import keyword_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Keyword Management"])


@router.post("/upload-keywords-csv", response_model=KeywordUploadResponse)
async def upload_keywords_csv(
    file: UploadFile = File(..., description="CSV file from Google Keyword Planner"),
    user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Upload and process Google Keyword Planner CSV file"""
    seller_id = user.get("seller_id")
    if not seller_id:
        raise HTTPException(status_code=400, detail="Seller ID not found")
    
    # Validate file type
    if not file.filename.lower().endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Process the CSV
        result = await keyword_service.process_csv_upload(
            file_content=file_content,
            filename=file.filename,
            seller_id=seller_id,
            session=session
        )
        
        logger.info(f"Successfully processed keyword CSV for seller {seller_id}: {result['batch_id']}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing keyword CSV upload: {e}")
        raise HTTPException(status_code=500, detail="Error processing CSV file")


@router.get("/keywords", response_model=List[KeywordResponse])
async def get_keywords(
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(None, description="Search within keywords")
):
    """Get uploaded keywords for the seller"""
    try:
        keywords = keyword_service.get_keywords_for_seller(seller_id, session)
        
        # Apply search filter if provided
        if search:
            keywords = [k for k in keywords if search.lower() in k.keyword.lower()]
        
        # Limit results
        keywords = keywords[:limit]
        
        return [
            KeywordResponse(
                id=k.id,
                keyword=k.keyword,
                search_volume=k.search_volume,
                competition=k.competition,
                competition_score=k.competition_score,
                top_of_page_bid_low=k.top_of_page_bid_low,
                top_of_page_bid_high=k.top_of_page_bid_high,
                relevance_score=k.relevance_score,
                category_match=k.category_match,
                created_at=k.created_at
            )
            for k in keywords
        ]
        
    except Exception as e:
        logger.error(f"Error getting keywords: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving keywords")


@router.get("/keyword-batches")
async def get_keyword_upload_batches(
    seller_id: str = Depends(get_current_seller),
    session: Session = Depends(get_session)
):
    """Get keyword upload batch history"""
    try:
        batches = keyword_service.get_upload_batches(seller_id, session)
        
        return [
            {
                "batch_id": batch.id,
                "filename": batch.filename,
                "total_keywords": batch.total_keywords,
                "processed_keywords": batch.processed_keywords,
                "failed_keywords": batch.failed_keywords,
                "status": batch.status,
                "uploaded_at": batch.uploaded_at,
                "completed_at": batch.completed_at,
                "error_message": batch.error_message
            }
            for batch in batches
        ]
        
    except Exception as e:
        logger.error(f"Error getting upload batches: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving upload history")