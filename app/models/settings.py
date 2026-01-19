"""
System settings model for database.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Float
from sqlalchemy.orm import relationship

from app.core.database import Base


class SystemSettings(Base):
    """System settings database model for storing configuration."""

    __tablename__ = "system_settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, index=True, nullable=False)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), default="string")  # string, int, float, bool, json
    description = Column(Text, nullable=True)
    is_sensitive = Column(Boolean, default=False)  # 敏感信息标记
    category = Column(String(100), nullable=True)  # github, openai, jwt, etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SystemSettings(key={self.key})>"


# 默认设置定义
DEFAULT_SETTINGS = [
    # GitHub OAuth
    {
        "key": "github_client_id",
        "value": "",
        "value_type": "string",
        "description": "GitHub OAuth App Client ID",
        "is_sensitive": False,
        "category": "github"
    },
    {
        "key": "github_client_secret",
        "value": "",
        "value_type": "string",
        "description": "GitHub OAuth App Client Secret",
        "is_sensitive": True,
        "category": "github"
    },
    {
        "key": "github_redirect_uri",
        "value": "http://localhost:8080/api/v1/github/callback",
        "value_type": "string",
        "description": "GitHub OAuth回调URL",
        "is_sensitive": False,
        "category": "github"
    },
    {
        "key": "github_scopes",
        "value": "repo,user",
        "value_type": "string",
        "description": "GitHub授权范围",
        "is_sensitive": False,
        "category": "github"
    },

    # OpenAI
    {
        "key": "openai_api_key",
        "value": "",
        "value_type": "string",
        "description": "OpenAI API密钥",
        "is_sensitive": True,
        "category": "openai"
    },
    {
        "key": "openai_model",
        "value": "gpt-4o",
        "value_type": "string",
        "description": "OpenAI模型名称",
        "is_sensitive": False,
        "category": "openai"
    },
    {
        "key": "openai_max_tokens",
        "value": "4096",
        "value_type": "int",
        "description": "OpenAI最大Token数",
        "is_sensitive": False,
        "category": "openai"
    },
    {
        "key": "openai_temperature",
        "value": "0.7",
        "value_type": "float",
        "description": "OpenAI Temperature参数",
        "is_sensitive": False,
        "category": "openai"
    },

    # Local LLM
    {
        "key": "local_llm_enabled",
        "value": "false",
        "value_type": "bool",
        "description": "是否启用本地LLM",
        "is_sensitive": False,
        "category": "local_llm"
    },
    {
        "key": "local_llm_url",
        "value": "",
        "value_type": "string",
        "description": "本地LLM服务地址",
        "is_sensitive": False,
        "category": "local_llm"
    },
    {
        "key": "local_llm_model",
        "value": "",
        "value_type": "string",
        "description": "本地LLM模型名称",
        "is_sensitive": False,
        "category": "local_llm"
    },

    # JWT
    {
        "key": "jwt_secret_key",
        "value": "change-this-in-production",
        "value_type": "string",
        "description": "JWT签名密钥",
        "is_sensitive": True,
        "category": "jwt"
    },
    {
        "key": "jwt_algorithm",
        "value": "HS256",
        "value_type": "string",
        "description": "JWT加密算法",
        "is_sensitive": False,
        "category": "jwt"
    },
    {
        "key": "jwt_expire_minutes",
        "value": "1440",
        "value_type": "int",
        "description": "JWT过期时间（分钟）",
        "is_sensitive": False,
        "category": "jwt"
    },
]
