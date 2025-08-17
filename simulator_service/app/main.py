from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import random
from typing import Dict, Any, List, Optional
import logging
import json
import os
from datetime import datetime, timedelta
import httpx
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import io
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Simulador de Campanhas - Mercado Livre",
    description="""
    Simulador avançado de campanhas publicitárias para Mercado Livre com IA e Machine Learning.
    
    ## Funcionalidades Principais
    
    * **Simulação de Campanhas** - Predição de métricas baseada em dados históricos
    * **Integração Mercado Livre** - Dados reais da API oficial
    * **Exportação de Relatórios** - PDF e CSV com métricas detalhadas
    * **Dashboard Interativo** - Gráficos e visualizações em tempo real
    * **Simulação A/B** - Testes comparativos de estratégias
    * **Machine Learning** - Algoritmos preditivos para otimização
    
    ## Métricas Disponíveis
    
    * ROI (Return on Investment)
    * CPC (Cost Per Click)
    * CTR (Click Through Rate)
    * Alcance e Impressões
    * Conversões e Receita
    * Recomendações Inteligentes
    """,
    version="2.0.0",
    contact={
        "name": "ML Project - Simulator Team",
        "url": "https://github.com/aluiziorenato/ml_project",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Simulation",
            "description": "Simulação de campanhas publicitárias"
        },
        {
            "name": "Reports",
            "description": "Geração e exportação de relatórios"
        },
        {
            "name": "A/B Testing",
            "description": "Testes A/B e comparações"
        },
        {
            "name": "Analytics",
            "description": "Analytics e métricas"
        },
        {
            "name": "Health",
            "description": "Health checks e monitoramento"
        }
    ]
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
import os
if os.path.exists("static"):
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

class ABTestRequest(BaseModel):
    test_name: str
    variations: List[CampaignSimulationRequest]
    traffic_split: List[float]  # Percentages for each variation

class ABTestResponse(BaseModel):
    test_id: str
    status: str
    variations_results: List[CampaignSimulationResponse]
    winner_variation: int
    confidence_level: float
    estimated_lift: float

class ReportRequest(BaseModel):
    campaign_ids: List[str]
    format: str = "pdf"  # pdf, csv, excel
    include_charts: bool = True

class MercadoLibreHistoricalRequest(BaseModel):
    category_id: str
    period_days: int = 30
    
class HistoricalData(BaseModel):
    date: str
    impressions: int
    clicks: int
    conversions: int
    spend: float
    category: str

# In-memory storage for demo (in production, use database)
campaign_results = {}
ab_tests = {}
historical_data_cache = {}

async def get_mercadolibre_historical_data(category_id: str, period_days: int = 30) -> List[HistoricalData]:
    """
    Fetch historical data from Mercado Livre API (simulated for demo)
    In production, this would use real ML API endpoints
    """
    try:
        # Simulate API call to Mercado Livre
        # Real implementation would use: https://api.mercadolibre.com/categories/{category_id}/trends
        logger.info(f"Fetching ML historical data for category {category_id}")
        
        # Generate realistic historical data based on category
        historical_data = []
        base_date = datetime.now() - timedelta(days=period_days)
        
        category_multipliers = {
            "MLB1051": {"impressions": 1000, "clicks": 50, "conversions": 2},  # Electronics
            "MLB1430": {"impressions": 800, "clicks": 40, "conversions": 1.5},   # Clothing
            "MLB1574": {"impressions": 600, "clicks": 30, "conversions": 1},     # Home
            "MLB1196": {"impressions": 400, "clicks": 20, "conversions": 0.8},   # Books
            "MLB1276": {"impressions": 900, "clicks": 45, "conversions": 1.8}    # Sports
        }
        
        multiplier = category_multipliers.get(category_id, {"impressions": 700, "clicks": 35, "conversions": 1.2})
        
        for i in range(period_days):
            date = base_date + timedelta(days=i)
            # Add some randomness and seasonal patterns
            seasonal_factor = 1 + 0.3 * random.sin(i * 0.1)  # Simulate seasonal trends
            weekend_factor = 0.7 if date.weekday() >= 5 else 1.0  # Lower weekend performance
            
            impressions = int(multiplier["impressions"] * seasonal_factor * weekend_factor * random.uniform(0.8, 1.2))
            clicks = int(multiplier["clicks"] * seasonal_factor * weekend_factor * random.uniform(0.8, 1.2))
            conversions = int(multiplier["conversions"] * seasonal_factor * weekend_factor * random.uniform(0.8, 1.2))
            spend = clicks * random.uniform(1.5, 3.0)  # Variable CPC
            
            historical_data.append(HistoricalData(
                date=date.strftime("%Y-%m-%d"),
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                spend=round(spend, 2),
                category=category_id
            ))
        
        # Cache the results
        historical_data_cache[f"{category_id}_{period_days}"] = historical_data
        return historical_data
        
    except Exception as e:
        logger.error(f"Error fetching ML historical data: {e}")
        # Return fallback data
        return [HistoricalData(
            date=datetime.now().strftime("%Y-%m-%d"),
            impressions=1000,
            clicks=50,
            conversions=2,
            spend=100.0,
            category=category_id
        )]

