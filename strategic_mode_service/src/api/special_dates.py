from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from src.core.database import get_db
from src.models.schemas import (
    SpecialDateCreate, SpecialDateUpdate, SpecialDateResponse
)
from src.services.special_dates_service import SpecialDatesService

router = APIRouter()

@router.get("/", response_model=List[SpecialDateResponse])
async def get_special_dates(
    skip: int = 0,
    limit: int = 100,
    is_active: Optional[bool] = None,
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db)
):
    """Get all special dates with optional filters"""
    service = SpecialDatesService(db)
    return service.get_special_dates(
        skip=skip, 
        limit=limit, 
        is_active=is_active,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/active", response_model=List[SpecialDateResponse])
async def get_active_special_dates(
    current_date: Optional[date] = Query(None, description="Date to check against (defaults to today)"),
    db: Session = Depends(get_db)
):
    """Get currently active special dates"""
    service = SpecialDatesService(db)
    return service.get_active_special_dates(current_date)

@router.get("/{date_id}", response_model=SpecialDateResponse)
async def get_special_date(
    date_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific special date by ID"""
    service = SpecialDatesService(db)
    special_date = service.get_special_date(date_id)
    if not special_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Special date not found"
        )
    return special_date

@router.post("/", response_model=SpecialDateResponse)
async def create_special_date(
    special_date: SpecialDateCreate,
    db: Session = Depends(get_db)
):
    """Create a new special date"""
    service = SpecialDatesService(db)
    try:
        return service.create_special_date(special_date)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{date_id}", response_model=SpecialDateResponse)
async def update_special_date(
    date_id: int,
    date_update: SpecialDateUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing special date"""
    service = SpecialDatesService(db)
    special_date = service.update_special_date(date_id, date_update)
    if not special_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Special date not found"
        )
    return special_date

@router.delete("/{date_id}")
async def delete_special_date(
    date_id: int,
    db: Session = Depends(get_db)
):
    """Delete a special date"""
    service = SpecialDatesService(db)
    success = service.delete_special_date(date_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Special date not found"
        )
    return {"message": "Special date deleted successfully"}

@router.post("/{date_id}/activate")
async def activate_special_date(
    date_id: int,
    db: Session = Depends(get_db)
):
    """Activate a special date"""
    service = SpecialDatesService(db)
    special_date = service.activate_special_date(date_id)
    if not special_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Special date not found"
        )
    return {"message": "Special date activated successfully"}

@router.post("/{date_id}/deactivate")
async def deactivate_special_date(
    date_id: int,
    db: Session = Depends(get_db)
):
    """Deactivate a special date"""
    service = SpecialDatesService(db)
    special_date = service.deactivate_special_date(date_id)
    if not special_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Special date not found"
        )
    return {"message": "Special date deactivated successfully"}

@router.get("/presets/default")
async def get_default_special_dates():
    """Get default special dates presets"""
    return {
        "special_dates": [
            {
                "name": "Black Friday",
                "description": "Black Friday - maior data de vendas do ano",
                "start_date": "2024-11-29",
                "end_date": "2024-11-29",
                "budget_multiplier": 3.0,
                "acos_adjustment": 10.0,
                "peak_hours": [
                    {"start": 8, "end": 12},
                    {"start": 18, "end": 23}
                ],
                "priority_categories": ["eletronicos", "moda", "casa"],
                "custom_settings": {
                    "max_bid_increase": 100,
                    "emergency_budget": True,
                    "competitor_monitoring": True
                }
            },
            {
                "name": "Cyber Monday",
                "description": "Cyber Monday - foco em eletrônicos e tecnologia",
                "start_date": "2024-12-02",
                "end_date": "2024-12-02",
                "budget_multiplier": 2.5,
                "acos_adjustment": 8.0,
                "peak_hours": [
                    {"start": 9, "end": 11},
                    {"start": 14, "end": 16},
                    {"start": 20, "end": 22}
                ],
                "priority_categories": ["eletronicos", "informatica", "games"],
                "custom_settings": {
                    "digital_focus": True,
                    "mobile_optimization": True
                }
            },
            {
                "name": "Natal",
                "description": "Período natalino - presentes e decoração",
                "start_date": "2024-12-15",
                "end_date": "2024-12-24",
                "budget_multiplier": 2.0,
                "acos_adjustment": 5.0,
                "peak_hours": [
                    {"start": 19, "end": 22}
                ],
                "priority_categories": ["presentes", "decoracao", "brinquedos"],
                "custom_settings": {
                    "gift_keywords": True,
                    "last_minute_shipping": True
                }
            },
            {
                "name": "Dia dos Namorados",
                "description": "Dia dos Namorados - produtos românticos",
                "start_date": "2024-06-10",
                "end_date": "2024-06-12",
                "budget_multiplier": 1.8,
                "acos_adjustment": 5.0,
                "peak_hours": [
                    {"start": 10, "end": 12},
                    {"start": 19, "end": 21}
                ],
                "priority_categories": ["presentes", "joias", "flores", "perfumes"],
                "custom_settings": {
                    "romantic_keywords": True,
                    "express_delivery": True
                }
            },
            {
                "name": "Dia das Mães",
                "description": "Dia das Mães - produtos para mães",
                "start_date": "2024-05-10",
                "end_date": "2024-05-12",
                "budget_multiplier": 2.2,
                "acos_adjustment": 7.0,
                "peak_hours": [
                    {"start": 9, "end": 11},
                    {"start": 15, "end": 17}
                ],
                "priority_categories": ["presentes", "beleza", "casa", "flores"],
                "custom_settings": {
                    "family_keywords": True,
                    "gift_wrapping": True
                }
            },
            {
                "name": "Dia dos Pais",
                "description": "Dia dos Pais - produtos masculinos",
                "start_date": "2024-08-09",
                "end_date": "2024-08-11",
                "budget_multiplier": 1.9,
                "acos_adjustment": 6.0,
                "peak_hours": [
                    {"start": 11, "end": 13},
                    {"start": 18, "end": 20}
                ],
                "priority_categories": ["presentes", "ferramentas", "esportes", "tecnologia"],
                "custom_settings": {
                    "masculine_keywords": True,
                    "practical_gifts": True
                }
            },
            {
                "name": "Dia das Crianças",
                "description": "Dia das Crianças - brinquedos e jogos",
                "start_date": "2024-10-10",
                "end_date": "2024-10-12",
                "budget_multiplier": 2.1,
                "acos_adjustment": 8.0,
                "peak_hours": [
                    {"start": 8, "end": 10},
                    {"start": 16, "end": 18}
                ],
                "priority_categories": ["brinquedos", "jogos", "livros", "roupas_infantis"],
                "custom_settings": {
                    "educational_focus": True,
                    "age_targeting": True
                }
            }
        ]
    }

@router.post("/presets/create-defaults")
async def create_default_special_dates(
    db: Session = Depends(get_db)
):
    """Create default special dates in the database"""
    service = SpecialDatesService(db)
    
    defaults_response = await get_default_special_dates()
    created_dates = []
    
    for date_data in defaults_response["special_dates"]:
        try:
            # Convert string dates to date objects
            date_data["start_date"] = date.fromisoformat(date_data["start_date"])
            date_data["end_date"] = date.fromisoformat(date_data["end_date"])
            
            special_date = SpecialDateCreate(**date_data)
            created_date = service.create_special_date(special_date)
            created_dates.append(created_date)
        except Exception as e:
            # Skip if already exists or has validation error
            continue
    
    return {
        "message": f"Created {len(created_dates)} default special dates",
        "created_dates": created_dates
    }