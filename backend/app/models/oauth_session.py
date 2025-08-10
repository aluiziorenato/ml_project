from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class OAuthSession(Base):
    __tablename__ = "oauth_sessions"
    id = Column(Integer, primary_key=True, index=True)
    # ... demais campos
