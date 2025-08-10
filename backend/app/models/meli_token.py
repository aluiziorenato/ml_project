from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta

class MeliToken(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[str] = Field(default=None, index=True)   # opcional: id do user local
    access_token: str
    refresh_token: str
    token_type: Optional[str] = "bearer"
    expires_at: Optional[datetime] = None  # momento em que o access_token expira
    scope: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
