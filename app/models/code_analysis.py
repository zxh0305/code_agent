"""
Code Analysis model for database.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base


class AnalysisStatus(str, Enum):
    """Analysis status enum."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class CodeAnalysis(Base):
    """Code Analysis database model."""

    __tablename__ = "code_analyses"

    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)

    # Analysis info
    file_path = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)

    # Analysis results (JSON)
    ast_structure = Column(JSON, nullable=True)  # AST tree structure
    code_structure = Column(JSON, nullable=True)  # Classes, functions, variables
    dependencies = Column(JSON, nullable=True)  # Import dependencies
    metrics = Column(JSON, nullable=True)  # Code metrics (lines, complexity, etc.)
    issues = Column(JSON, nullable=True)  # Detected issues

    # Error info
    error_message = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    repository = relationship("Repository", back_populates="code_analyses")

    def __repr__(self) -> str:
        return f"<CodeAnalysis(id={self.id}, file_path={self.file_path})>"


class AIInteraction(Base):
    """AI Interaction log database model."""

    __tablename__ = "ai_interactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=True)

    # Interaction details
    model_name = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)

    # Token usage
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)

    # Status
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    error_message = Column(Text, nullable=True)

    # Context
    context_type = Column(String(50), nullable=True)  # code_generation, code_review, etc.
    context_data = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<AIInteraction(id={self.id}, model={self.model_name})>"
