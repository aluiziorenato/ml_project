"""
Shared utilities for SEO Intelligence modules
Provides common functionality for all SEO services
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import logging
import asyncio
import aioredis
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Common models
class SEOMetrics(BaseModel):
    """Standard SEO metrics across all modules"""
    keyword: str
    search_volume: int
    competition_score: float
    difficulty_score: float
    opportunity_score: float
    trend_direction: str  # 'up', 'down', 'stable'

class MarketData(BaseModel):
    """Market data structure for SEO analysis"""
    keyword: str
    category: str
    platform: str  # 'mercadolibre', 'amazon', 'shopee'
    search_volume: int
    avg_cpc: float
    competition_level: str
    seasonal_trends: List[Dict[str, Any]]
    timestamp: datetime

class SEOAlert(BaseModel):
    """Alert structure for opportunities"""
    alert_id: str
    alert_type: str
    priority: str  # 'high', 'medium', 'low'
    title: str
    description: str
    recommended_action: str
    confidence_score: float
    expires_at: Optional[datetime]
    created_at: datetime

# Database utilities
class DatabaseManager:
    """Shared database manager for all SEO modules"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

# Redis utilities
class CacheManager:
    """Shared cache manager for all SEO modules"""
    
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis_client = await aioredis.from_url(self.redis_url)
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis_client:
            await self.connect()
        return await self.redis_client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache with expiration"""
        if not self.redis_client:
            await self.connect()
        await self.redis_client.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            await self.connect()
        await self.redis_client.delete(key)

# HTTP client utilities
class APIClient:
    """Shared HTTP client for external API calls"""
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
    
    async def get(self, url: str, headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make GET request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=headers or {})
            response.raise_for_status()
            return response.json()
    
    async def post(self, url: str, data: Dict[str, Any], headers: Dict[str, str] = None) -> Dict[str, Any]:
        """Make POST request"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(url, json=data, headers=headers or {})
            response.raise_for_status()
            return response.json()

# SEO analysis utilities
class SEOAnalyzer:
    """Common SEO analysis functions"""
    
    @staticmethod
    def calculate_opportunity_score(search_volume: int, competition: float, difficulty: float) -> float:
        """Calculate opportunity score for a keyword"""
        # Higher search volume = better opportunity
        # Lower competition = better opportunity  
        # Lower difficulty = better opportunity
        volume_factor = min(search_volume / 10000, 1.0)  # Normalize to 0-1
        competition_factor = 1.0 - competition  # Invert competition (lower is better)
        difficulty_factor = 1.0 - difficulty    # Invert difficulty (lower is better)
        
        opportunity_score = (volume_factor * 0.4 + competition_factor * 0.3 + difficulty_factor * 0.3)
        return round(opportunity_score, 3)
    
    @staticmethod
    def detect_trend_direction(data_points: List[float]) -> str:
        """Detect trend direction from data points"""
        if len(data_points) < 2:
            return 'stable'
        
        # Calculate average change
        changes = [data_points[i] - data_points[i-1] for i in range(1, len(data_points))]
        avg_change = sum(changes) / len(changes)
        
        if avg_change > 0.05:  # 5% threshold
            return 'up'
        elif avg_change < -0.05:
            return 'down'
        else:
            return 'stable'
    
    @staticmethod
    def calculate_blue_ocean_score(competitors_count: int, market_size: int) -> float:
        """Calculate Blue Ocean opportunity score"""
        if market_size == 0:
            return 0.0
        
        # Lower competitors with higher market size = higher blue ocean score
        competition_density = competitors_count / market_size
        blue_ocean_score = max(0.0, 1.0 - competition_density)
        
        return round(blue_ocean_score, 3)

# Configuration utilities
def get_config():
    """Get common configuration for all SEO modules"""
    return {
        'database_url': os.getenv('DATABASE_URL', 'postgresql+psycopg2://postgres:postgres@db:5432/ml_db'),
        'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
        'ml_api_url': os.getenv('ML_API_URL', 'https://api.mercadolibre.com'),
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',
        'log_level': os.getenv('LOG_LEVEL', 'INFO'),
    }

# Shared FastAPI dependencies
def get_database():
    """FastAPI dependency for database session"""
    config = get_config()
    db_manager = DatabaseManager(config['database_url'])
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

def get_cache():
    """FastAPI dependency for cache manager"""
    config = get_config()
    return CacheManager(config['redis_url'])

def get_api_client():
    """FastAPI dependency for API client"""
    return APIClient()