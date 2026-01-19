"""
LLM API routes.
Handles AI-powered code operations.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.llm_service import llm_service

router = APIRouter(prefix="/llm", tags=["LLM"])


# Request/Response Models
class GenerateCodeRequest(BaseModel):
    """Generate code request model."""
    requirements: str
    language: str = "python"
    context: Optional[str] = None
    use_local: bool = False


class ModifyCodeRequest(BaseModel):
    """Modify code request model."""
    original_code: str
    requirements: str
    language: str = "python"
    context: Optional[str] = None
    use_local: bool = False


class ReviewCodeRequest(BaseModel):
    """Review code request model."""
    code: str
    language: str = "python"
    use_local: bool = False


class FixBugRequest(BaseModel):
    """Fix bug request model."""
    code: str
    error_description: str
    language: str = "python"
    stack_trace: Optional[str] = None
    use_local: bool = False


class GenerateDocsRequest(BaseModel):
    """Generate documentation request model."""
    code: str
    language: str = "python"
    use_local: bool = False


class GeneratePRDescRequest(BaseModel):
    """Generate PR description request model."""
    changed_files: List[str]
    commit_messages: List[str]
    use_local: bool = False


class GenerateCommitMsgRequest(BaseModel):
    """Generate commit message request model."""
    changed_files: List[str]
    diff_summary: str
    use_local: bool = False


class ChatMessage(BaseModel):
    """Chat message model."""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model."""
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None
    use_local: bool = False


# Routes
@router.post("/generate")
async def generate_code(request: GenerateCodeRequest):
    """
    Generate code based on requirements.

    Uses LLM to generate production-ready code.
    """
    result = llm_service.generate_code(
        requirements=request.requirements,
        language=request.language,
        context=request.context,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Code generation failed"))

    return result


@router.post("/modify")
async def modify_code(request: ModifyCodeRequest):
    """
    Modify existing code based on requirements.

    Uses LLM to apply changes while maintaining code quality.
    """
    result = llm_service.modify_code(
        original_code=request.original_code,
        requirements=request.requirements,
        language=request.language,
        context=request.context,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Code modification failed"))

    return result


@router.post("/review")
async def review_code(request: ReviewCodeRequest):
    """
    Review code and provide feedback.

    Returns issues, suggestions, and positive aspects.
    """
    result = llm_service.review_code(
        code=request.code,
        language=request.language,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Code review failed"))

    return result


@router.post("/fix")
async def fix_bug(request: FixBugRequest):
    """
    Fix bugs in code.

    Analyzes error and provides fixed code with explanation.
    """
    result = llm_service.fix_bug(
        code=request.code,
        error_description=request.error_description,
        language=request.language,
        stack_trace=request.stack_trace,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Bug fix failed"))

    return result


@router.post("/docs")
async def generate_documentation(request: GenerateDocsRequest):
    """
    Generate documentation for code.

    Creates comprehensive documentation including docstrings.
    """
    result = llm_service.generate_documentation(
        code=request.code,
        language=request.language,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Documentation generation failed"))

    return result


@router.post("/pr-description")
async def generate_pr_description(request: GeneratePRDescRequest):
    """
    Generate PR description from changes.

    Creates professional PR summary with test instructions.
    """
    result = llm_service.generate_pr_description(
        changed_files=request.changed_files,
        commit_messages=request.commit_messages,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "PR description generation failed"))

    return result


@router.post("/commit-message")
async def generate_commit_message(request: GenerateCommitMsgRequest):
    """
    Generate commit message from changes.

    Creates conventional commit format message.
    """
    result = llm_service.generate_commit_message(
        changed_files=request.changed_files,
        diff_summary=request.diff_summary,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Commit message generation failed"))

    return result


@router.post("/chat")
async def chat(request: ChatRequest):
    """
    General chat with LLM.

    Supports multi-turn conversation with custom system prompt.
    """
    messages = [{"role": m.role, "content": m.content} for m in request.messages]

    result = await llm_service.chat(
        messages=messages,
        system_prompt=request.system_prompt,
        use_local=request.use_local
    )

    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result.get("message", "Chat failed"))

    return result
