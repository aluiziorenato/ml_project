"""
Loki logging configuration
"""

import logging
import logging_loki
import os
from typing import Optional

def setup_loki_logging(loki_url: Optional[str] = None, app_name: str = "ml_project_backend"):
    """
    Configure Loki logging handler
    
    Args:
        loki_url: Loki server URL (default: http://localhost:3100)
        app_name: Application name for log labels
    """
    
    # Default Loki URL
    if not loki_url:
        loki_url = os.getenv("LOKI_URL", "http://localhost:3100")
    
    try:
        # Create Loki handler
        handler = logging_loki.LokiHandler(
            url=f"{loki_url}/loki/api/v1/push",
            tags={"application": app_name},
            version="1",
        )
        
        # Configure logger
        logger = logging.getLogger()
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Test log
        logger.info("Loki logging configured successfully", extra={"tags": {"component": "logging"}})
        
        return True
        
    except Exception as e:
        # Fallback to console logging if Loki is not available
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        )
        
        logger = logging.getLogger()
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        
        logger.warning(f"Failed to configure Loki logging, falling back to console: {e}")
        return False

def get_structured_logger(component: str):
    """
    Get a structured logger with component tagging
    
    Args:
        component: Component name for log organization
    """
    logger = logging.getLogger(component)
    
    # Add structured logging methods
    def log_request(method: str, path: str, status_code: int, duration: float, user_id: str = None):
        extra = {
            "tags": {
                "component": component,
                "type": "request",
                "method": method,
                "status_code": str(status_code)
            }
        }
        if user_id:
            extra["tags"]["user_id"] = user_id
            
        logger.info(
            f"Request {method} {path} - {status_code} ({duration:.3f}s)",
            extra=extra
        )
    
    def log_business_event(event_type: str, details: dict = None):
        extra = {
            "tags": {
                "component": component,
                "type": "business_event",
                "event_type": event_type
            }
        }
        if details:
            extra["tags"].update(details)
            
        logger.info(f"Business event: {event_type}", extra=extra)
    
    def log_error(error: Exception, context: dict = None):
        extra = {
            "tags": {
                "component": component,
                "type": "error",
                "error_type": type(error).__name__
            }
        }
        if context:
            extra["tags"].update(context)
            
        logger.error(f"Error: {str(error)}", extra=extra, exc_info=True)
    
    def log_performance(operation: str, duration: float, metadata: dict = None):
        extra = {
            "tags": {
                "component": component,
                "type": "performance",
                "operation": operation
            }
        }
        if metadata:
            extra["tags"].update(metadata)
            
        logger.info(f"Performance: {operation} took {duration:.3f}s", extra=extra)
    
    # Attach methods to logger
    logger.log_request = log_request
    logger.log_business_event = log_business_event
    logger.log_error = log_error
    logger.log_performance = log_performance
    
    return logger

# Component loggers
auth_logger = get_structured_logger("auth")
api_logger = get_structured_logger("api")
database_logger = get_structured_logger("database")
ml_logger = get_structured_logger("ml")
campaign_logger = get_structured_logger("campaigns")
system_logger = get_structured_logger("system")