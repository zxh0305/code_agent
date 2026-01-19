"""
Code analysis API routes.
Handles code parsing and analysis operations.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.code_analysis_service import code_analysis_service

router = APIRouter(prefix="/code", tags=["Code Analysis"])


# Request/Response Models
class AnalyzeCodeRequest(BaseModel):
    """Analyze code request model."""
    source_code: str
    language: str = "python"


class AnalyzeFileRequest(BaseModel):
    """Analyze file request model."""
    file_path: str


class AnalyzeRepoRequest(BaseModel):
    """Analyze repository request model."""
    repo_path: str
    extensions: Optional[List[str]] = None


class GetContextRequest(BaseModel):
    """Get code context request model."""
    file_path: str
    start_line: int
    end_line: Optional[int] = None
    context_lines: int = 5


# Routes
@router.post("/analyze")
async def analyze_code(request: AnalyzeCodeRequest):
    """
    Analyze source code and extract structure.

    Returns AST structure, classes, functions, and metrics.
    """
    if request.language != "python":
        raise HTTPException(
            status_code=400,
            detail=f"Language '{request.language}' not yet supported"
        )

    result = code_analysis_service.analyze_python_code(request.source_code)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Analysis failed"))

    return result


@router.post("/analyze/file")
async def analyze_file(request: AnalyzeFileRequest):
    """
    Analyze a source code file.

    Returns AST structure and code metrics.
    """
    language = code_analysis_service.detect_language(request.file_path)

    if language != "python":
        raise HTTPException(
            status_code=400,
            detail=f"Language '{language or 'unknown'}' not yet supported"
        )

    result = code_analysis_service.analyze_python_file(request.file_path)

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result.get("message", "Analysis failed"))

    return result


@router.post("/analyze/repository")
async def analyze_repository(request: AnalyzeRepoRequest):
    """
    Analyze all code files in a repository.

    Returns analysis for all supported files.
    """
    result = code_analysis_service.analyze_repository(
        repo_path=request.repo_path,
        extensions=request.extensions
    )
    return {"status": "success", **result}


@router.post("/context")
async def get_code_context(request: GetContextRequest):
    """
    Get code context around specific lines.

    Useful for providing context to LLM for code modifications.
    """
    result = code_analysis_service.get_code_context(
        file_path=request.file_path,
        start_line=request.start_line,
        end_line=request.end_line,
        context_lines=request.context_lines
    )

    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result.get("message", "Context retrieval failed"))

    return result


@router.get("/language")
async def detect_language(file_path: str = Query(...)):
    """
    Detect programming language from file path.
    """
    language = code_analysis_service.detect_language(file_path)
    return {
        "status": "success",
        "file_path": file_path,
        "language": language
    }
