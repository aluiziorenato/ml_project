from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import logging
import os
from app.core.config import settings
from app.core.database import create_db_and_tables
from app.api import campaigns, suggestions, dashboard


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Discount Campaign Scheduler service...")
    try:
        create_db_and_tables()
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Discount Campaign Scheduler service...")


# Create FastAPI application
app = FastAPI(
    title="Discount Campaign Scheduler",
    description="""
    **Discount Campaign Scheduler** - Independent module for managing discount campaigns with strategic suggestions and automated scheduling.
    
    ## Features
    
    * **Campaign Management**: Create, update, and manage discount campaigns
    * **Strategic Suggestions**: AI-powered suggestions for high-potential items
    * **Automated Scheduling**: Schedule campaign activation/pause by day/time
    * **Performance Metrics**: Collect and analyze campaign performance data
    * **Predictive Analytics**: Forecast campaign performance based on historical data
    * **Dashboard Analytics**: Comprehensive performance dashboards and trends
    * **OAuth2 Authentication**: Secure access with Mercado Libre authentication
    
    ## Key Capabilities
    
    - Suggest top 5 ads with highest discount campaign potential
    - Schedule automatic campaign activation/pause via ML API
    - Collect metrics: clicks, impressions, conversions, conversion rates
    - Performance prediction with confidence scoring
    - Grafana-ready metrics for dashboards and alerts
    - Historical calendar analysis for optimal timing
    
    **Note**: This module is independent from the ads module and does not suggest prices.
    """,
    version="1.0.0",
    contact={
        "name": "Aluizio Renato",
        "email": "aluizio@example.com"
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(campaigns.router)
app.include_router(suggestions.router)
app.include_router(dashboard.router)

# Include keywords router
from app.api import keywords
app.include_router(keywords.router)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/ui")
async def serve_ui():
    """Serve the web UI"""
    static_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(static_path):
        return FileResponse(static_path)
    else:
        raise HTTPException(status_code=404, detail="UI not found")


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint with service information"""
    return {
        "service": "Discount Campaign Scheduler",
        "version": "1.0.0",
        "status": "active",
        "description": "Strategic discount campaign management with AI suggestions and automated scheduling",
        "features": [
            "Strategic AI-powered item suggestions",
            "Automated campaign scheduling",
            "Performance metrics collection",
            "Predictive analytics",
            "Dashboard analytics",
            "OAuth2 ML authentication"
        ],
        "endpoints": {
            "campaigns": "/api/campaigns",
            "suggestions": "/api/suggestions", 
            "dashboard": "/api/dashboard",
            "docs": "/docs",
            "health": "/health"
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "discount-campaign-scheduler",
        "version": "1.0.0",
        "timestamp": "2024-08-16T14:50:00Z"
    }


@app.get("/api/health", tags=["Health"])
async def api_health():
    """API health check endpoint"""
    try:
        from app.core.database import engine
        # Test database connection
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "service": "discount-campaign-scheduler",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {
        "error": "Not Found",
        "message": "The requested resource was not found",
        "status_code": 404
    }


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return {
        "error": "Internal Server Error",
        "message": "An unexpected error occurred",
        "status_code": 500
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8015,
        reload=True
    )