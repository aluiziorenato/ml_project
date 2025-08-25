from sqlalchemy import Column, Integer, String
from app.database import Base

class ApiTest(Base):
    __tablename__ = "api_tests"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    # demais campos
