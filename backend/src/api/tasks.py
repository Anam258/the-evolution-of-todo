"""
Task API endpoints for the Nuralyx Flow application.

Implements CRUD operations for tasks with user isolation using UserIsolationService.
All endpoints require authentication and enforce user isolation.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from typing import List

from ..database import get_session
from ..models.task import Task, TaskCreate, TaskRead, TaskUpdate, TaskPatch
from ..middleware.auth_middleware import require_authenticated_user
from ..services.user_isolation_service import user_isolation_service

router = APIRouter(prefix="", tags=["tasks"])  # Changed prefix to allow full path control


@router.get("/api/{user_id}/tasks", response_model=List[TaskRead])
def get_tasks(
    user_id: int,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Retrieve all tasks for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        List of tasks owned by the authenticated user
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    tasks = user_isolation_service.get_user_owned_resources(
        db_session, Task, current_user_id
    )
    return tasks


@router.post("/api/{user_id}/tasks", response_model=TaskRead)
def create_task(
    user_id: int,
    task_data: TaskCreate,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Create a new task for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        task_data: Task creation data
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        Created task with assigned ID
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    # Create the task with the authenticated user's ID
    db_task = Task(
        title=task_data.title,
        description=task_data.description,
        is_completed=task_data.is_completed,
        user_id=current_user_id
    )

    db_session.add(db_task)
    db_session.commit()
    db_session.refresh(db_task)

    return db_task


@router.get("/api/{user_id}/tasks/{task_id}", response_model=TaskRead)
def get_task(
    user_id: int,
    task_id: int,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Retrieve a specific task for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        task_id: ID of the task to retrieve
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        Task if it exists and is owned by the user

    Raises:
        HTTPException: 404 if task doesn't exist or isn't owned by user
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    task = user_isolation_service.get_single_user_resource(
        db_session, Task, task_id, current_user_id
    )

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/api/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task(
    user_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Update a specific task for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        task_id: ID of the task to update
        task_data: Task update data
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        Updated task

    Raises:
        HTTPException: 404 if task doesn't exist or isn't owned by user
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    # Prepare update data excluding None values
    update_data = {}
    if task_data.title is not None:
        update_data["title"] = task_data.title
    if task_data.description is not None:
        update_data["description"] = task_data.description
    if task_data.is_completed is not None:
        update_data["is_completed"] = task_data.is_completed

    # Use UserIsolationService to update the task
    success = user_isolation_service.update_user_resource(
        db_session, Task, task_id, current_user_id, update_data
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Retrieve and return the updated task
    updated_task = user_isolation_service.get_single_user_resource(
        db_session, Task, task_id, current_user_id
    )

    return updated_task


@router.patch("/api/{user_id}/tasks/{task_id}", response_model=TaskRead)
def update_task_status(
    user_id: int,
    task_id: int,
    task_data: TaskPatch,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Update task completion status for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        task_id: ID of the task to update
        task_data: Task status update data (is_completed)
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        Updated task with new status

    Raises:
        HTTPException: 404 if task doesn't exist or isn't owned by user
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    # Prepare update data
    update_data = {"is_completed": task_data.is_completed}

    # Use UserIsolationService to update the task
    success = user_isolation_service.update_user_resource(
        db_session, Task, task_id, current_user_id, update_data
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Retrieve and return the updated task
    updated_task = user_isolation_service.get_single_user_resource(
        db_session, Task, task_id, current_user_id
    )

    return updated_task


@router.delete("/api/{user_id}/tasks/{task_id}")
def delete_task(
    user_id: int,
    task_id: int,
    current_user_id: int = Depends(require_authenticated_user()),
    db_session: Session = Depends(get_session)
):
    """
    Delete a specific task for the authenticated user.

    Args:
        user_id: ID of the user in the URL path
        task_id: ID of the task to delete
        current_user_id: ID of the authenticated user (extracted from JWT)
        db_session: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if task doesn't exist or isn't owned by user
    """
    # Validate that the user_id in the URL matches the user_id from the JWT token
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: user ID in URL does not match authenticated user"
        )

    success = user_isolation_service.delete_user_resource(
        db_session, Task, task_id, current_user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task deleted successfully"}