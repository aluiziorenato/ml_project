"""
Prometheus metrics configuration and collectors
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time
import psutil
import logging

# Request metrics
request_count = Counter(
    'http_requests_total', 
    'Total HTTP requests', 
    ['method', 'endpoint', 'status_code']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# System metrics
system_cpu_usage = Gauge('system_cpu_usage_percent', 'System CPU usage percentage')
system_memory_usage = Gauge('system_memory_usage_percent', 'System memory usage percentage')
system_disk_usage = Gauge('system_disk_usage_percent', 'System disk usage percentage')

# Application metrics
active_connections = Gauge('active_connections_total', 'Number of active connections')
database_connections = Gauge('database_connections_active', 'Active database connections')
cache_hits = Counter('cache_hits_total', 'Total cache hits')
cache_misses = Counter('cache_misses_total', 'Total cache misses')

# Business metrics
user_logins = Counter('user_logins_total', 'Total user logins', ['status'])
api_calls = Counter('api_calls_total', 'Total API calls', ['service', 'endpoint'])
errors = Counter('application_errors_total', 'Application errors', ['error_type'])

# Campaign metrics
campaigns_active = Gauge('campaigns_active_total', 'Number of active campaigns')
campaigns_clicks = Counter('campaigns_clicks_total', 'Total campaign clicks', ['campaign_id'])
campaigns_conversions = Counter('campaigns_conversions_total', 'Total campaign conversions', ['campaign_id'])

# ML Model metrics
model_predictions = Counter('ml_model_predictions_total', 'Total ML model predictions', ['model_name'])
model_training_duration = Histogram('ml_model_training_duration_seconds', 'ML model training duration')
model_accuracy = Gauge('ml_model_accuracy', 'ML model accuracy score', ['model_name'])

# Security metrics
security_events = Counter('security_events_total', 'Security events', ['event_type'])
failed_auth_attempts = Counter('failed_auth_attempts_total', 'Failed authentication attempts', ['ip_address'])

# Infrastructure metrics  
queue_size = Gauge('queue_size', 'Background task queue size', ['queue_name'])
cache_operations = Counter('cache_operations_total', 'Cache operations', ['operation', 'result'])

logger = logging.getLogger(__name__)

def update_system_metrics():
    """Update system performance metrics"""
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)
        
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.percent)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        system_disk_usage.set(disk_percent)
        
    except Exception as e:
        logger.error(f"Error updating system metrics: {e}")

def record_request(method: str, endpoint: str, status_code: int, duration: float):
    """Record HTTP request metrics"""
    request_count.labels(method=method, endpoint=endpoint, status_code=status_code).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration)

def record_user_login(success: bool):
    """Record user login attempt"""
    status = 'success' if success else 'failed'
    user_logins.labels(status=status).inc()

def record_api_call(service: str, endpoint: str):
    """Record API call"""
    api_calls.labels(service=service, endpoint=endpoint).inc()

def record_error(error_type: str):
    """Record application error"""
    errors.labels(error_type=error_type).inc()

def record_campaign_click(campaign_id: str):
    """Record campaign click"""
    campaigns_clicks.labels(campaign_id=campaign_id).inc()

def record_campaign_conversion(campaign_id: str):
    """Record campaign conversion"""
    campaigns_conversions.labels(campaign_id=campaign_id).inc()

def record_model_prediction(model_name: str):
    """Record ML model prediction"""
    model_predictions.labels(model_name=model_name).inc()

def set_model_accuracy(model_name: str, accuracy: float):
    """Set ML model accuracy"""
    model_accuracy.labels(model_name=model_name).set(accuracy)

def record_security_event(event_type: str):
    """Record security event"""
    security_events.labels(event_type=event_type).inc()

def record_failed_auth(ip_address: str):
    """Record failed authentication attempt"""
    failed_auth_attempts.labels(ip_address=ip_address).inc()

def set_queue_size(queue_name: str, size: int):
    """Set queue size"""
    queue_size.labels(queue_name=queue_name).set(size)

def record_cache_operation(operation: str, result: str):
    """Record cache operation"""
    cache_operations.labels(operation=operation, result=result).inc()

def get_metrics():
    """Get all metrics in Prometheus format"""
    # Update system metrics before returning
    update_system_metrics()
    return generate_latest()