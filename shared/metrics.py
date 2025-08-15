"""
Prometheus metrics for ML services
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
from functools import wraps

# Metrics for all services
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status_code', 'service']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint', 'service']
)

# Service-specific metrics
simulator_campaigns = Gauge(
    'simulator_campaigns_total',
    'Total number of campaigns in simulator'
)

simulator_active_campaigns = Gauge(
    'simulator_active_campaigns',
    'Number of active campaigns in simulator'
)

learning_models = Gauge(
    'learning_models_total',
    'Total number of ML models'
)

learning_training_jobs = Gauge(
    'learning_training_jobs_active',
    'Number of active training jobs'
)

optimizer_ab_tests = Gauge(
    'optimizer_ab_tests_total',
    'Total number of A/B tests'
)

optimizer_running_tests = Gauge(
    'optimizer_running_ab_tests',
    'Number of running A/B tests'
)

optimizer_templates = Gauge(
    'optimizer_templates_total',
    'Total number of copy templates'
)

# Business metrics
campaign_simulation_requests = Counter(
    'campaign_simulations_total',
    'Total campaign simulations requested',
    ['category', 'audience']
)

model_predictions = Counter(
    'model_predictions_total',
    'Total model predictions made',
    ['model_type', 'status']
)

copy_optimizations = Counter(
    'copy_optimizations_total',
    'Total copy optimizations performed',
    ['goal', 'category']
)

ab_test_conversions = Counter(
    'ab_test_conversions_total',
    'Total A/B test conversions',
    ['test_id', 'variation']
)

def track_requests(service_name: str):
    """Decorator to track HTTP requests"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request info from FastAPI context
            request = kwargs.get('request') or (args[0] if args else None)
            method = getattr(request, 'method', 'unknown') if request else 'unknown'
            url_path = getattr(request, 'url', {}).path if request and hasattr(request, 'url') else 'unknown'
            
            start_time = time.time()
            
            try:
                # Execute the original function
                response = await func(*args, **kwargs)
                status_code = getattr(response, 'status_code', 200)
                
                # Track successful request
                request_count.labels(
                    method=method,
                    endpoint=url_path,
                    status_code=status_code,
                    service=service_name
                ).inc()
                
                return response
                
            except Exception as e:
                # Track failed request
                status_code = getattr(e, 'status_code', 500)
                request_count.labels(
                    method=method,
                    endpoint=url_path,
                    status_code=status_code,
                    service=service_name
                ).inc()
                raise
                
            finally:
                # Track request duration
                duration = time.time() - start_time
                request_duration.labels(
                    method=method,
                    endpoint=url_path,
                    service=service_name
                ).observe(duration)
        
        return wrapper
    return decorator

def update_simulator_metrics(campaigns_storage):
    """Update simulator service metrics"""
    total_campaigns = len(campaigns_storage)
    active_campaigns = len([c for c in campaigns_storage.values() 
                          if c.get("response", {}).get("status") == "active"])
    
    simulator_campaigns.set(total_campaigns)
    simulator_active_campaigns.set(active_campaigns)

def update_learning_metrics(models_storage, training_jobs):
    """Update learning service metrics"""
    total_models = len(models_storage)
    active_training = len([j for j in training_jobs.values() 
                          if j.status in ["queued", "running"]])
    
    learning_models.set(total_models)
    learning_training_jobs.set(active_training)

def update_optimizer_metrics(ab_tests_storage, templates_storage):
    """Update optimizer service metrics"""
    total_tests = len(ab_tests_storage)
    running_tests = len([t for t in ab_tests_storage.values() 
                        if t.get("response", {}).get("status") == "running"])
    total_templates = len(templates_storage)
    
    optimizer_ab_tests.set(total_tests)
    optimizer_running_tests.set(running_tests)
    optimizer_templates.set(total_templates)

def track_campaign_simulation(category: str, audience: str):
    """Track campaign simulation request"""
    campaign_simulation_requests.labels(
        category=category,
        audience=audience
    ).inc()

def track_model_prediction(model_type: str, status: str):
    """Track model prediction"""
    model_predictions.labels(
        model_type=model_type,
        status=status
    ).inc()

def track_copy_optimization(goal: str, category: str):
    """Track copy optimization"""
    copy_optimizations.labels(
        goal=goal,
        category=category
    ).inc()

def track_ab_test_conversion(test_id: str, variation: int):
    """Track A/B test conversion"""
    ab_test_conversions.labels(
        test_id=test_id,
        variation=str(variation)
    ).inc()

def add_metrics_endpoint(app):
    """Add Prometheus metrics endpoint to FastAPI app"""
    
    @app.get("/metrics")
    async def get_metrics():
        """Prometheus metrics endpoint"""
        return Response(
            content=generate_latest(),
            media_type=CONTENT_TYPE_LATEST
        )

def setup_metrics_middleware(app, service_name: str):
    """Setup metrics middleware for FastAPI app"""
    
    @app.middleware("http")
    async def metrics_middleware(request, call_next):
        """Middleware to collect metrics for all requests"""
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Track metrics
        duration = time.time() - start_time
        
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status_code=response.status_code,
            service=service_name
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path,
            service=service_name
        ).observe(duration)
        
        return response