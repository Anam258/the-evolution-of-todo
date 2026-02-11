"""
Task API endpoints — contract: /api/v1/{user_id}/tasks

Every endpoint validates that the {user_id} in the URL matches the
user_id extracted from the JWT by the JWTAuthMiddleware.  This gives
us defence-in-depth: the middleware rejects unauthenticated requests,
and the route rejects cross-user access.

Note: These routes are mounted with prefix="/api/v1" in main.py,
so /{user_id}/tasks becomes /api/v1/{user_id}/tasks.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session
from typing import List

from ..database import get_session
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskPatch
from ..middleware.auth_middleware import get_current_user_id
from ..services.user_isolation_service import user_isolation_service

router = APIRouter(tags=["tasks"])


def _enforce_ownership(url_user_id: int, jwt_user_id: int) -> None:
    """Reject if the URL user_id doesn't match the JWT user_id."""
    if url_user_id != jwt_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID mismatch",
        )


# ── LIST ──────────────────────────────────────────────────────────────────

@router.get("/{user_id}/tasks", response_model=List[TaskRead])
def list_tasks(
    user_id: int,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)
    return user_isolation_service.get_user_owned_resources(db, Task, uid)


# ── CREATE ────────────────────────────────────────────────────────────────

@router.post("/{user_id}/tasks", response_model=TaskRead, status_code=201)
def create_task(
    user_id: int,
    body: TaskCreate,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)

    task = Task(
        title=body.title,
        description=body.description,
        is_completed=body.is_completed,
        user_id=uid,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# ── READ ONE ──────────────────────────────────────────────────────────────

@router.get("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    user_id: int,
    task_id: int,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)

    task = user_isolation_service.get_single_user_resource(db, Task, task_id, uid)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# ── UPDATE (full) ─────────────────────────────────────────────────────────

@router.put("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: int,
    task_id: int,
    body: TaskUpdate,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)

    updates = {k: v for k, v in body.dict(exclude_unset=True).items() if v is not None}
    if not user_isolation_service.update_user_resource(db, Task, task_id, uid, updates):
        raise HTTPException(status_code=404, detail="Task not found")

    return user_isolation_service.get_single_user_resource(db, Task, task_id, uid)


# ── PATCH (status toggle) ────────────────────────────────────────────────

@router.patch("/{user_id}/tasks/{task_id}", response_model=TaskRead)
def patch_task(
    user_id: int,
    task_id: int,
    body: TaskPatch,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)

    if not user_isolation_service.update_user_resource(
        db, Task, task_id, uid, {"is_completed": body.is_completed}
    ):
        raise HTTPException(status_code=404, detail="Task not found")

    return user_isolation_service.get_single_user_resource(db, Task, task_id, uid)


# ── DELETE ────────────────────────────────────────────────────────────────

@router.delete("/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: int,
    task_id: int,
    request: Request,
    db: Session = Depends(get_session),
):
    uid = get_current_user_id(request)
    _enforce_ownership(user_id, uid)

    if not user_isolation_service.delete_user_resource(db, Task, task_id, uid):
        raise HTTPException(status_code=404, detail="Task not found")

    return {"message": "Task deleted successfully"}
