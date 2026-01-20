"""
Task API routes.
Handles task CRUD operations for code development tasks.
"""

from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.task import Task

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Request/Response Models
class TaskCreate(BaseModel):
    """Create task request."""
    name: Optional[str] = "新建任务"
    description: Optional[str] = None
    repository: Optional[str] = None
    branch: Optional[str] = None
    requirement: Optional[str] = None
    language: Optional[str] = None


class TaskUpdate(BaseModel):
    """Update task request."""
    name: Optional[str] = None
    description: Optional[str] = None
    repository: Optional[str] = None
    branch: Optional[str] = None
    requirement: Optional[str] = None
    generated_code: Optional[str] = None
    language: Optional[str] = None
    status: Optional[str] = None
    is_archived: Optional[bool] = None
    metadata: Optional[dict] = None


class TaskResponse(BaseModel):
    """Task response model."""
    id: int
    name: str
    description: Optional[str]
    repository: Optional[str]
    branch: Optional[str]
    requirement: Optional[str]
    generated_code: Optional[str]
    language: Optional[str]
    status: str
    is_archived: bool
    metadata: Optional[dict]
    created_at: Optional[str]
    updated_at: Optional[str]

    class Config:
        from_attributes = True


# Routes
@router.post("", response_model=TaskResponse)
async def create_task(
    request: TaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new task."""
    task = Task(
        name=request.name or "新建任务",
        description=request.description,
        repository=request.repository,
        branch=request.branch,
        requirement=request.requirement,
        language=request.language,
        status="draft"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskResponse(**task.to_dict())


@router.get("", response_model=List[TaskResponse])
async def list_tasks(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    is_archived: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    """List all tasks with pagination."""
    query = select(Task).where(Task.is_archived == is_archived)

    if status:
        query = query.where(Task.status == status)

    query = query.order_by(Task.updated_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    tasks = result.scalars().all()

    return [TaskResponse(**task.to_dict()) for task in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(**task.to_dict())


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    request: TaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update fields
    update_data = request.dict(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return TaskResponse(**task.to_dict())


@router.patch("/{task_id}/rename")
async def rename_task(
    task_id: int,
    name: str = Query(..., min_length=1, max_length=255),
    db: AsyncSession = Depends(get_db)
):
    """Rename a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.name = name
    await db.commit()
    await db.refresh(task)
    return {"status": "success", "name": task.name}


@router.patch("/{task_id}/archive")
async def archive_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Archive a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_archived = True
    await db.commit()
    return {"status": "success", "message": "Task archived"}


@router.patch("/{task_id}/unarchive")
async def unarchive_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Unarchive a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.is_archived = False
    await db.commit()
    return {"status": "success", "message": "Task unarchived"}


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a task."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"status": "success", "message": "Task deleted"}
