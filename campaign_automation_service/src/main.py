"""Main FastAPI application for Campaign Automation Service."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
import uuid

from .api.routes import router
from .utils.config import settings
from .utils.logger import logger, log_request, log_response


# Rate limiter
limiter = Limiter(key_func=get_remote_address)

# FastAPI app
app = FastAPI(
    title="Campaign Automation Service",
    description="""
    # 🚀 Campaign Automation Service
    
    Advanced campaign automation system for Mercado Livre with AI-powered optimization.
    
    ## 🎯 Core Features
    
    * **Campaign Management** - Complete CRUD operations for advertising campaigns
    * **AI-Powered Optimization** - Integration with ML services for copy and bidding optimization
    * **Performance Analytics** - Real-time metrics, trends analysis, and benchmarking
    * **Competitor Intelligence** - Automated competitor monitoring and analysis
    * **A/B Testing** - Automated test creation and statistical analysis
    * **Task Scheduling** - Automated optimization and monitoring tasks
    * **Real-time Metrics** - Live performance tracking and alerts
    
    ## 🤖 AI Integration
    
    * **Copy Optimization** - Automated ad copy enhancement using AI
    * **Performance Prediction** - ML-based campaign performance forecasting
    * **Bidding Optimization** - Smart bid adjustments based on performance data
    * **Keyword Research** - AI-powered keyword discovery and analysis
    
    ## 🔒 Security Features
    
    * JWT Authentication
    * Rate Limiting
    * Input Validation
    * CORS Protection
    * Request/Response Logging
    
    ## 📈 Integration
    
    This service integrates with:
    * Simulator Service (Port 8001) - Campaign simulation
    * Learning Service (Port 8002) - Machine learning insights
    * Optimizer AI (Port 8003) - Copy optimization
    * PostgreSQL - Data persistence
    * Redis - Caching and task queues
    * Celery - Asynchronous task processing
    
    ## 🛠️ Technical Stack
    
    * **Backend**: FastAPI (Python 3.11)
    * **Database**: PostgreSQL with SQLAlchemy
    * **Cache**: Redis
    * **Queue**: Celery
    * **Authentication**: JWT tokens
    * **Containerization**: Docker
    """,
    version=settings.app_version,
    contact={
        "name": "ML Project - Campaign Automation Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Campaigns",
            "description": "Campaign management operations - create, update, activate, pause campaigns"
        },
        {
            "name": "Analytics", 
            "description": "Performance analytics - metrics, trends, benchmarking"
        },
        {
            "name": "AI Optimization",
            "description": "AI-powered optimization - copy, bidding, performance prediction"
        },
        {
            "name": "A/B Testing",
            "description": "A/B test creation and analysis"
        },
        {
            "name": "Competitor Analysis",
            "description": "Competitor monitoring and intelligence gathering"
        },
        {
            "name": "Automation",
            "description": "Task scheduling and automation management"
        },
        {
            "name": "Health",
            "description": "Health checks and service status"
        }
    ]
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production, specify exact hosts
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log all HTTP requests and responses."""
    # Generate request ID
    request_id = str(uuid.uuid4())
    
    # Start timing
    start_time = time.time()
    
    # Log request
    log_request(
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        query_params=str(request.query_params),
        client_ip=request.client.host if request.client else "unknown"
    )
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000
    
    # Log response
    log_response(
        request_id=request_id,
        status_code=response.status_code,
        duration_ms=duration_ms
    )
    
    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id
    
    return response


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    """Add security headers to responses."""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# Include API routes
app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info(
        "Campaign Automation Service starting up",
        version=settings.app_version,
        debug=settings.debug,
        port=settings.api_port
    )
    
    # Initialize database tables (in production)
    # await init_database()
    
    # Start scheduler (in production)
    # from .services.scheduler import scheduler
    # asyncio.create_task(scheduler.start_scheduler())


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Campaign Automation Service shutting down")
    
    # Stop scheduler (in production)
    # from .services.scheduler import scheduler
    # await scheduler.stop_scheduler()


@app.get("/", tags=["Root"])
@limiter.limit("100/minute")
async def root(request: Request):
    """Root endpoint with service information."""
    return {
        "service": "Campaign Automation Service",
        "version": settings.app_version,
        "status": "running",
        "description": "AI-powered campaign automation for Mercado Livre",
        "documentation": "/docs",
        "health": "/health",
        "features": [
            "Campaign Management",
            "AI Optimization", 
            "Performance Analytics",
            "Competitor Monitoring",
            "A/B Testing",
            "Task Automation"
        ],
        "integrations": [
            "Simulator Service (8001)",
            "Learning Service (8002)", 
            "Optimizer AI (8003)",
            "PostgreSQL Database",
            "Redis Cache",
            "Celery Workers"
        ]
    }


@app.get("/health", tags=["Health"])
@limiter.limit("200/minute")
async def health_check(request: Request):
    """Basic health check endpoint."""
    try:
        return {
            "status": "healthy",
            "service": "campaign_automation_service",
            "version": settings.app_version,
            "port": settings.api_port,
            "timestamp": time.time(),
            "uptime": "running"
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        return {
            "status": "unhealthy",
            "service": "campaign_automation_service", 
            "version": settings.app_version,
            "error": str(e),
            "timestamp": time.time()
        }


@app.get("/metrics", tags=["Health"])
@limiter.limit("50/minute")
async def get_service_metrics(request: Request):
    """Get service metrics for monitoring."""
    try:
        # In production, would include real metrics
        return {
            "requests_total": 0,
            "requests_per_minute": 0,
            "active_campaigns": 0,
            "scheduled_tasks": 0,
            "cache_hit_rate": 0.0,
            "average_response_time": 0.0,
            "memory_usage": 0.0,
            "cpu_usage": 0.0,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error("Metrics collection failed", error=str(e))
        return {"error": str(e), "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )