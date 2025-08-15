from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import io
import csv
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Aprendizado Contínuo - Mercado Livre", 
    version="1.0.0",
    description="API para aprendizado contínuo e gerenciamento de modelos de ML",
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
model_updates = []
learning_history = []
models_storage = {}
training_jobs = {}

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

class ModelCreateRequest(BaseModel):
    name: str
    description: str
    model_type: str  # "linear_regression", "random_forest", "neural_network"
    hyperparameters: Dict[str, Any] = {}
    features: List[str] = []

class ModelResponse(BaseModel):
    model_id: str
    name: str
    description: str
    model_type: str
    status: str  # "training", "ready", "archived"
    hyperparameters: Dict[str, Any]
    features: List[str]
    performance_metrics: Dict[str, float]
    created_at: str
    updated_at: str
    version: str

class TrainingJobRequest(BaseModel):
    model_id: str
    training_data_source: str
    validation_split: float = 0.2
    epochs: Optional[int] = None
    batch_size: Optional[int] = None

class TrainingJobResponse(BaseModel):
    job_id: str
    model_id: str
    status: str  # "queued", "running", "completed", "failed"
    progress: float
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    logs: List[str] = []
    final_metrics: Dict[str, float] = {}

class ModelListResponse(BaseModel):
    models: List[ModelResponse]
    total: int
    page: int
    per_page: int

class PredictionRequest(BaseModel):
    model_id: str
    features: Dict[str, Any]

class PredictionResponse(BaseModel):
    prediction: Dict[str, Any]
    confidence: float
    model_version: str
    timestamp: str

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main frontend page"""
    try:
        with open("static/index.html", "r", encoding="utf-8") as file:
            return HTMLResponse(content=file.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Learning Service</h1><p>API available at /docs</p>")

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

# Model Management Endpoints

@app.post("/api/models", response_model=ModelResponse)
async def create_model(request: ModelCreateRequest):
    """Create a new ML model"""
    model_id = f"MDL_{str(uuid.uuid4())[:8].upper()}"
    
    # Validate model type
    valid_types = ["linear_regression", "random_forest", "neural_network", "svm", "gradient_boosting"]
    if request.model_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Model type must be one of: {valid_types}")
    
    # Create model
    model = ModelResponse(
        model_id=model_id,
        name=request.name,
        description=request.description,
        model_type=request.model_type,
        status="ready",
        hyperparameters=request.hyperparameters,
        features=request.features,
        performance_metrics={},
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat(),
        version="1.0.0"
    )
    
    models_storage[model_id] = model
    logger.info(f"Created model {model_id}: {request.name}")
    
    return model

@app.get("/api/models", response_model=ModelListResponse)
async def list_models(page: int = 1, per_page: int = 10, status: Optional[str] = None, model_type: Optional[str] = None):
    """List all models with pagination and optional filters"""
    models = list(models_storage.values())
    
    # Filter by status
    if status:
        models = [m for m in models if m.status == status]
    
    # Filter by model type
    if model_type:
        models = [m for m in models if m.model_type == model_type]
    
    total = len(models)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_models = models[start_idx:end_idx]
    
    return ModelListResponse(
        models=paginated_models,
        total=total,
        page=page,
        per_page=per_page
    )

@app.get("/api/models/{model_id}", response_model=ModelResponse)
async def get_model(model_id: str):
    """Get a specific model by ID"""
    if model_id not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    
    return models_storage[model_id]

@app.put("/api/models/{model_id}", response_model=ModelResponse)
async def update_model(model_id: str, updates: Dict[str, Any]):
    """Update model metadata"""
    if model_id not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models_storage[model_id]
    
    # Update allowed fields
    allowed_fields = ["name", "description", "status", "hyperparameters"]
    for field, value in updates.items():
        if field in allowed_fields:
            setattr(model, field, value)
    
    model.updated_at = datetime.now().isoformat()
    models_storage[model_id] = model
    
    return model

@app.delete("/api/models/{model_id}")
async def delete_model(model_id: str):
    """Delete a model"""
    if model_id not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Check if model has active training jobs
    active_jobs = [job for job in training_jobs.values() 
                   if job.model_id == model_id and job.status in ["queued", "running"]]
    
    if active_jobs:
        raise HTTPException(status_code=400, detail="Cannot delete model with active training jobs")
    
    del models_storage[model_id]
    return {"message": f"Model {model_id} deleted successfully"}

@app.post("/api/models/{model_id}/train", response_model=TrainingJobResponse)
async def start_training(model_id: str, request: TrainingJobRequest):
    """Start training a model"""
    if model_id not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if request.model_id != model_id:
        raise HTTPException(status_code=400, detail="Model ID mismatch")
    
    job_id = f"JOB_{str(uuid.uuid4())[:8].upper()}"
    
    # Create training job
    job = TrainingJobResponse(
        job_id=job_id,
        model_id=model_id,
        status="queued",
        progress=0.0,
        started_at=None,
        completed_at=None,
        logs=[f"Training job {job_id} created"],
        final_metrics={}
    )
    
    training_jobs[job_id] = job
    
    # Simulate starting training (in real implementation, this would trigger async training)
    job.status = "running"
    job.started_at = datetime.now().isoformat()
    job.progress = 10.0
    job.logs.append("Training started")
    
    models_storage[model_id].status = "training"
    
    return job

@app.get("/api/training-jobs", response_model=List[TrainingJobResponse])
async def list_training_jobs(status: Optional[str] = None, model_id: Optional[str] = None):
    """List training jobs with optional filters"""
    jobs = list(training_jobs.values())
    
    if status:
        jobs = [j for j in jobs if j.status == status]
    
    if model_id:
        jobs = [j for j in jobs if j.model_id == model_id]
    
    return jobs

@app.get("/api/training-jobs/{job_id}", response_model=TrainingJobResponse)
async def get_training_job(job_id: str):
    """Get training job status and details"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    # Simulate progress updates for demo
    if job.status == "running" and job.progress < 100:
        import random
        job.progress = min(100.0, job.progress + random.uniform(5, 15))
        
        if job.progress >= 100:
            job.status = "completed"
            job.completed_at = datetime.now().isoformat()
            job.final_metrics = {
                "accuracy": round(random.uniform(0.8, 0.95), 3),
                "precision": round(random.uniform(0.75, 0.9), 3),
                "recall": round(random.uniform(0.7, 0.85), 3),
                "f1_score": round(random.uniform(0.72, 0.87), 3)
            }
            job.logs.append("Training completed successfully")
            
            # Update model status and performance
            if job.model_id in models_storage:
                models_storage[job.model_id].status = "ready"
                models_storage[job.model_id].performance_metrics = job.final_metrics
    
    return job

