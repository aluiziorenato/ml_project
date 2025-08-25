from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from src.core.config import settings
from src.core.database import engine, Base
from src.api import strategies, special_dates, integrations, reports
from src.services.strategy_coordinator import StrategyCoordinator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Strategic Mode Service...")
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Initialize strategy coordinator
    coordinator = StrategyCoordinator()
    app.state.coordinator = coordinator
    
    logger.info("Strategic Mode Service started successfully!")
    
    yield
    
    # Shutdown
    logger.info("Strategic Mode Service shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Strategic Mode Service",
    description="Sistema de modo estratégico e campanhas para datas especiais",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategies.router, prefix="/api/strategies", tags=["strategies"])
app.include_router(special_dates.router, prefix="/api/special-dates", tags=["special-dates"])
app.include_router(integrations.router, prefix="/api/integrations", tags=["integrations"])
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Strategic Mode Service",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "service": "strategic-mode",
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected",
        "redis": "connected"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )