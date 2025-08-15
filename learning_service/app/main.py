from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from datetime import datetime
from typing import Dict, List, Any
import logging
import io
import csv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Aprendizado Contínuo - Mercado Livre", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# In-memory storage for demo purposes (in production, use a database)
model_updates = []
learning_history = []

class ModelUpdateRequest(BaseModel):
    campaign_id: str
    actual_clicks: int
    actual_conversions: int
    actual_revenue: float
    predicted_clicks: int
    predicted_conversions: int
    predicted_revenue: float
    notes: str = ""

class ModelUpdateResponse(BaseModel):
    update_id: str
    status: str
    accuracy_metrics: Dict[str, float]
    improvement_suggestions: List[str]
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    with open("static/index.html", "r", encoding="utf-8") as file:
        return HTMLResponse(content=file.read())

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "learning_service"}

@app.post("/api/update-model", response_model=ModelUpdateResponse)
async def update_model(request: ModelUpdateRequest) -> ModelUpdateResponse:
    """
    Update the model with actual campaign results for continuous learning
    """
    logger.info(f"Updating model with results from campaign: {request.campaign_id}")
    
    # Generate update ID
    update_id = f"UPD_{len(model_updates) + 1:06d}"
    
    # Calculate accuracy metrics
    click_accuracy = 1 - abs(request.actual_clicks - request.predicted_clicks) / max(request.predicted_clicks, 1)
    conversion_accuracy = 1 - abs(request.actual_conversions - request.predicted_conversions) / max(request.predicted_conversions, 1)
    revenue_accuracy = 1 - abs(request.actual_revenue - request.predicted_revenue) / max(request.predicted_revenue, 1)
    
    # Ensure accuracy is between 0 and 1
    click_accuracy = max(0, min(1, click_accuracy))
    conversion_accuracy = max(0, min(1, conversion_accuracy))
    revenue_accuracy = max(0, min(1, revenue_accuracy))
    
    overall_accuracy = (click_accuracy + conversion_accuracy + revenue_accuracy) / 3
    
    # Generate improvement suggestions based on accuracy
    suggestions = []
    if click_accuracy < 0.8:
        suggestions.append("Improve click prediction models - consider seasonality factors")
    if conversion_accuracy < 0.8:
        suggestions.append("Enhance conversion rate modeling - analyze user behavior patterns")
    if revenue_accuracy < 0.8:
        suggestions.append("Refine revenue forecasting - incorporate market trends")
    if overall_accuracy > 0.9:
        suggestions.append("Excellent prediction accuracy - maintain current model parameters")
    
    # Store the update
    update_record = {
        "update_id": update_id,
        "campaign_id": request.campaign_id,
        "timestamp": datetime.now().isoformat(),
        "actual_metrics": {
            "clicks": request.actual_clicks,
            "conversions": request.actual_conversions,
            "revenue": request.actual_revenue
        },
        "predicted_metrics": {
            "clicks": request.predicted_clicks,
            "conversions": request.predicted_conversions,
            "revenue": request.predicted_revenue
        },
        "accuracy_metrics": {
            "click_accuracy": round(click_accuracy, 3),
            "conversion_accuracy": round(conversion_accuracy, 3),
            "revenue_accuracy": round(revenue_accuracy, 3),
            "overall_accuracy": round(overall_accuracy, 3)
        },
        "notes": request.notes
    }
    
    model_updates.append(update_record)
    learning_history.append({
        "timestamp": datetime.now().isoformat(),
        "accuracy": overall_accuracy,
        "campaign_id": request.campaign_id
    })
    
    return ModelUpdateResponse(
        update_id=update_id,
        status="success",
        accuracy_metrics={
            "click_accuracy": round(click_accuracy, 3),
            "conversion_accuracy": round(conversion_accuracy, 3),
            "revenue_accuracy": round(revenue_accuracy, 3),
            "overall_accuracy": round(overall_accuracy, 3)
        },
        improvement_suggestions=suggestions,
        timestamp=datetime.now().isoformat()
    )

@app.post("/api/upload-results")
async def upload_results(file: UploadFile = File(...)):
    """
    Upload campaign results from CSV file for batch model updates
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    content = await file.read()
    csv_content = io.StringIO(content.decode('utf-8'))
    
    try:
        csv_reader = csv.DictReader(csv_content)
        updates_processed = 0
        
        for row in csv_reader:
            # Process each row as a model update
            request = ModelUpdateRequest(
                campaign_id=row.get('campaign_id', ''),
                actual_clicks=int(row.get('actual_clicks', 0)),
                actual_conversions=int(row.get('actual_conversions', 0)),
                actual_revenue=float(row.get('actual_revenue', 0)),
                predicted_clicks=int(row.get('predicted_clicks', 0)),
                predicted_conversions=int(row.get('predicted_conversions', 0)),
                predicted_revenue=float(row.get('predicted_revenue', 0)),
                notes=row.get('notes', '')
            )
            
            # Update model with this data
            await update_model(request)
            updates_processed += 1
        
        return {
            "status": "success",
            "message": f"Processed {updates_processed} campaign updates",
            "updates_processed": updates_processed
        }
    
    except Exception as e:
        logger.error(f"Error processing CSV file: {e}")
        raise HTTPException(status_code=400, detail=f"Error processing CSV file: {str(e)}")

@app.get("/api/learning-history")
async def get_learning_history():
    """Get the learning history for visualization"""
    return {
        "history": learning_history[-50:],  # Return last 50 entries
        "total_updates": len(model_updates),
        "average_accuracy": sum(h["accuracy"] for h in learning_history) / max(len(learning_history), 1)
    }

@app.get("/api/model-performance")
async def get_model_performance():
    """Get current model performance metrics"""
    if not model_updates:
        return {"message": "No model updates available yet"}
    
    recent_updates = model_updates[-10:]  # Last 10 updates
    
    avg_metrics = {
        "click_accuracy": sum(u["accuracy_metrics"]["click_accuracy"] for u in recent_updates) / len(recent_updates),
        "conversion_accuracy": sum(u["accuracy_metrics"]["conversion_accuracy"] for u in recent_updates) / len(recent_updates),
        "revenue_accuracy": sum(u["accuracy_metrics"]["revenue_accuracy"] for u in recent_updates) / len(recent_updates),
        "overall_accuracy": sum(u["accuracy_metrics"]["overall_accuracy"] for u in recent_updates) / len(recent_updates)
    }
    
    return {
        "current_performance": avg_metrics,
        "total_campaigns_analyzed": len(model_updates),
        "last_update": model_updates[-1]["timestamp"] if model_updates else None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)