@app.post("/api/training-jobs/{job_id}/cancel")
async def cancel_training_job(job_id: str):
    """Cancel a training job"""
    if job_id not in training_jobs:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    job = training_jobs[job_id]
    
    if job.status not in ["queued", "running"]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled")
    
    job.status = "cancelled"
    job.completed_at = datetime.now().isoformat()
    job.logs.append("Training cancelled by user")
    
    # Reset model status
    if job.model_id in models_storage:
        models_storage[job.model_id].status = "ready"
    
    return {"message": f"Training job {job_id} cancelled"}

@app.post("/api/models/{model_id}/predict", response_model=PredictionResponse)
async def make_prediction(model_id: str, request: PredictionRequest):
    """Make predictions using a trained model"""
    if model_id not in models_storage:
        raise HTTPException(status_code=404, detail="Model not found")
    
    model = models_storage[model_id]
    
    if model.status != "ready":
        raise HTTPException(status_code=400, detail="Model is not ready for predictions")
    
    if request.model_id != model_id:
        raise HTTPException(status_code=400, detail="Model ID mismatch")
    
    # Simulate prediction (in real implementation, this would use the trained model)
    import random
    
    prediction = {}
    if model.model_type == "linear_regression":
        prediction = {"value": round(random.uniform(100, 1000), 2)}
    elif model.model_type in ["random_forest", "gradient_boosting"]:
        prediction = {"class": random.choice(["high", "medium", "low"]), "probabilities": [0.3, 0.5, 0.2]}
    else:
        prediction = {"result": "processed", "score": round(random.uniform(0.1, 1.0), 3)}
    
    confidence = random.uniform(0.7, 0.95)
    
    return PredictionResponse(
        prediction=prediction,
        confidence=round(confidence, 3),
        model_version=model.version,
        timestamp=datetime.now().isoformat()
    )

@app.get("/api/models/stats")
async def get_models_stats():
    """Get aggregate statistics for all models"""
    if not models_storage:
        return {
            "total_models": 0,
            "ready_models": 0,
            "training_models": 0,
            "avg_accuracy": 0,
            "model_types": {}
        }
    
    models = list(models_storage.values())
    ready_models = [m for m in models if m.status == "ready"]
    training_models = [m for m in models if m.status == "training"]
    
    # Calculate average accuracy for models with performance metrics
    models_with_metrics = [m for m in models if m.performance_metrics.get("accuracy")]
    avg_accuracy = sum(m.performance_metrics["accuracy"] for m in models_with_metrics) / max(len(models_with_metrics), 1)
    
    # Count by model type
    model_types = {}
    for model in models:
        model_types[model.model_type] = model_types.get(model.model_type, 0) + 1
    
    return {
        "total_models": len(models),
        "ready_models": len(ready_models),
        "training_models": len(training_models),
        "avg_accuracy": round(avg_accuracy, 3),
        "model_types": model_types
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)