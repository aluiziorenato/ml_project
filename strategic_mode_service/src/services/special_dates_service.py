from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from src.models.database import SpecialDate
from src.models.schemas import SpecialDateCreate, SpecialDateUpdate, SpecialDateResponse

class SpecialDatesService:
    """Service for managing special dates"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_special_dates(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[SpecialDateResponse]:
        """Get all special dates with optional filters"""
        query = self.db.query(SpecialDate)
        
        if is_active is not None:
            query = query.filter(SpecialDate.is_active == is_active)
        
        if start_date:
            query = query.filter(SpecialDate.start_date >= start_date)
        
        if end_date:
            query = query.filter(SpecialDate.end_date <= end_date)
        
        special_dates = query.offset(skip).limit(limit).all()
        return [SpecialDateResponse.from_orm(special_date) for special_date in special_dates]
    
    def get_active_special_dates(self, current_date: Optional[date] = None) -> List[SpecialDateResponse]:
        """Get currently active special dates"""
        if current_date is None:
            current_date = date.today()
        
        special_dates = self.db.query(SpecialDate).filter(
            SpecialDate.is_active == True,
            SpecialDate.start_date <= current_date,
            SpecialDate.end_date >= current_date
        ).all()
        
        return [SpecialDateResponse.from_orm(special_date) for special_date in special_dates]
    
    def get_special_date(self, date_id: int) -> Optional[SpecialDateResponse]:
        """Get a specific special date by ID"""
        special_date = self.db.query(SpecialDate).filter(SpecialDate.id == date_id).first()
        return SpecialDateResponse.from_orm(special_date) if special_date else None
    
    def create_special_date(self, special_date: SpecialDateCreate) -> SpecialDateResponse:
        """Create a new special date"""
        # Check for overlapping dates with same name
        existing = self.db.query(SpecialDate).filter(
            SpecialDate.name == special_date.name,
            SpecialDate.start_date <= special_date.end_date,
            SpecialDate.end_date >= special_date.start_date
        ).first()
        
        if existing:
            raise ValueError(f"Special date '{special_date.name}' already exists for overlapping period")
        
        db_special_date = SpecialDate(**special_date.model_dump())
        self.db.add(db_special_date)
        self.db.commit()
        self.db.refresh(db_special_date)
        
        return SpecialDateResponse.from_orm(db_special_date)
    
    def update_special_date(self, date_id: int, date_update: SpecialDateUpdate) -> Optional[SpecialDateResponse]:
        """Update an existing special date"""
        special_date = self.db.query(SpecialDate).filter(SpecialDate.id == date_id).first()
        if not special_date:
            return None
        
        update_data = date_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(special_date, field, value)
        
        self.db.commit()
        self.db.refresh(special_date)
        
        return SpecialDateResponse.from_orm(special_date)
    
    def delete_special_date(self, date_id: int) -> bool:
        """Delete a special date"""
        special_date = self.db.query(SpecialDate).filter(SpecialDate.id == date_id).first()
        if not special_date:
            return False
        
        self.db.delete(special_date)
        self.db.commit()
        return True
    
    def activate_special_date(self, date_id: int) -> Optional[SpecialDateResponse]:
        """Activate a special date"""
        special_date = self.db.query(SpecialDate).filter(SpecialDate.id == date_id).first()
        if not special_date:
            return None
        
        special_date.is_active = True
        self.db.commit()
        self.db.refresh(special_date)
        
        return SpecialDateResponse.from_orm(special_date)
    
    def deactivate_special_date(self, date_id: int) -> Optional[SpecialDateResponse]:
        """Deactivate a special date"""
        special_date = self.db.query(SpecialDate).filter(SpecialDate.id == date_id).first()
        if not special_date:
            return None
        
        special_date.is_active = False
        self.db.commit()
        self.db.refresh(special_date)
        
        return SpecialDateResponse.from_orm(special_date)