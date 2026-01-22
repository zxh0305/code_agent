"""
GitHub API routes.
Handles GitHub OAuth and repository operations.
"""

from typing import List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from github import GithubException
from pydantic import BaseModel

from app.services.github_service import github_service
from app.core.config import settings

router = APIRouter(prefix="/github", tags=["GitHub"])


# Request/Response Models
class AuthURLResponse(BaseModel):
    """Auth URL response model."""
    auth_url: str
    state: str


class TokenRequest(BaseModel):
    """Token exchange request model."""
    code: str
    state: str


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str
    scope: str


class RepositoryResponse(BaseModel):
    """Repository response model."""
    id: int
    name: str
    full_name: str
    description: Optional[str]
    html_url: str
    clone_url: str
    default_branch: str
    private: bool
    language: Optional[str]
    stargazers_count: int
    forks_count: int


class CloneRequest(BaseModel):
    """Clone repository request model."""
    repo_url: str
    local_path: str
    branch: Optional[str] = None


class BranchRequest(BaseModel):
    """Create branch request model."""
    local_path: str
    branch_name: str
    base_branch: Optional[str] = None


class CommitRequest(BaseModel):
    """Commit changes request model."""
    local_path: str
    message: str
    files: Optional[List[str]] = None


class PushRequest(BaseModel):
    """Push changes request model."""
    local_path: str
    branch: Optional[str] = None
    force: bool = False


class FileReadRequest(BaseModel):
    """File read request model."""
    local_path: str
    file_path: str


class FileWriteRequest(BaseModel):
    """File write request model."""
    local_path: str
    file_path: str
    content: str


# Routes
@router.get("/auth", response_model=AuthURLResponse)
async def get_auth_url():
    """
    Generate GitHub OAuth authorization URL.

    Returns the URL and state for OAuth flow.
    """
    result = await github_service.generate_auth_url()
    return AuthURLResponse(**result)


@router.get("/callback")
async def github_callback(
    code: str = Query(...),
    state: str = Query(...)
):
    """
    Handle GitHub OAuth callback.

    Exchanges authorization code for access token and redirects to frontend.
    """
    try:
        token_data = await github_service.exchange_code_for_token(code, state)
        access_token = token_data.get("access_token")

        # Redirect to frontend callback page with token
        redirect_url = f"{settings.FRONTEND_URL}/github/callback?token={access_token}"

        return RedirectResponse(url=redirect_url, status_code=302)
    except ValueError as e:
        # On error, redirect to frontend with error message
        error_url = f"{settings.FRONTEND_URL}/github/callback?error={str(e)}"
        return RedirectResponse(url=error_url, status_code=302)
    except Exception as e:
        error_url = f"{settings.FRONTEND_URL}/github/callback?error={str(e)}"
        return RedirectResponse(url=error_url, status_code=302)


@router.post("/token", response_model=TokenResponse)
async def exchange_token(request: TokenRequest):
    """
    Exchange authorization code for access token.

    Alternative to callback for SPA applications.
    """
    try:
        token_data = await github_service.exchange_code_for_token(
            request.code,
            request.state
        )
        return TokenResponse(
            access_token=token_data["access_token"],
            token_type=token_data.get("token_type", "bearer"),
            scope=token_data.get("scope", "")
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/user")
async def get_user_info(access_token: str = Query(...)):
    """Get authenticated user's GitHub information."""
    try:
        user_info = await github_service.get_user_info(access_token)
        return {"status": "success", "user": user_info}
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Invalid or expired access token")
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")


@router.get("/repos")
async def list_repositories(
    access_token: str = Query(...),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100),
    sort: str = Query("updated"),
    direction: str = Query("desc")
):
    """List user's GitHub repositories."""
    try:
        repos = await github_service.list_user_repositories(
            access_token=access_token,
            page=page,
            per_page=per_page,
            sort=sort,
            direction=direction
        )
        return {
            "status": "success",
            "repositories": repos,
            "page": page,
            "per_page": per_page
        }
    except GithubException as e:
        raise HTTPException(status_code=e.status, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list repositories: {str(e)}")


@router.get("/repos/{owner}/{repo}")
async def get_repository(
    owner: str,
    repo: str,
    access_token: str = Query(...)
):
    """Get specific repository information."""
    try:
        repo_info = await github_service.get_repository(access_token, owner, repo)
        return {"status": "success", "repository": repo_info}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repos/{owner}/{repo}/branches")
async def list_branches(
    owner: str,
    repo: str,
    access_token: str = Query(...)
):
    """List branches of a repository."""
    try:
        branches = await github_service.list_branches(access_token, owner, repo)
        return {"status": "success", "branches": branches}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repos/clone")
async def clone_repository(
    request: CloneRequest,
    access_token: str = Query(...)
):
    """Clone a GitHub repository."""
    result = github_service.clone_repository(
        clone_url=request.repo_url,
        local_path=request.local_path,
        access_token=access_token,
        branch=request.branch
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/repos/pull")
async def pull_repository(local_path: str = Query(...)):
    """Pull latest changes from remote."""
    result = github_service.pull_repository(local_path)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/branch/create")
async def create_branch(request: BranchRequest):
    """Create a new branch."""
    result = github_service.create_branch(
        local_path=request.local_path,
        branch_name=request.branch_name,
        base_branch=request.base_branch
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/commit")
async def commit_changes(request: CommitRequest):
    """Commit changes to repository."""
    result = github_service.commit_changes(
        local_path=request.local_path,
        message=request.message,
        files=request.files
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/push")
async def push_changes(request: PushRequest):
    """Push changes to remote."""
    result = github_service.push_changes(
        local_path=request.local_path,
        branch=request.branch,
        force=request.force
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.post("/file/read")
async def read_file(request: FileReadRequest):
    """Read file content from repository."""
    result = github_service.get_file_content(
        local_path=request.local_path,
        file_path=request.file_path
    )
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


@router.post("/file/write")
async def write_file(request: FileWriteRequest):
    """Write content to a file."""
    result = github_service.write_file(
        local_path=request.local_path,
        file_path=request.file_path,
        content=request.content
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@router.get("/files")
async def list_files(
    local_path: str = Query(...),
    path: str = Query(""),
    extensions: Optional[str] = Query(None)
):
    """List files in repository."""
    ext_list = extensions.split(",") if extensions else None
    files = github_service.list_files(
        local_path=local_path,
        path=path,
        extensions=ext_list
    )
    return {"status": "success", "files": files}
