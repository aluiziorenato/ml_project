from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime

class OAuthToken(SQLModel, table=True):
    __tablename__ = "oauth_tokens"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    access_token: str
    refresh_token: Optional[str]
    expires_in: Optional[int]
    scope: Optional[str]
    token_type: Optional[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # relacionamento com User
    user: "User" = Relationship(back_populates="oauth_tokens")
