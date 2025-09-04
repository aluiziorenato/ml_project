from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class CampaignBase(BaseModel):
    name: str
    status: str
    performance: Optional[str] = None
    budget: float
    acos: Optional[float] = None
    strategy: Optional[str] = None
    channel: Optional[str] = None
    currency_id: Optional[str] = None
    items: Optional[List[str]] = None

class CampaignCreate(CampaignBase):
    pass

class CampaignRead(CampaignBase):
    id: int
    created_at: datetime

class PromotionBase(BaseModel):
    discount: str
    status: str
    produtos: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    price: Optional[float] = None
    discount_percentage: Optional[float] = None

class PromotionCreate(PromotionBase):
    pass

class PromotionRead(PromotionBase):
    id: int
    created_at: datetime

class ProductBase(BaseModel):
    id: str
    title: str
    price: float
    image: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    status: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductRead(ProductBase):
    pass
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
