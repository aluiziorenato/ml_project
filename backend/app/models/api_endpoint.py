from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
    default_headers = Column(String, nullable=True)
    auth_type = Column(String, default="none")
    oauth_scope = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
