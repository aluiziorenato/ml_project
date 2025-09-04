from pydantic import BaseModel
from typing import Optional

class Campaign(BaseModel):
    id: Optional[int]
    name: str
    type: str
    status: str
    budget: float
    spent: float
    clicks: int
    conversions: int
    start_date: Optional[str]
    end_date: Optional[str]
