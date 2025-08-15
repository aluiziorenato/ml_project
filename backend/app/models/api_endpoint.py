from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class ApiEndpoint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    url: str
    default_headers: Optional[str] = None
    auth_type: Optional[str] = "none"
    oauth_scope: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
