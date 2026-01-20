"""
Settings API routes.
Handles system configuration management.
"""

from typing import Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.settings_service import (
    SettingsService,
    test_github_connection,
    test_openai_connection
)

router = APIRouter(prefix="/settings", tags=["Settings"])


# Request/Response Models
class SettingsResponse(BaseModel):
    """Settings response model."""
    settings: Dict[str, Any]


class UpdateSettingsRequest(BaseModel):
    """Update settings request model."""
    # GitHub OAuth
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None
    github_redirect_uri: Optional[str] = None
    github_scopes: Optional[str] = None

    # OpenAI
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None
    openai_max_tokens: Optional[int] = None
    openai_temperature: Optional[float] = None

    # Local LLM
    local_llm_enabled: Optional[bool] = None
    local_llm_url: Optional[str] = None
    local_llm_model: Optional[str] = None

    # JWT
    jwt_secret_key: Optional[str] = None
    jwt_algorithm: Optional[str] = None
    jwt_expire_minutes: Optional[int] = None


class TestGithubRequest(BaseModel):
    """Test GitHub connection request."""
    client_id: str
    client_secret: str


class TestOpenAIRequest(BaseModel):
    """Test OpenAI connection request."""
    api_key: str


class TestResult(BaseModel):
    """Test result response."""
    success: bool
    message: Optional[str] = None


# Routes
@router.get("", response_model=SettingsResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """
    Get all system settings.

    Sensitive values are partially masked for security.
    """
    service = SettingsService(db)
    await service.init_default_settings()
    settings = await service.get_all_settings(mask_sensitive=True)
    return SettingsResponse(settings=settings)


@router.post("")
async def update_settings(
    request: UpdateSettingsRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Update system settings.

    Only non-null values will be updated.
    """
    service = SettingsService(db)

    # Convert request to dict, excluding None values
    settings_dict = {
        k: v for k, v in request.dict().items()
        if v is not None
    }

    await service.update_settings(settings_dict)

    return {"status": "success", "message": "设置已保存"}


@router.get("/{key}")
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    """Get a single setting by key."""
    service = SettingsService(db)
    value = await service.get_setting(key)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Setting '{key}' not found")
    return {"key": key, "value": value}


@router.post("/test/github", response_model=TestResult)
async def test_github(request: TestGithubRequest):
    """
    Test GitHub OAuth credentials.

    Validates the format and connectivity to GitHub API.
    """
    result = await test_github_connection(
        request.client_id,
        request.client_secret
    )
    return TestResult(**result)


@router.post("/test/openai", response_model=TestResult)
async def test_openai(request: TestOpenAIRequest):
    """
    Test OpenAI API key.

    Validates the API key by listing available models.
    """
    result = await test_openai_connection(request.api_key)
    return TestResult(**result)


@router.get("/category/{category}")
async def get_settings_by_category(
    category: str,
    db: AsyncSession = Depends(get_db)
):
    """Get settings filtered by category."""
    service = SettingsService(db)
    settings = await service.get_settings_by_category(category)
    return {"category": category, "settings": settings}
