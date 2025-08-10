from sqlalchemy import Column, Integer, String
from app.database import Base

class ApiEndpoint(Base):
    __tablename__ = "api_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String)
