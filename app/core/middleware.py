"""
Middleware components for the FastAPI application.
Includes logging, rate limiting, authentication, and request tracking.
"""

import time
import uuid
from typing import Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import (
    get_logger,
    bind_request_context,
    clear_request_context,
)
from app.core.redis import redis_client
from app.core.config import settings
from app.exceptions import (
    AppException,
    RateLimitError,
    AuthenticationError,
    InvalidTokenError,
)
from app.core.security import decode_access_token

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging all HTTP requests and responses.
    Adds request ID tracking and performance metrics.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Get user ID if authenticated
        user_id = getattr(request.state, "user_id", None)

        # Bind request context to logs
        bind_request_context(
            request_id=request_id,
            user_id=user_id,
            client_ip=client_ip,
        )

        # Log request start
        start_time = time.time()
        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=str(request.query_params),
        )

        try:
            response = await call_next(request)

            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000

            # Log request completion
            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                exc_info=True,
            )
            raise

        finally:
            clear_request_context()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for API rate limiting using Redis.
    Supports IP-based and user-based rate limiting.
    """

    def __init__(
        self,
        app: FastAPI,
        requests_limit: int = None,
        window_seconds: int = None,
    ):
        super().__init__(app)
        self.requests_limit = requests_limit or settings.RATE_LIMIT_REQUESTS
        self.window_seconds = window_seconds or settings.RATE_LIMIT_PERIOD

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get client identifier (IP or user ID)
        client_ip = request.client.host if request.client else "unknown"
        user_id = getattr(request.state, "user_id", None)
        identifier = f"user:{user_id}" if user_id else f"ip:{client_ip}"

        # Check rate limit
        rate_limit_key = f"rate_limit:{identifier}"

        try:
            # Get current request count
            current_count = await redis_client.get(rate_limit_key)
            current_count = int(current_count) if current_count else 0

            if current_count >= self.requests_limit:
                # Get TTL for retry-after header
                ttl = await redis_client.client.ttl(rate_limit_key)
                logger.warning(
                    "Rate limit exceeded",
                    identifier=identifier,
                    limit=self.requests_limit,
                    window=self.window_seconds,
                )
                raise RateLimitError(retry_after=ttl if ttl > 0 else self.window_seconds)

            # Increment counter
            pipe = redis_client.client.pipeline()
            pipe.incr(rate_limit_key)
            if current_count == 0:
                pipe.expire(rate_limit_key, self.window_seconds)
            await pipe.execute()

        except RateLimitError:
            raise
        except Exception as e:
            # Log error but don't block request if Redis is unavailable
            logger.warning(
                "Rate limiting check failed",
                error=str(e),
            )

        return await call_next(request)


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for JWT token authentication.
    Validates tokens and sets user context.
    """

    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/docs",
        "/redoc",
        "/openapi.json",
        "/api/v1/github/auth",
        "/api/v1/github/callback",
        "/api/v1/settings",  # Settings page needs to be accessible
    }

    # Path prefixes that don't require authentication
    PUBLIC_PATH_PREFIXES = {
        "/api/v1/settings/test",  # Connection test endpoints
    }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Check if path is public
        path = request.url.path
        if path in self.PUBLIC_PATHS:
            return await call_next(request)

        for prefix in self.PUBLIC_PATH_PREFIXES:
            if path.startswith(prefix):
                return await call_next(request)

        # Get token from header
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix

            # Validate token
            payload = decode_access_token(token)
            if payload:
                # Set user context
                request.state.user_id = payload.get("sub")
                request.state.token_data = payload
            else:
                # Invalid token - log but allow request for now
                # In strict mode, raise InvalidTokenError
                logger.warning(
                    "Invalid authentication token",
                    path=path,
                )

        return await call_next(request)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Global exception handler middleware.
    Converts exceptions to standardized JSON responses.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AppException as e:
            # Handle application exceptions
            logger.warning(
                "Application exception",
                error_code=e.error_code,
                message=e.message,
                status_code=e.status_code,
            )
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": e.to_dict(),
                    "request_id": getattr(request.state, "request_id", None),
                },
            )
        except Exception as e:
            # Handle unexpected exceptions
            logger.error(
                "Unhandled exception",
                error=str(e),
                exc_info=True,
            )

            # Don't expose internal error details in production
            if settings.DEBUG:
                message = str(e)
            else:
                message = "An unexpected error occurred"

            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "error_code": "INTERNAL_ERROR",
                        "message": message,
                    },
                    "request_id": getattr(request.state, "request_id", None),
                },
            )


def setup_middlewares(app: FastAPI) -> None:
    """
    Setup all middlewares for the application.
    Order matters - middlewares are executed in reverse order.
    """
    # Exception handler should be first (executed last)
    app.add_middleware(ExceptionHandlerMiddleware)

    # Authentication
    app.add_middleware(AuthenticationMiddleware)

    # Rate limiting
    app.add_middleware(RateLimitMiddleware)

    # Request logging should be last (executed first)
    app.add_middleware(RequestLoggingMiddleware)

    logger.info("Middlewares configured successfully")
