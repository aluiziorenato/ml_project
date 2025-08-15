import sys
import os
# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import uuid

# Import shared modules
from auth import add_auth_routes, require_scope, get_current_active_user, User
from metrics import (
    add_metrics_endpoint, setup_metrics_middleware, update_simulator_metrics,
    track_campaign_simulation
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simulador de Campanhas - Mercado Livre", 
    version="1.0.0",
    description="API para simulação e gerenciamento de campanhas publicitárias no Mercado Livre",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files if directory exists
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# In-memory storage for demo purposes (in production, use a database)
campaigns_storage = {}

# Setup authentication and metrics
add_auth_routes(app)
add_metrics_endpoint(app)
setup_metrics_middleware(app, "simulator_service")

class CampaignSimulationRequest(BaseModel):
    product_name: str
    category: str
    budget: float
    duration_days: int
    target_audience: str
    keywords: list[str]

class CampaignSimulationResponse(BaseModel):
    campaign_id: str
    estimated_reach: int
    estimated_clicks: int
    estimated_conversions: int
    estimated_revenue: float
    cost_per_click: float
    roi_percentage: float
    recommendations: list[str]
    created_at: str
    status: str = "active"

class CampaignUpdateRequest(BaseModel):
    product_name: Optional[str] = None
    category: Optional[str] = None
    budget: Optional[float] = None
    duration_days: Optional[int] = None
    target_audience: Optional[str] = None
    keywords: Optional[list[str]] = None
    status: Optional[str] = None

class CampaignListResponse(BaseModel):
    campaigns: List[CampaignSimulationResponse]
    total: int
    page: int
    per_page: int

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Simulator Service</h1><p>API available at /docs</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simulator_service"}

@app.post("/api/simulate", response_model=CampaignSimulationResponse)
async def simulate_campaign(
    request: CampaignSimulationRequest,
    current_user: User = Depends(require_scope("write"))
) -> CampaignSimulationResponse:
    """
    Simulate a campaign for Mercado Libre based on input parameters
    """
    logger.info(f"Creating simulation for product: {request.product_name} by user: {current_user.username}")
    
    # Track metrics
    track_campaign_simulation(request.product_category, request.target_audience)
    
    # Generate unique campaign ID
    campaign_id = f"CAM_{str(uuid.uuid4())[:8].upper()}"
    
    # Simulate campaign metrics based on input parameters
    base_reach = request.budget * 10  # Basic reach estimation
    
    # Category multipliers
    category_multipliers = {
        "electronics": 1.5,
        "clothing": 1.2,
        "home": 1.0,
        "sports": 1.3,
        "books": 0.8,
        "automotive": 1.4
    }
    
    category_multiplier = category_multipliers.get(request.category.lower(), 1.0)
    
    # Target audience multipliers
    audience_multipliers = {
        "young_adults": 1.3,
        "families": 1.1,
        "professionals": 1.4,
        "seniors": 0.9
    }
    
    audience_multiplier = audience_multipliers.get(request.target_audience.lower(), 1.0)
    
    # Keyword optimization factor
    keyword_factor = min(1.5, 1 + (len(request.keywords) * 0.1))
    
    # Duration factor (longer campaigns get better rates)
    duration_factor = min(1.3, 1 + (request.duration_days / 30) * 0.3)
    
    # Calculate final estimates
    estimated_reach = int(base_reach * category_multiplier * audience_multiplier * keyword_factor * duration_factor)
    
    # Click rate varies by category and audience
    click_rate_multiplier = category_multiplier * audience_multiplier
    estimated_clicks = int(estimated_reach * 0.05 * click_rate_multiplier)
    estimated_conversions = int(estimated_clicks * 0.03)
    
    # Calculate revenue estimates
    avg_order_value = request.budget / max(1, estimated_conversions) * random.uniform(2, 4)
    estimated_revenue = estimated_conversions * avg_order_value
    
    cost_per_click = request.budget / max(1, estimated_clicks)
    roi_percentage = ((estimated_revenue - request.budget) / request.budget) * 100
    
    # Generate recommendations
    recommendations = []
    if roi_percentage < 50:
        recommendations.append("Consider adjusting keywords for better targeting")
    if cost_per_click > 2.0:
        recommendations.append("Budget allocation could be optimized for lower CPC")
    if len(request.keywords) < 5:
        recommendations.append("Adding more relevant keywords could improve reach")
    if request.duration_days < 7:
        recommendations.append("Consider extending campaign duration for better performance")
    
    recommendations.append(f"Target audience '{request.target_audience}' shows good potential for {request.category}")
    
    # Create campaign response
    campaign_response = CampaignSimulationResponse(
        campaign_id=campaign_id,
        estimated_reach=estimated_reach,
        estimated_clicks=estimated_clicks,
        estimated_conversions=estimated_conversions,
        estimated_revenue=round(estimated_revenue, 2),
        cost_per_click=round(cost_per_click, 2),
        roi_percentage=round(roi_percentage, 2),
        recommendations=recommendations,
        created_at=datetime.now().isoformat(),
        status="active"
    )
    
    # Store the campaign (including the original request data)
    campaigns_storage[campaign_id] = {
        "response": campaign_response,
        "request": request,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "created_by": current_user.username
    }
    
    # Update metrics
    update_simulator_metrics(campaigns_storage)
    
    return campaign_response

@app.get("/api/campaigns", response_model=CampaignListResponse)
async def list_campaigns(
    page: int = 1, 
    per_page: int = 10, 
    status: Optional[str] = None,
    current_user: User = Depends(require_scope("read"))
):
    """List all campaigns with pagination and optional status filter"""
    campaigns = list(campaigns_storage.values())
    
    # Filter by status if provided
    if status:
        campaigns = [c for c in campaigns if c["response"].status == status]
    
    total = len(campaigns)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_campaigns = campaigns[start_idx:end_idx]
    
    return CampaignListResponse(
        campaigns=[c["response"] for c in paginated_campaigns],
        total=total,
        page=page,
        per_page=per_page
    )

@app.get("/api/simulation/{campaign_id}", response_model=CampaignSimulationResponse)
async def get_simulation_results(
    campaign_id: str,
    current_user: User = Depends(require_scope("read"))
):
    """Get existing simulation results by campaign ID"""
    if campaign_id not in campaigns_storage:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaigns_storage[campaign_id]["response"]

@app.put("/api/simulation/{campaign_id}", response_model=CampaignSimulationResponse)
async def update_campaign(
    campaign_id: str, 
    update_request: CampaignUpdateRequest,
    current_user: User = Depends(require_scope("write"))
):
    """Update an existing campaign"""
    if campaign_id not in campaigns_storage:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign_data = campaigns_storage[campaign_id]
    original_request = campaign_data["request"]
    
    # Update only provided fields
    updated_fields = update_request.dict(exclude_unset=True)
    
    # Update the original request with new values
    for field, value in updated_fields.items():
        if field != "status" and hasattr(original_request, field):
            setattr(original_request, field, value)
    
    # If budget or other simulation parameters changed, re-simulate
    simulation_fields = ["budget", "duration_days", "keywords", "category", "target_audience"]
    if any(field in updated_fields for field in simulation_fields):
        # Re-run simulation with updated parameters
        new_simulation = await simulate_campaign(original_request)
        # Keep the original campaign_id
        new_simulation.campaign_id = campaign_id
        campaigns_storage[campaign_id]["response"] = new_simulation
    
    # Update status if provided
    if "status" in updated_fields:
        campaigns_storage[campaign_id]["response"].status = updated_fields["status"]
    
    campaigns_storage[campaign_id]["updated_at"] = datetime.now().isoformat()
    
    # Update metrics
    update_simulator_metrics(campaigns_storage)
    
    return campaigns_storage[campaign_id]["response"]

@app.delete("/api/simulation/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: User = Depends(require_scope("write"))
):
    """Delete a campaign"""
    if campaign_id not in campaigns_storage:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    del campaigns_storage[campaign_id]
    
    # Update metrics
    update_simulator_metrics(campaigns_storage)
    
    return {"message": f"Campaign {campaign_id} deleted successfully"}

@app.get("/api/campaigns/stats")
async def get_campaigns_stats(current_user: User = Depends(require_scope("read"))):
    """Get aggregate statistics for all campaigns"""
    if not campaigns_storage:
        return {
            "total_campaigns": 0,
            "active_campaigns": 0,
            "total_budget": 0,
            "avg_roi": 0,
            "avg_cpc": 0
        }
    
    campaigns = [c["response"] for c in campaigns_storage.values()]
    active_campaigns = [c for c in campaigns if c.status == "active"]
    
    total_budget = sum(campaigns_storage[c.campaign_id]["request"].budget for c in campaigns)
    avg_roi = sum(c.roi_percentage for c in campaigns) / len(campaigns)
    avg_cpc = sum(c.cost_per_click for c in campaigns) / len(campaigns)
    
    return {
        "total_campaigns": len(campaigns),
        "active_campaigns": len(active_campaigns),
        "total_budget": round(total_budget, 2),
        "avg_roi": round(avg_roi, 2),
        "avg_cpc": round(avg_cpc, 2)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)