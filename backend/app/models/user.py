from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    oauth_tokens: List["OAuthToken"] = Relationship(back_populates="user")
