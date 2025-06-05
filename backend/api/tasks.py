"""
Tasks API endpoints for task management and delegation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import asyncio
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, and_, or_
from sqlalchemy.orm import selectinload

from backend.database.models import Task, Director, User, BoardSession
from backend.database.connection import get_async_db
from backend.auth.security import get_current_active_user, get_current_superuser
from backend.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskWithDetails,
    TaskExecute,
    TaskResult
)
from backend.schemas.common import PaginatedResponse, MessageResponse, TaskStatus
from backend.services.task_processor import TaskProcessor
from backend.utils.privacy_shield import privacy_shield

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_director_id: Optional[str] = None,
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List tasks with pagination and filters"""
    # Build query
    query = select(Task).options(
        selectinload(Task.assigned_director),
        selectinload(Task.user),
        selectinload(Task.session)
    )
    count_query = select(func.count()).select_from(Task)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
        count_query = count_query.where(Task.user_id == current_user.id)
    
    # Apply filters
    if status:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    
    if priority:
        query = query.where(Task.priority == priority)
        count_query = count_query.where(Task.priority == priority)
    
    if assigned_director_id:
        query = query.where(Task.assigned_director_id == assigned_director_id)
        count_query = count_query.where(Task.assigned_director_id == assigned_director_id)
    
    if session_id:
        query = query.where(Task.session_id == session_id)
        count_query = count_query.where(Task.session_id == session_id)
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination and ordering
    offset = (page - 1) * page_size
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    tasks = result.scalars().all()
    
    # Convert to response models
    task_responses = [TaskWithDetails.from_orm(t) for t in tasks]
    
    return PaginatedResponse.create(
        data=task_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{task_id}", response_model=TaskWithDetails)
async def get_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific task by ID"""
    query = select(Task).options(
        selectinload(Task.assigned_director),
        selectinload(Task.user),
        selectinload(Task.session)
    ).where(Task.id == task_id)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return TaskWithDetails.from_orm(task)


@router.post("/", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new task"""
    # Create or get session
    session = None
    if task_data.session_id:
        result = await db.execute(
            select(BoardSession).where(
                BoardSession.id == task_data.session_id,
                BoardSession.user_id == current_user.id
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
    
    # Create task
    task = Task(
        title=task_data.title,
        description=task_data.description,
        requirements=task_data.requirements,
        deliverables=task_data.deliverables,
        priority=task_data.priority,
        user_id=current_user.id,
        session_id=session.id if session else None
    )
    
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Queue for processing if auto_execute is True
    if task_data.auto_execute:
        background_tasks.add_task(
            process_task_background,
            task_id=str(task.id),
            db_manager=db.get_bind()
        )
    
    logger.info(f"Task {task.id} created by user {current_user.username}")
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a task"""
    query = select(Task).where(Task.id == task_id)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if task can be updated
    if task.status in ["in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update task in {task.status} status"
        )
    
    # Update fields
    update_data = task_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await db.commit()
    await db.refresh(task)
    
    logger.info(f"Task {task.id} updated by user {current_user.username}")
    
    return task


@router.delete("/{task_id}", response_model=MessageResponse)
async def delete_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a task"""
    query = select(Task).where(Task.id == task_id)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if task can be deleted
    if task.status == "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete task in progress"
        )
    
    await db.delete(task)
    await db.commit()
    
    logger.info(f"Task {task.id} deleted by user {current_user.username}")
    
    return {"message": f"Task {task.id} deleted successfully"}


@router.post("/{task_id}/execute", response_model=TaskResult)
async def execute_task(
    task_id: str,
    execute_data: Optional[TaskExecute] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Execute a task immediately"""
    query = select(Task).options(
        selectinload(Task.assigned_director),
        selectinload(Task.session)
    ).where(Task.id == task_id)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if task can be executed
    if task.status in ["in_progress", "completed"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Task is already {task.status}"
        )
    
    # Select director if not assigned
    director = task.assigned_director
    if not director and execute_data and execute_data.director_id:
        director_result = await db.execute(
            select(Director).where(
                Director.id == execute_data.director_id,
                Director.is_available == True
            )
        )
        director = director_result.scalar_one_or_none()
        
        if not director:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Director not found or unavailable"
            )
    
    # Use task processor to execute
    processor = TaskProcessor(db)
    
    try:
        # Update task status
        task.status = "in_progress"
        task.started_at = datetime.utcnow()
        if director:
            task.assigned_director_id = director.id
        await db.commit()
        
        # Execute task
        result = await processor.execute_task(task, director)
        
        # Update task with result
        task.status = "completed" if result["success"] else "failed"
        task.completed_at = datetime.utcnow()
        task.execution_time = (task.completed_at - task.started_at).total_seconds()
        task.result = result
        task.quality_score = result.get("quality", 0.0)
        
        if not result["success"]:
            task.error_message = result.get("error", "Unknown error")
        
        await db.commit()
        await db.refresh(task)
        
        logger.info(f"Task {task.id} executed with status {task.status}")
        
        return TaskResult(
            task_id=task.id,
            status=task.status,
            result=result,
            execution_time=task.execution_time,
            quality_score=task.quality_score,
            error_message=task.error_message
        )
        
    except Exception as e:
        # Update task as failed
        task.status = "failed"
        task.completed_at = datetime.utcnow()
        task.error_message = str(e)
        await db.commit()
        
        logger.error(f"Task {task.id} execution failed: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Task execution failed: {str(e)}"
        )


@router.post("/{task_id}/cancel", response_model=MessageResponse)
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Cancel a task"""
    query = select(Task).where(Task.id == task_id)
    
    # Filter by user if not superuser
    if not current_user.is_superuser:
        query = query.where(Task.user_id == current_user.id)
    
    result = await db.execute(query)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check if task can be cancelled
    if task.status not in ["pending", "in_progress"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task in {task.status} status"
        )
    
    # Cancel task
    task.status = "cancelled"
    task.completed_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info(f"Task {task.id} cancelled by user {current_user.username}")
    
    return {"message": f"Task {task.id} cancelled successfully"}


@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_task_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get task statistics summary"""
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Base query filter
    base_filter = [Task.created_at >= from_date]
    if not current_user.is_superuser:
        base_filter.append(Task.user_id == current_user.id)
    
    # Total tasks
    total_result = await db.execute(
        select(func.count()).select_from(Task).where(*base_filter)
    )
    total_tasks = total_result.scalar()
    
    # Tasks by status
    status_result = await db.execute(
        select(Task.status, func.count()).where(*base_filter).group_by(Task.status)
    )
    tasks_by_status = {status: count for status, count in status_result}
    
    # Tasks by priority
    priority_result = await db.execute(
        select(Task.priority, func.count()).where(*base_filter).group_by(Task.priority)
    )
    tasks_by_priority = {priority: count for priority, count in priority_result}
    
    # Average execution time
    exec_time_result = await db.execute(
        select(func.avg(Task.execution_time)).where(
            *base_filter,
            Task.status == "completed",
            Task.execution_time.isnot(None)
        )
    )
    avg_execution_time = exec_time_result.scalar() or 0.0
    
    # Average quality score
    quality_result = await db.execute(
        select(func.avg(Task.quality_score)).where(
            *base_filter,
            Task.status == "completed",
            Task.quality_score.isnot(None)
        )
    )
    avg_quality_score = quality_result.scalar() or 0.0
    
    # Success rate
    completed = tasks_by_status.get("completed", 0)
    failed = tasks_by_status.get("failed", 0)
    success_rate = completed / (completed + failed) if (completed + failed) > 0 else 0.0
    
    return {
        "period_days": days,
        "total_tasks": total_tasks,
        "tasks_by_status": tasks_by_status,
        "tasks_by_priority": tasks_by_priority,
        "average_execution_time": avg_execution_time,
        "average_quality_score": avg_quality_score,
        "success_rate": success_rate,
        "from_date": from_date.isoformat(),
        "to_date": datetime.utcnow().isoformat()
    }


async def process_task_background(task_id: str, db_manager):
    """Background task processor"""
    # This would be implemented to process tasks asynchronously
    logger.info(f"Processing task {task_id} in background")


from datetime import timedelta  # Add this import