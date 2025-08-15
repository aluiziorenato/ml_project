from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class ApiEndpoint(SQLModel, table=True):
    __tablename__ = "api_endpoints"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    url: Optional[str] = None
    base_url: Optional[str] = None
    auth_type: Optional[str] = None
    oauth_scope: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
