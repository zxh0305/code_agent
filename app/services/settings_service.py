"""
Settings service for managing system configuration.
"""

import json
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

import httpx
from openai import OpenAI

from app.models.settings import SystemSettings, DEFAULT_SETTINGS


class SettingsService:
    """Service for managing system settings."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def init_default_settings(self) -> None:
        """Initialize default settings if not exist."""
        for setting in DEFAULT_SETTINGS:
            stmt = insert(SystemSettings).values(**setting)
            stmt = stmt.on_conflict_do_nothing(index_elements=['key'])
            await self.db.execute(stmt)
        await self.db.commit()

    async def get_all_settings(self, mask_sensitive: bool = True) -> Dict[str, Any]:
        """
        Get all settings as a dictionary.

        Args:
            mask_sensitive: Whether to mask sensitive values

        Returns:
            Dictionary of all settings
        """
        result = await self.db.execute(select(SystemSettings))
        settings = result.scalars().all()

        settings_dict = {}
        for s in settings:
            value = self._convert_value(s.value, s.value_type)
            if mask_sensitive and s.is_sensitive and value:
                # 敏感信息只显示部分
                if isinstance(value, str) and len(value) > 8:
                    value = value[:4] + "*" * (len(value) - 8) + value[-4:]
            settings_dict[s.key] = value

        return settings_dict

    async def get_setting(self, key: str) -> Optional[Any]:
        """Get a single setting value."""
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        setting = result.scalar_one_or_none()
        if setting:
            return self._convert_value(setting.value, setting.value_type)
        return None

    async def set_setting(self, key: str, value: Any) -> None:
        """Set a single setting value."""
        str_value = self._to_string(value)
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.key == key)
        )
        setting = result.scalar_one_or_none()

        if setting:
            setting.value = str_value
            setting.updated_at = datetime.utcnow()
        else:
            new_setting = SystemSettings(
                key=key,
                value=str_value,
                value_type=self._detect_type(value)
            )
            self.db.add(new_setting)

        await self.db.commit()

    async def update_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update multiple settings at once.

        Args:
            settings: Dictionary of settings to update
        """
        for key, value in settings.items():
            # 直接更新所有提供的值，包括空值
            # 这样用户可以清空敏感设置
            await self.set_setting(key, value)

    async def get_settings_by_category(self, category: str) -> Dict[str, Any]:
        """Get settings filtered by category."""
        result = await self.db.execute(
            select(SystemSettings).where(SystemSettings.category == category)
        )
        settings = result.scalars().all()

        return {
            s.key: self._convert_value(s.value, s.value_type)
            for s in settings
        }

    def _convert_value(self, value: str, value_type: str) -> Any:
        """Convert string value to appropriate type."""
        if value is None or value == "":
            return None

        try:
            if value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value)
            elif value_type == "bool":
                return value.lower() in ("true", "1", "yes")
            elif value_type == "json":
                return json.loads(value)
            else:
                return value
        except (ValueError, json.JSONDecodeError):
            return value

    def _to_string(self, value: Any) -> str:
        """Convert value to string for storage."""
        if isinstance(value, bool):
            return "true" if value else "false"
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        else:
            return str(value) if value is not None else ""

    def _detect_type(self, value: Any) -> str:
        """Detect value type."""
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "float"
        elif isinstance(value, (dict, list)):
            return "json"
        else:
            return "string"


async def test_github_connection(client_id: str, client_secret: str) -> Dict[str, Any]:
    """
    Test GitHub OAuth credentials.

    Note: This only validates the format, actual OAuth requires user interaction.
    """
    if not client_id or not client_secret:
        return {"success": False, "message": "Client ID和Client Secret不能为空"}

    # 验证格式
    if not client_id.startswith("Iv") and not client_id.startswith("Ov"):
        # GitHub OAuth App Client ID通常以Iv1.开头
        pass  # 不严格限制格式

    if len(client_secret) < 20:
        return {"success": False, "message": "Client Secret长度不正确"}

    # 尝试访问GitHub API验证
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com/",
                headers={"Accept": "application/vnd.github.v3+json"},
                timeout=10.0
            )
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "GitHub API可访问，凭证格式正确。实际验证需要完成OAuth流程。"
                }
            else:
                return {"success": False, "message": f"GitHub API返回: {response.status_code}"}
    except Exception as e:
        return {"success": False, "message": f"无法连接GitHub API: {str(e)}"}


async def test_openai_connection(api_key: str) -> Dict[str, Any]:
    """
    Test OpenAI API key.
    """
    if not api_key:
        return {"success": False, "message": "API Key不能为空"}

    if not api_key.startswith("sk-"):
        return {"success": False, "message": "API Key格式不正确，应以sk-开头"}

    try:
        client = OpenAI(api_key=api_key)
        # 使用简单的模型列表API测试连接
        models = client.models.list()
        model_count = len(list(models))
        return {
            "success": True,
            "message": f"连接成功，可用模型数: {model_count}"
        }
    except Exception as e:
        error_msg = str(e)
        if "invalid_api_key" in error_msg.lower():
            return {"success": False, "message": "API Key无效"}
        elif "rate_limit" in error_msg.lower():
            return {"success": True, "message": "API Key有效（触发速率限制）"}
        else:
            return {"success": False, "message": f"连接失败: {error_msg}"}


async def test_llm_provider_connection(
    provider: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Test LLM provider connection.

    Args:
        provider: Provider name (openai, siliconflow, qwen, zhipu, local)
        api_key: API key for the provider
        base_url: Base URL for the provider API
        model: Model name to test

    Returns:
        Test result with success status and message
    """
    if not api_key and provider != "local":
        return {"success": False, "message": "API Key不能为空"}

    try:
        # 根据提供商配置客户端
        if provider == "local":
            client = OpenAI(
                base_url=base_url or "http://localhost:8000/v1",
                api_key="not-needed"
            )
        else:
            client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )

        # 测试连接 - 使用模型列表API
        models = client.models.list()
        model_count = len(list(models))

        return {
            "success": True,
            "message": f"{provider} 连接成功，可用模型数: {model_count}"
        }
    except Exception as e:
        error_msg = str(e)
        return {
            "success": False,
            "message": f"{provider} 连接失败: {error_msg}"
        }
