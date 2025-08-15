from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class ApiEndpointCreate(BaseModel):
    name: str
    base_url: str
    default_headers: Optional[str] = None
    auth_type: Optional[str] = "none"
    oauth_scope: Optional[str] = None

class ApiEndpointRead(ApiEndpointCreate):
    id: int
    created_at: datetime

class OAuthStartResponse(BaseModel):
    authorization_url: str
    oauth_session_id: int

class OAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str]
    expires_in: Optional[int]

class ApiTestCreate(BaseModel):
    endpoint_id: int
    name: Optional[str]
    request_method: str = "GET"
    request_path: str = "/"
    request_headers: Optional[str] = None
    request_body: Optional[str] = None

class ApiTestRead(ApiTestCreate):
    id: int
    status_code: Optional[int]
    response_body: Optional[str]
    executed_at: datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
