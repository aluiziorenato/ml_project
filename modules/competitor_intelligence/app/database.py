"""Database configuration for competitor intelligence module."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from .models import Base

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+psycopg2://postgres:postgres@db:5432/ml_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database():
    """Get database session."""
    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as e:
        print(f"Database error: {e}")
        # Return None for endpoints that can work without database
        yield None

def create_tables():
    """Create database tables."""
    Base.metadata.create_all(bind=engine)

def get_db_session() -> Session:
    """Get a new database session."""
    return SessionLocal()