"""Logging utilities for ACOS Service."""

import logging
import sys
from typing import Dict, Any
from datetime import datetime


class ACOSLogger:
    """Custom logger for ACOS Service."""
    
    def __init__(self, name: str = "acos_service"):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger configuration."""
        if not self.logger.handlers:
            # Create console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            # Add handler to logger
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.INFO)
    
    def info(self, message: str, **kwargs):
        """Log info message."""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_info}" if extra_info else message
        self.logger.info(full_message)
    
    def error(self, message: str, **kwargs):
        """Log error message."""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_info}" if extra_info else message
        self.logger.error(full_message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message."""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_info}" if extra_info else message
        self.logger.warning(full_message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message."""
        extra_info = " | ".join([f"{k}={v}" for k, v in kwargs.items()])
        full_message = f"{message} | {extra_info}" if extra_info else message
        self.logger.debug(full_message)


def log_error(error: Exception, context: Dict[str, Any] = None):
    """Log error with context information."""
    logger = ACOSLogger()
    
    error_msg = f"Error: {str(error)}"
    if context:
        context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
        error_msg = f"{error_msg} | Context: {context_str}"
    
    logger.error(error_msg)


def log_acos_action(
    action: str, 
    campaign_id: int, 
    acos_value: float, 
    threshold: float,
    result: str
):
    """Log ACOS automation action."""
    logger = ACOSLogger()
    
    logger.info(
        f"ACOS Action: {action}",
        campaign_id=campaign_id,
        acos=f"{acos_value:.2f}%",
        threshold=f"{threshold:.2f}%",
        result=result,
        timestamp=datetime.utcnow().isoformat()
    )


def log_rule_execution(rule_id: int, campaign_id: int, status: str, details: Dict[str, Any]):
    """Log ACOS rule execution."""
    logger = ACOSLogger()
    
    logger.info(
        f"Rule Execution: {status}",
        rule_id=rule_id,
        campaign_id=campaign_id,
        **details
    )


# Global logger instance
logger = ACOSLogger()