from pydantic import BaseModel
from typing import Optional

class Promotion(BaseModel):
    id: Optional[int]
    name: str
    type: str
    status: str
    discount: float
    start_date: Optional[str]
    end_date: Optional[str]
