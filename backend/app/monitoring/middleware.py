"""
Monitoring middleware for automatic metrics collection
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable

from .prometheus_metrics import record_request
from .loki_config import api_logger

class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically collect request metrics and logs
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Record start time
        start_time = time.time()
        
        # Get request details
        method = request.method
        path = request.url.path
        
        try:
            # Process request
            response = await call_next(request)
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            record_request(method, path, response.status_code, duration)
            
            # Log request
            api_logger.log_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration=duration,
                user_id=getattr(request.state, 'user_id', None)
            )
            
            return response
            
        except Exception as e:
            # Calculate duration for failed requests
            duration = time.time() - start_time
            
            # Record failed request metrics
            record_request(method, path, 500, duration)
            
            # Log error
            api_logger.log_error(e, {
                "method": method,
                "path": path,
                "duration": duration
            })
            
            # Re-raise the exception
            raise e