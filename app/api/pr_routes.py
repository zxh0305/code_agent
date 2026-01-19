"""
Pull Request API routes.
Handles PR creation, updates, and management.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.pr_service import pr_service

router = APIRouter(prefix="/pr", tags=["Pull Requests"])


# Request/Response Models
class CreatePRRequest(BaseModel):
    """Create PR request model."""
    repo_owner: str
    repo_name: str
    title: str
    body: str
    head_branch: str
    base_branch: str = "main"
    draft: bool = False
    reviewers: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    issue_number: Optional[int] = None


class UpdatePRRequest(BaseModel):
    """Update PR request model."""
    repo_owner: str
    repo_name: str
    pr_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None
    base_branch: Optional[str] = None


class MergePRRequest(BaseModel):
    """Merge PR request model."""
    repo_owner: str
    repo_name: str
    pr_number: int
    commit_title: Optional[str] = None
    commit_message: Optional[str] = None
    merge_method: str = "merge"


class AddCommentRequest(BaseModel):
    """Add comment request model."""
    repo_owner: str
    repo_name: str
    pr_number: int
    body: str


class CreateReviewRequest(BaseModel):
    """Create review request model."""
    repo_owner: str
    repo_name: str
    pr_number: int
    body: str
    event: str = "COMMENT"
    comments: Optional[List[dict]] = None


# Routes
@router.post("/create")
async def create_pull_request(
    request: CreatePRRequest,
    access_token: str = Query(...)
):
    """
    Create a new Pull Request.

    Creates PR with specified title, body, and branches.
    Optionally assigns reviewers and labels.
    """
    result = pr_service.create_pull_request(
        access_token=access_token,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        title=request.title,
        body=request.body,
        head_branch=request.head_branch,
        base_branch=request.base_branch,
        draft=request.draft,
        reviewers=request.reviewers,
        labels=request.labels,
        issue_number=request.issue_number
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "PR creation failed")
        )

    return result


@router.get("/{owner}/{repo}/{pr_number}")
async def get_pull_request(
    owner: str,
    repo: str,
    pr_number: int,
    access_token: str = Query(...)
):
    """Get Pull Request details."""
    result = pr_service.get_pull_request(
        access_token=access_token,
        repo_owner=owner,
        repo_name=repo,
        pr_number=pr_number
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to get PR")
        )

    return result


@router.get("/{owner}/{repo}")
async def list_pull_requests(
    owner: str,
    repo: str,
    access_token: str = Query(...),
    state: str = Query("open"),
    sort: str = Query("created"),
    direction: str = Query("desc"),
    base: Optional[str] = Query(None),
    head: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(30, ge=1, le=100)
):
    """List Pull Requests in a repository."""
    result = pr_service.list_pull_requests(
        access_token=access_token,
        repo_owner=owner,
        repo_name=repo,
        state=state,
        sort=sort,
        direction=direction,
        base_branch=base,
        head_branch=head,
        page=page,
        per_page=per_page
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to list PRs")
        )

    return result


@router.put("/update")
async def update_pull_request(
    request: UpdatePRRequest,
    access_token: str = Query(...)
):
    """Update a Pull Request."""
    result = pr_service.update_pull_request(
        access_token=access_token,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        pr_number=request.pr_number,
        title=request.title,
        body=request.body,
        state=request.state,
        base_branch=request.base_branch
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to update PR")
        )

    return result


@router.post("/merge")
async def merge_pull_request(
    request: MergePRRequest,
    access_token: str = Query(...)
):
    """Merge a Pull Request."""
    result = pr_service.merge_pull_request(
        access_token=access_token,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        pr_number=request.pr_number,
        commit_title=request.commit_title,
        commit_message=request.commit_message,
        merge_method=request.merge_method
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to merge PR")
        )

    return result


@router.post("/comment")
async def add_comment(
    request: AddCommentRequest,
    access_token: str = Query(...)
):
    """Add a comment to a Pull Request."""
    result = pr_service.add_comment(
        access_token=access_token,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        pr_number=request.pr_number,
        body=request.body
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to add comment")
        )

    return result


@router.get("/{owner}/{repo}/{pr_number}/files")
async def get_pr_files(
    owner: str,
    repo: str,
    pr_number: int,
    access_token: str = Query(...)
):
    """Get files changed in a Pull Request."""
    result = pr_service.get_pr_files(
        access_token=access_token,
        repo_owner=owner,
        repo_name=repo,
        pr_number=pr_number
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to get PR files")
        )

    return result


@router.post("/review")
async def create_review(
    request: CreateReviewRequest,
    access_token: str = Query(...)
):
    """Create a review on a Pull Request."""
    result = pr_service.create_review(
        access_token=access_token,
        repo_owner=request.repo_owner,
        repo_name=request.repo_name,
        pr_number=request.pr_number,
        body=request.body,
        event=request.event,
        comments=request.comments
    )

    if result["status"] == "error":
        raise HTTPException(
            status_code=result.get("error_code", 400),
            detail=result.get("message", "Failed to create review")
        )

    return result
