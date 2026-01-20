"""
Structured logging configuration for production use.
Uses structlog for JSON-formatted, context-rich logging.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor

from app.core.config import settings


def add_app_context(
    logger: logging.Logger,
    method_name: str,
    event_dict: Dict[str, Any]
) -> Dict[str, Any]:
    """Add application context to log entries."""
    event_dict["app_name"] = settings.APP_NAME
    event_dict["app_version"] = settings.APP_VERSION
    return event_dict


def configure_logging() -> None:
    """
    Configure structured logging for the application.

    - Development: Colored, human-readable output
    - Production: JSON format for log aggregation
    """
    # Determine if we're in development or production
    is_development = settings.DEBUG

    # Shared processors for all environments
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
        add_app_context,
    ]

    if is_development:
        # Development: colored console output
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production: JSON output for log aggregation
        processors = shared_processors + [
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    log_level = logging.DEBUG if is_development else logging.INFO

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Set third-party library log levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.DEBUG if is_development else logging.WARNING
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured structlog logger

    Example:
        logger = get_logger(__name__)
        logger.info("Processing request", user_id=123, action="login")
    """
    return structlog.get_logger(name)


# Request context keys
REQUEST_ID_KEY = "request_id"
USER_ID_KEY = "user_id"
CLIENT_IP_KEY = "client_ip"


def bind_request_context(
    request_id: str,
    user_id: int | None = None,
    client_ip: str | None = None
) -> None:
    """
    Bind request context to all subsequent log entries.

    Args:
        request_id: Unique request identifier
        user_id: Authenticated user ID (if available)
        client_ip: Client IP address
    """
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request_id,
        user_id=user_id,
        client_ip=client_ip,
    )


def clear_request_context() -> None:
    """Clear request context after request completion."""
    structlog.contextvars.clear_contextvars()


# Initialize logging on module load
configure_logging()

# Default logger instance
logger = get_logger("app")
