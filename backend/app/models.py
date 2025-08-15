from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, nullable=False)
    hashed_password: str
    is_active: bool = True
    is_superuser: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

# demais modelos...

class OAuthSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint_id: int
    state: str
    code_verifier: str
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_type: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ApiTest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    endpoint_id: Optional[int] = None
    name: Optional[str] = None
    request_method: str = "GET"
    request_path: str = "/"
    request_headers: Optional[str] = None
    request_body: Optional[str] = None
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    executed_at: datetime = Field(default_factory=datetime.utcnow)
