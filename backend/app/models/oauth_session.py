from datetime import datetime
from sqlmodel import SQLModel, Field

class OAuthSession(SQLModel, table=True):
    state: str = Field(primary_key=True, index=True)
    code_verifier: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
