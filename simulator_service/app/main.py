from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import random
from typing import Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Simulador de Campanhas - Mercado Livre", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

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

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simulator_service"}

@app.post("/api/simulate", response_model=CampaignSimulationResponse)
async def simulate_campaign(request: CampaignSimulationRequest) -> CampaignSimulationResponse:
    """
    Simulate a campaign for Mercado Libre based on input parameters
    """
    logger.info(f"Simulating campaign for product: {request.product_name}")
    
    # Generate campaign ID
    campaign_id = f"CAMP_{random.randint(100000, 999999)}"
    
    # Calculate estimates based on budget and other factors
    base_reach = min(request.budget * 100, 50000)
    estimated_reach = int(base_reach * random.uniform(0.8, 1.2))
    
    # Click rate varies by category and target audience
    click_rate_multiplier = {
        "electronics": 1.2,
        "clothing": 1.0,
        "home": 0.9,
        "books": 0.7,
        "sports": 1.1
    }.get(request.category.lower(), 1.0)
    
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
    
    return CampaignSimulationResponse(
        campaign_id=campaign_id,
        estimated_reach=estimated_reach,
        estimated_clicks=estimated_clicks,
        estimated_conversions=estimated_conversions,
        estimated_revenue=round(estimated_revenue, 2),
        cost_per_click=round(cost_per_click, 2),
        roi_percentage=round(roi_percentage, 2),
        recommendations=recommendations
    )

@app.get("/api/simulation/{campaign_id}")
async def get_simulation_results(campaign_id: str):
    """Get existing simulation results by campaign ID"""
    # In a real implementation, this would fetch from a database
    return {
        "campaign_id": campaign_id,
        "status": "completed",
        "message": "Simulation data would be retrieved from database"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)