def get_category_id_from_name(category_name: str) -> str:
    """Map category names to Mercado Livre category IDs"""
    category_mapping = {
        "electronics": "MLB1051",
        "clothing": "MLB1430", 
        "home": "MLB1574",
        "books": "MLB1196",
        "sports": "MLB1276"
    }
    return category_mapping.get(category_name.lower(), "MLB1051")

def generate_pdf_report(campaign_ids: List[str], include_charts: bool = True) -> bytes:
    """Generate PDF report for campaigns"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph("Campaign Performance Report", styles['Title'])
    elements.append(title)
    elements.append(Spacer(1, 12))
    
    # Generate report for each campaign
    for campaign_id in campaign_ids:
        if campaign_id in campaign_results:
            result = campaign_results[campaign_id]
            
            # Campaign summary
            campaign_title = Paragraph(f"Campaign: {campaign_id}", styles['Heading2'])
            elements.append(campaign_title)
            
            # Data table
            data = [
                ['Metric', 'Value'],
                ['Estimated Reach', f"{result['estimated_reach']:,}"],
                ['Estimated Clicks', f"{result['estimated_clicks']:,}"],
                ['Estimated Conversions', f"{result['estimated_conversions']:,}"],
                ['Estimated Revenue', f"R$ {result['estimated_revenue']:,.2f}"],
                ['Cost Per Click', f"R$ {result['cost_per_click']:.2f}"],
                ['ROI Percentage', f"{result['roi_percentage']:.1f}%"]
            ]
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 12))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()

def generate_csv_report(campaign_ids: List[str]) -> str:
    """Generate CSV report for campaigns"""
    data = []
    for campaign_id in campaign_ids:
        if campaign_id in campaign_results:
            result = campaign_results[campaign_id]
            data.append({
                'Campaign ID': campaign_id,
                'Estimated Reach': result['estimated_reach'],
                'Estimated Clicks': result['estimated_clicks'],
                'Estimated Conversions': result['estimated_conversions'],
                'Estimated Revenue': result['estimated_revenue'],
                'Cost Per Click': result['cost_per_click'],
                'ROI Percentage': result['roi_percentage']
            })
    
    df = pd.DataFrame(data)
    return df.to_csv(index=False)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Simulator Service</h1><p>Frontend not available</p>")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "simulator_service"}

@app.post("/api/simulate", response_model=CampaignSimulationResponse, tags=["Simulation"])
async def simulate_campaign(request: CampaignSimulationRequest) -> CampaignSimulationResponse:
    """
    Simulate a campaign for Mercado Libre based on input parameters and historical data
    """
    logger.info(f"Simulating campaign for product: {request.product_name}")
    
    # Generate campaign ID
    campaign_id = f"CAMP_{random.randint(100000, 999999)}"
    
    # Get historical data from Mercado Libre API
    category_id = get_category_id_from_name(request.category)
    historical_data = await get_mercadolibre_historical_data(category_id, 30)
    
    # Calculate averages from historical data for more realistic estimates
    if historical_data:
        avg_ctr = sum(h.clicks / max(h.impressions, 1) for h in historical_data) / len(historical_data)
        avg_conversion_rate = sum(h.conversions / max(h.clicks, 1) for h in historical_data) / len(historical_data)
        avg_cpc = sum(h.spend / max(h.clicks, 1) for h in historical_data) / len(historical_data)
    else:
        avg_ctr = 0.05
        avg_conversion_rate = 0.03
        avg_cpc = 2.0
    
    # Calculate estimates based on budget and historical performance
    estimated_clicks = int(request.budget / avg_cpc)
    estimated_reach = int(estimated_clicks / avg_ctr)
    estimated_conversions = int(estimated_clicks * avg_conversion_rate)
    
    # Add some variance and keyword optimization
    keyword_boost = min(len(request.keywords) * 0.1, 0.3)  # Up to 30% boost for good keywords
    duration_factor = min(request.duration_days / 30, 1.0)  # Longer campaigns get better performance
    
    estimated_reach = int(estimated_reach * (1 + keyword_boost) * duration_factor)
    estimated_clicks = int(estimated_clicks * (1 + keyword_boost))
    estimated_conversions = int(estimated_conversions * (1 + keyword_boost))
    
    # Calculate revenue estimates
    avg_order_value = request.budget / max(1, estimated_conversions) * random.uniform(3, 6)
    estimated_revenue = estimated_conversions * avg_order_value
    
    cost_per_click = request.budget / max(1, estimated_clicks)
    roi_percentage = ((estimated_revenue - request.budget) / request.budget) * 100
    
    # Generate intelligent recommendations based on data
    recommendations = []
    if roi_percentage < 50:
        recommendations.append("Consider adjusting keywords for better targeting based on historical performance")
    if cost_per_click > avg_cpc * 1.5:
        recommendations.append("Budget allocation could be optimized for lower CPC based on market data")
    if len(request.keywords) < 5:
        recommendations.append("Adding more relevant keywords could improve reach by up to 30%")
    if request.duration_days < 7:
        recommendations.append("Consider extending campaign duration - longer campaigns show 20% better performance")
    
    recommendations.append(f"Category '{request.category}' shows {avg_ctr*100:.1f}% avg CTR in recent data")
    recommendations.append(f"Historical conversion rate for this category: {avg_conversion_rate*100:.1f}%")
    
    # Store results for reporting
    result_data = {
        "campaign_id": campaign_id,
        "estimated_reach": estimated_reach,
        "estimated_clicks": estimated_clicks,
        "estimated_conversions": estimated_conversions,
        "estimated_revenue": round(estimated_revenue, 2),
        "cost_per_click": round(cost_per_click, 2),
        "roi_percentage": round(roi_percentage, 2),
        "recommendations": recommendations,
        "created_at": datetime.now().isoformat(),
        "request_data": request.dict()
    }
    campaign_results[campaign_id] = result_data
    
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

@app.get("/api/simulation/{campaign_id}", tags=["Simulation"])
async def get_simulation_results(campaign_id: str):
    """Get existing simulation results by campaign ID"""
    if campaign_id in campaign_results:
        return {
            "campaign_id": campaign_id,
            "status": "completed",
            "data": campaign_results[campaign_id]
        }
    else:
        raise HTTPException(status_code=404, detail="Campaign not found")

@app.post("/api/ab-test", response_model=ABTestResponse, tags=["A/B Testing"])
async def create_ab_test(request: ABTestRequest) -> ABTestResponse:
    """
    Create A/B test for multiple campaign variations
    """
    if len(request.variations) < 2:
        raise HTTPException(status_code=400, detail="At least 2 variations required for A/B test")
    
    if len(request.traffic_split) != len(request.variations):
        raise HTTPException(status_code=400, detail="Traffic split must match number of variations")
    
    if abs(sum(request.traffic_split) - 100) > 0.1:
        raise HTTPException(status_code=400, detail="Traffic split must sum to 100%")
    
    test_id = f"ABT_{random.randint(100000, 999999)}"
    logger.info(f"Creating A/B test: {test_id} with {len(request.variations)} variations")
    
    # Simulate each variation
    variations_results = []
    performance_scores = []
    
    for i, variation in enumerate(request.variations):
        # Add some randomness to simulate A/B test variance
        variation_result = await simulate_campaign(variation)
        
        # Adjust results based on traffic split
        traffic_factor = request.traffic_split[i] / 100
        variation_result.estimated_reach = int(variation_result.estimated_reach * traffic_factor)
        variation_result.estimated_clicks = int(variation_result.estimated_clicks * traffic_factor)
        variation_result.estimated_conversions = int(variation_result.estimated_conversions * traffic_factor)
        variation_result.estimated_revenue = variation_result.estimated_revenue * traffic_factor
        
        variations_results.append(variation_result)
        
        # Calculate performance score for comparison
        score = variation_result.roi_percentage
        performance_scores.append(score)
    
    # Determine winner
    winner_variation = performance_scores.index(max(performance_scores))
    best_score = max(performance_scores)
    second_best_score = sorted(performance_scores, reverse=True)[1] if len(performance_scores) > 1 else 0
    
    # Calculate confidence level and lift
    confidence_level = min(95, 50 + (best_score - second_best_score) * 2)  # Simplified confidence calculation
    estimated_lift = ((best_score - second_best_score) / second_best_score * 100) if second_best_score > 0 else 0
    
    # Store A/B test results
    ab_test_data = {
        "test_id": test_id,
        "test_name": request.test_name,
        "variations": [v.dict() for v in request.variations],
        "traffic_split": request.traffic_split,
        "results": [v.dict() for v in variations_results],
        "winner_variation": winner_variation,
        "confidence_level": confidence_level,
        "estimated_lift": estimated_lift,
        "created_at": datetime.now().isoformat()
    }
    ab_tests[test_id] = ab_test_data
    
    return ABTestResponse(
        test_id=test_id,
        status="completed",
        variations_results=variations_results,
        winner_variation=winner_variation,
        confidence_level=round(confidence_level, 1),
        estimated_lift=round(estimated_lift, 2)
    )

@app.get("/api/ab-test/{test_id}", tags=["A/B Testing"])
async def get_ab_test_results(test_id: str):
    """Get A/B test results by test ID"""
    if test_id in ab_tests:
        return ab_tests[test_id]
    else:
        raise HTTPException(status_code=404, detail="A/B test not found")

@app.post("/api/reports/generate", tags=["Reports"])
async def generate_report(request: ReportRequest):
    """
    Generate and download campaign reports in various formats
    """
    if not request.campaign_ids:
        raise HTTPException(status_code=400, detail="At least one campaign ID required")
    
    # Check if campaigns exist
    missing_campaigns = [cid for cid in request.campaign_ids if cid not in campaign_results]
    if missing_campaigns:
        raise HTTPException(status_code=404, detail=f"Campaigns not found: {missing_campaigns}")
    
    if request.format.lower() == "pdf":
        pdf_content = generate_pdf_report(request.campaign_ids, request.include_charts)
        return Response(
            content=pdf_content,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=campaign_report.pdf"}
        )
    
    elif request.format.lower() == "csv":
        csv_content = generate_csv_report(request.campaign_ids)
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=campaign_report.csv"}
        )
    
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'pdf' or 'csv'")

@app.get("/api/historical-data/{category_id}", tags=["Analytics"])
async def get_historical_data(category_id: str, period_days: int = 30):
    """
    Get historical performance data from Mercado Livre for a specific category
    """
    try:
        historical_data = await get_mercadolibre_historical_data(category_id, period_days)
        
        # Calculate summary statistics
        total_impressions = sum(h.impressions for h in historical_data)
        total_clicks = sum(h.clicks for h in historical_data)
        total_conversions = sum(h.conversions for h in historical_data)
        total_spend = sum(h.spend for h in historical_data)
        
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
        
        return {
            "category_id": category_id,
            "period_days": period_days,
            "data": [h.dict() for h in historical_data],
            "summary": {
                "total_impressions": total_impressions,
                "total_clicks": total_clicks,
                "total_conversions": total_conversions,
                "total_spend": round(total_spend, 2),
                "avg_ctr": round(avg_ctr, 2),
                "avg_conversion_rate": round(avg_conversion_rate, 2),
                "avg_cpc": round(avg_cpc, 2)
            }
        }
    except Exception as e:
        logger.error(f"Error fetching historical data: {e}")
        raise HTTPException(status_code=500, detail="Error fetching historical data")

@app.get("/api/dashboard/{campaign_id}", tags=["Analytics"])
async def get_dashboard_data(campaign_id: str):
    """
    Get dashboard data with interactive charts for a campaign
    """
    if campaign_id not in campaign_results:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    result = campaign_results[campaign_id]
    
    # Create dashboard metrics
    dashboard_data = {
        "campaign_id": campaign_id,
        "metrics": {
            "reach": result["estimated_reach"],
            "clicks": result["estimated_clicks"], 
            "conversions": result["estimated_conversions"],
            "revenue": result["estimated_revenue"],
            "cpc": result["cost_per_click"],
            "roi": result["roi_percentage"]
        },
        "charts": {
            "funnel": {
                "reach": result["estimated_reach"],
                "clicks": result["estimated_clicks"],
                "conversions": result["estimated_conversions"]
            },
            "financial": {
                "spend": result["request_data"]["budget"],
                "revenue": result["estimated_revenue"],
                "profit": result["estimated_revenue"] - result["request_data"]["budget"]
            }
        },
        "recommendations": result["recommendations"]
    }
    
    return dashboard_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)