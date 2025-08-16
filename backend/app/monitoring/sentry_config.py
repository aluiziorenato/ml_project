"""
Sentry integration for error monitoring and performance tracking.
Configures Sentry SDK with FastAPI integration and GitHub secrets.
"""
import logging
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.httpx import HttpxIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.settings import settings

logger = logging.getLogger(__name__)


def init_sentry():
    """
    Initialize Sentry SDK with FastAPI and other integrations.
    Only initializes if SENTRY_DSN is provided via environment variable.
    """
    if not settings.sentry_dsn:
        logger.info("Sentry DSN not configured, skipping Sentry initialization")
        return False
    
    try:
        # Configure logging integration to capture logs as breadcrumbs
        sentry_logging = LoggingIntegration(
            level=logging.INFO,        # Capture info and above as breadcrumbs
            event_level=logging.ERROR  # Send errors as events
        )
        
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
            profiles_sample_rate=0.1,  # Profile 10% of sampled transactions
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
                HttpxIntegration(),
                sentry_logging,
            ],
            # Set tag for service identification
            before_send=lambda event, hint: add_service_context(event),
            # Additional configuration
            attach_stacktrace=True,
            send_default_pii=False,  # Don't send personally identifiable information
        )
        
        logger.info(f"Sentry initialized for environment: {settings.sentry_environment}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize Sentry: {e}")
        return False


def add_service_context(event):
    """Add service-specific context to Sentry events."""
    event.setdefault("tags", {})
    event["tags"]["service"] = "ml-project-backend"
    event["tags"]["version"] = "2.0.0"
    
    # Add custom context
    event.setdefault("contexts", {})
    event["contexts"]["app"] = {
        "name": "ML Integration Backend",
        "version": "2.0.0"
    }
    
    return event


def capture_message(message: str, level: str = "info", **kwargs):
    """
    Capture a custom message with Sentry.
    
    Args:
        message: The message to capture
        level: Log level (debug, info, warning, error, fatal)
        **kwargs: Additional context data
    """
    if settings.sentry_dsn:
        with sentry_sdk.configure_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_message(message, level)
    else:
        logger.log(getattr(logging, level.upper(), logging.INFO), message)


def capture_exception(exception: Exception, **kwargs):
    """
    Capture an exception with additional context.
    
    Args:
        exception: The exception to capture
        **kwargs: Additional context data
    """
    if settings.sentry_dsn:
        with sentry_sdk.configure_scope() as scope:
            for key, value in kwargs.items():
                scope.set_extra(key, value)
            sentry_sdk.capture_exception(exception)
    else:
        logger.exception("Exception occurred", exc_info=exception)


def add_breadcrumb(message: str, category: str = "default", level: str = "info", data: dict = None):
    """
    Add a breadcrumb for debugging context.
    
    Args:
        message: Breadcrumb message
        category: Category for grouping (e.g., "auth", "api", "db")
        level: Severity level
        data: Additional data dictionary
    """
    if settings.sentry_dsn:
        sentry_sdk.add_breadcrumb({
            "message": message,
            "category": category,
            "level": level,
            "data": data or {}
        })