"""
Metrics and monitoring endpoints
"""

from fastapi import APIRouter, Response, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from prometheus_client import CONTENT_TYPE_LATEST
import time
import psutil
from typing import Dict, Any, Optional

from ..monitoring.prometheus_metrics import (
    get_metrics,
    update_system_metrics,
    active_connections,
    campaigns_active,
    set_model_accuracy
)
from ..monitoring.loki_config import system_logger, api_logger
from ..settings import settings

router = APIRouter(prefix="/api/metrics", tags=["metrics"])
security = HTTPBearer(auto_error=False)

def verify_metrics_auth(authorization: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verify metrics endpoint authentication"""
    if not settings.enable_metrics_auth:
        return True
    
    if not authorization:
        raise HTTPException(
            status_code=401, 
            detail="Authentication required for metrics endpoint"
        )
    
    if authorization.credentials != settings.metrics_api_key:
        raise HTTPException(
            status_code=403, 
            detail="Invalid authentication credentials"
        )
    
    return True

@router.get("/prometheus")
async def prometheus_metrics(auth: bool = Depends(verify_metrics_auth)):
    """
    Expose Prometheus metrics endpoint
    Requires authentication in production environment
    """
    try:
        # Update system metrics before serving
        update_system_metrics()
        
        # Record API call
        api_logger.log_request("GET", "/api/metrics/prometheus", 200, 0.1)
        
        return Response(
            content=get_metrics(),
            media_type=CONTENT_TYPE_LATEST
        )
    except Exception as e:
        system_logger.log_error(e, {"endpoint": "/api/metrics/prometheus"})
        return Response(
            content="# Error generating metrics\n",
            media_type=CONTENT_TYPE_LATEST,
            status_code=500
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint with detailed system information
    """
    start_time = time.time()
    
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Calculate uptime (simplified)
        boot_time = psutil.boot_time()
        current_time = time.time()
        uptime_seconds = current_time - boot_time
        
        health_data = {
            "status": "healthy",
            "timestamp": time.time(),
            "uptime_seconds": round(uptime_seconds, 2),
            "system": {
                "cpu_percent": round(cpu_percent, 2),
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": round(memory.percent, 2),
                    "used": memory.used
                },
                "disk": {
                    "total": disk.total,
                    "used": disk.used,
                    "free": disk.free,
                    "percent": round((disk.used / disk.total) * 100, 2)
                }
            },
            "application": {
                "active_connections": 0,  # This would be updated by actual connection tracking
                "database_status": "connected",  # This would be checked against actual DB
                "cache_status": "available"
            }
        }
        
        duration = time.time() - start_time
        api_logger.log_request("GET", "/api/metrics/health", 200, duration)
        
        return JSONResponse(content=health_data)
        
    except Exception as e:
        duration = time.time() - start_time
        system_logger.log_error(e, {"endpoint": "/api/metrics/health"})
        api_logger.log_request("GET", "/api/metrics/health", 500, duration)
        
        return JSONResponse(
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            },
            status_code=500
        )

@router.get("/system")
async def system_metrics():
    """
    Detailed system metrics endpoint
    """
    start_time = time.time()
    
    try:
        # CPU information
        cpu_count = psutil.cpu_count()
        cpu_percent_per_core = psutil.cpu_percent(percpu=True, interval=0.1)
        cpu_freq = psutil.cpu_freq()
        
        # Memory information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk information
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()
        
        # Network information
        network_io = psutil.net_io_counters()
        
        # Process information
        process_count = len(psutil.pids())
        
        metrics = {
            "cpu": {
                "count": cpu_count,
                "percent_total": round(sum(cpu_percent_per_core) / len(cpu_percent_per_core), 2),
                "percent_per_core": [round(p, 2) for p in cpu_percent_per_core],
                "frequency": {
                    "current": round(cpu_freq.current, 2) if cpu_freq else None,
                    "min": round(cpu_freq.min, 2) if cpu_freq else None,
                    "max": round(cpu_freq.max, 2) if cpu_freq else None
                }
            },
            "memory": {
                "virtual": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": round(memory.percent, 2),
                    "used": memory.used,
                    "free": memory.free
                },
                "swap": {
                    "total": swap.total,
                    "used": swap.used,
                    "free": swap.free,
                    "percent": round(swap.percent, 2)
                }
            },
            "disk": {
                "usage": {
                    "total": disk_usage.total,
                    "used": disk_usage.used,
                    "free": disk_usage.free,
                    "percent": round((disk_usage.used / disk_usage.total) * 100, 2)
                },
                "io": {
                    "read_count": disk_io.read_count if disk_io else 0,
                    "write_count": disk_io.write_count if disk_io else 0,
                    "read_bytes": disk_io.read_bytes if disk_io else 0,
                    "write_bytes": disk_io.write_bytes if disk_io else 0
                }
            },
            "network": {
                "bytes_sent": network_io.bytes_sent if network_io else 0,
                "bytes_recv": network_io.bytes_recv if network_io else 0,
                "packets_sent": network_io.packets_sent if network_io else 0,
                "packets_recv": network_io.packets_recv if network_io else 0
            },
            "processes": {
                "count": process_count
            }
        }
        
        duration = time.time() - start_time
        api_logger.log_request("GET", "/api/metrics/system", 200, duration)
        
        return JSONResponse(content=metrics)
        
    except Exception as e:
        duration = time.time() - start_time
        system_logger.log_error(e, {"endpoint": "/api/metrics/system"})
        api_logger.log_request("GET", "/api/metrics/system", 500, duration)
        
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )

@router.post("/test-metrics")
async def test_metrics():
    """
    Endpoint to generate test metrics for demonstration
    """
    try:
        # Simulate some metrics
        active_connections.set(42)
        campaigns_active.set(15)
        set_model_accuracy("recommendation_engine", 0.87)
        set_model_accuracy("price_optimizer", 0.92)
        
        # Log test events
        api_logger.log_business_event("metrics_test", {"action": "generate_test_data"})
        system_logger.info("Test metrics generated successfully")
        
        return JSONResponse(content={
            "status": "success",
            "message": "Test metrics generated",
            "metrics": {
                "active_connections": 42,
                "campaigns_active": 15,
                "model_accuracies": {
                    "recommendation_engine": 0.87,
                    "price_optimizer": 0.92
                }
            }
        })
        
    except Exception as e:
        system_logger.log_error(e, {"endpoint": "/api/metrics/test-metrics"})
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )