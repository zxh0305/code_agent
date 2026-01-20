"""
Main FastAPI application entry point.
Production-ready with logging, middleware, and error handling.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.redis import redis_client
from app.core.logging import get_logger, configure_logging
from app.core.middleware import setup_middlewares
from app.api import github_routes, code_routes, pr_routes, llm_routes, settings_routes

# Initialize logging
configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting application", app_name=settings.APP_NAME, version=settings.APP_VERSION)

    # Startup
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    try:
        await redis_client.connect()
        logger.info("Redis connection established")
    except Exception as e:
        logger.warning("Failed to connect to Redis, rate limiting disabled", error=str(e))

    logger.info("Application started successfully")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    await redis_client.disconnect()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
# 智能GitHub代码开发协作平台 API

一个由AI驱动的智能GitHub代码开发协作平台，提供以下功能：

## 功能模块

- **GitHub集成**: OAuth授权、仓库管理、分支操作
- **代码分析**: AST解析、代码结构提取、度量计算
- **PR管理**: 自动创建、审核、合并PR
- **AI助手**: 代码生成、修改、审核、Bug修复

## 认证方式

大部分API需要Bearer Token认证。在请求头中添加：
```
Authorization: Bearer <your-token>
```

## 错误处理

所有错误响应遵循统一格式：
```json
{
    "error": {
        "error_code": "ERROR_CODE",
        "message": "Human readable message",
        "details": {}
    },
    "request_id": "abc123"
}
```
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    responses={
        401: {"description": "Authentication required"},
        403: {"description": "Permission denied"},
        429: {"description": "Rate limit exceeded"},
        500: {"description": "Internal server error"},
    },
)

# Configure CORS (must be added before other middlewares)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# Setup custom middlewares (logging, rate limiting, auth, exception handling)
setup_middlewares(app)

# Include routers with tags for documentation grouping
app.include_router(
    github_routes.router,
    prefix=settings.API_PREFIX,
    tags=["GitHub"]
)
app.include_router(
    code_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Code Analysis"]
)
app.include_router(
    pr_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Pull Requests"]
)
app.include_router(
    llm_routes.router,
    prefix=settings.API_PREFIX,
    tags=["AI/LLM"]
)
app.include_router(
    settings_routes.router,
    prefix=settings.API_PREFIX,
    tags=["Settings"]
)


@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint.

    Returns basic application information.
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """
    Health check endpoint.

    Returns the health status of the application and its dependencies.
    Used for container orchestration health checks.
    """
    health_status = {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "checks": {}
    }

    # Check database connection
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis connection
    try:
        if redis_client._client:
            await redis_client.client.ping()
            health_status["checks"]["redis"] = "healthy"
        else:
            health_status["checks"]["redis"] = "not connected"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    return health_status


@app.get("/ready", tags=["System"])
async def readiness_check():
    """
    Readiness check endpoint.

    Returns whether the application is ready to accept traffic.
    """
    # Check if all required services are available
    ready = True
    checks = {}

    # Database must be available
    try:
        from app.core.database import engine
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        checks["database"] = "ready"
    except Exception:
        checks["database"] = "not ready"
        ready = False

    return {
        "ready": ready,
        "checks": checks
    }


if __name__ == "__main__":
    import uvicorn

    logger.info(
        "Starting server",
        host=settings.HOST,
        port=settings.PORT,
        debug=settings.DEBUG
    )

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS if not settings.DEBUG else 1,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info",
    )
