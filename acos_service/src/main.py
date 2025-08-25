"""Main FastAPI application for ACOS Service."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import time
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from .api.routes import router
from .utils.logger import logger
from .utils.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="ACOS (Advertising Cost of Sales) Service",
    description="""
    🎯 **ACOS Service** - Marketplace Campaign Optimization
    
    Intelligent ACOS monitoring and automation for marketplace advertising campaigns.
    
    ## Key Features
    
    * **Real-time ACOS Monitoring** - Track advertising cost of sales across campaigns
    * **Automated Campaign Actions** - Pause, adjust bids/budgets based on ACOS thresholds  
    * **Smart Alerts** - Configurable alerts for ACOS performance issues
    * **AI-Powered Recommendations** - Optimization suggestions from ML models
    * **Rule-Based Automation** - Create custom automation rules with flexible conditions
    * **Detailed Analytics** - Comprehensive ACOS analysis and trend tracking
    
    ## ACOS Calculation
    
    ACOS = (Ad Spend / Ad Revenue) × 100
    
    * Lower ACOS = Better efficiency (spending less to generate revenue)
    * Higher ACOS = Lower efficiency (spending more for the same revenue)
    
    ## Automation Actions
    
    * **Pause Campaigns** - Automatically pause underperforming campaigns
    * **Adjust Bids** - Reduce/increase bid amounts based on performance
    * **Optimize Budgets** - Reallocate budget across campaigns
    * **Keyword Optimization** - AI-powered keyword recommendations
    * **Smart Alerts** - Real-time notifications for threshold breaches
    """,
    version="1.0.0",
    contact={
        "name": "ML Project - ACOS Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "ACOS Rules",
            "description": "Create and manage ACOS automation rules"
        },
        {
            "name": "ACOS Metrics",
            "description": "Campaign ACOS metrics and performance tracking"
        },
        {
            "name": "ACOS Analysis",
            "description": "Detailed ACOS analysis and optimization insights"
        },
        {
            "name": "ACOS Alerts",
            "description": "ACOS alert management and resolution"
        },
        {
            "name": "ACOS Automation",
            "description": "Automation engine control and monitoring"
        },
        {
            "name": "Health",
            "description": "Service health checks and monitoring"
        }
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include API routes
app.include_router(router)

# Root endpoint with service info
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    """ACOS Service information page."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACOS Service - Marketplace Campaign Optimization</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            .header { color: #2c5aa0; border-bottom: 2px solid #2c5aa0; padding-bottom: 20px; }
            .metrics { display: flex; gap: 20px; margin: 20px 0; }
            .metric-card { background: #f5f5f5; padding: 15px; border-radius: 8px; flex: 1; }
            .metric-value { font-size: 24px; font-weight: bold; color: #2c5aa0; }
            .endpoints { background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .endpoint { margin: 10px 0; padding: 8px; background: white; border-radius: 4px; }
            .method { font-weight: bold; color: #007acc; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 ACOS Service</h1>
            <p>Advertising Cost of Sales Monitoring & Automation</p>
        </div>
        
        <div class="metrics">
            <div class="metric-card">
                <div>Service Port</div>
                <div class="metric-value">8016</div>
            </div>
            <div class="metric-card">
                <div>Status</div>
                <div class="metric-value">Active</div>
            </div>
            <div class="metric-card">
                <div>Version</div>
                <div class="metric-value">1.0.0</div>
            </div>
        </div>
        
        <h2>📊 Key Features</h2>
        <ul>
            <li><strong>ACOS Monitoring</strong> - Real-time tracking of advertising efficiency</li>
            <li><strong>Automated Actions</strong> - Smart campaign optimization based on thresholds</li>
            <li><strong>AI Integration</strong> - ML-powered recommendations and insights</li>
            <li><strong>Alert System</strong> - Configurable alerts for performance issues</li>
            <li><strong>Rule Engine</strong> - Flexible automation rules with custom conditions</li>
        </ul>
        
        <h2>🔧 API Endpoints</h2>
        <div class="endpoints">
            <div class="endpoint">
                <span class="method">GET</span> /docs - Interactive API Documentation
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/acos/rules - List automation rules
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/acos/rules - Create automation rule
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/acos/campaigns/{id}/metrics - Get ACOS metrics
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/acos/campaigns/{id}/analysis - Detailed ACOS analysis
            </div>
            <div class="endpoint">
                <span class="method">GET</span> /api/acos/alerts - List ACOS alerts
            </div>
            <div class="endpoint">
                <span class="method">POST</span> /api/acos/automation/evaluate - Trigger rule evaluation
            </div>
        </div>
        
        <h2>📈 ACOS Formula</h2>
        <p><strong>ACOS = (Ad Spend ÷ Ad Revenue) × 100</strong></p>
        <p>Lower ACOS indicates better advertising efficiency.</p>
        
        <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p>ACOS Service - Part of ML Project Marketplace Automation Suite</p>
        </footer>
    </body>
    </html>
    """

# Startup event
@app.on_event("startup")
async def startup_event():
    """Application startup."""
    logger.info("🎯 ACOS Service starting up...")
    logger.info(f"Service running on port {settings.port}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown."""
    logger.info("🎯 ACOS Service shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8016)