"""
Directors API endpoints for managing AI agents
"""

from typing import List, Optional
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from sqlalchemy.orm import selectinload

from backend.database.models import Director, Task, User
from backend.database.connection import get_async_db
from backend.auth.security import get_current_active_user, get_current_superuser
from backend.schemas.directors import (
    DirectorCreate,
    DirectorUpdate,
    DirectorResponse,
    DirectorWithMetrics,
    DirectorPerformance
)
from backend.schemas.common import PaginatedResponse, MessageResponse
from backend.utils.privacy_shield import privacy_shield

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=PaginatedResponse)
async def list_directors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    is_available: Optional[bool] = None,
    specialty: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """List all directors with pagination and filters"""
    # Build query
    query = select(Director)
    count_query = select(func.count()).select_from(Director)
    
    # Apply filters
    if is_available is not None:
        query = query.where(Director.is_available == is_available)
        count_query = count_query.where(Director.is_available == is_available)
    
    if specialty:
        query = query.where(Director.specialties.contains([specialty]))
        count_query = count_query.where(Director.specialties.contains([specialty]))
    
    # Get total count
    total_result = await db.execute(count_query)
    total = total_result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute query
    result = await db.execute(query)
    directors = result.scalars().all()
    
    # Convert to response models
    director_responses = [DirectorWithMetrics.from_orm(d) for d in directors]
    
    return PaginatedResponse.create(
        data=director_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{director_id}", response_model=DirectorWithMetrics)
async def get_director(
    director_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get a specific director by ID"""
    result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = result.scalar_one_or_none()
    
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Director not found"
        )
    
    return DirectorWithMetrics.from_orm(director)


@router.post("/", response_model=DirectorResponse)
async def create_director(
    director_data: DirectorCreate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """Create a new director (admin only)"""
    # Check if director with same name exists
    result = await db.execute(
        select(Director).where(Director.name == director_data.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Director with this name already exists"
        )
    
    # Validate endpoint
    if not privacy_shield.validate_api_endpoint(director_data.endpoint):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API endpoint not in allowed list"
        )
    
    # Create director
    director = Director(
        name=director_data.name,
        role=director_data.role,
        endpoint=director_data.endpoint,
        api_key_encrypted=director_data.api_key,  # Should be encrypted in production
        specialties=director_data.specialties,
        is_available=director_data.is_available
    )
    
    db.add(director)
    await db.commit()
    await db.refresh(director)
    
    logger.info(f"Director {director.name} created by {current_user.username}")
    
    return director


@router.put("/{director_id}", response_model=DirectorResponse)
async def update_director(
    director_id: str,
    director_data: DirectorUpdate,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """Update a director (admin only)"""
    result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = result.scalar_one_or_none()
    
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Director not found"
        )
    
    # Update fields
    update_data = director_data.dict(exclude_unset=True)
    
    # Validate endpoint if changed
    if "endpoint" in update_data:
        if not privacy_shield.validate_api_endpoint(update_data["endpoint"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="API endpoint not in allowed list"
            )
    
    for field, value in update_data.items():
        setattr(director, field, value)
    
    director.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(director)
    
    logger.info(f"Director {director.name} updated by {current_user.username}")
    
    return director


@router.delete("/{director_id}", response_model=MessageResponse)
async def delete_director(
    director_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """Delete a director (admin only)"""
    result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = result.scalar_one_or_none()
    
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Director not found"
        )
    
    # Check if director has active tasks
    task_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.assigned_director_id == director_id,
            Task.status.in_(["pending", "in_progress"])
        )
    )
    active_tasks = task_result.scalar()
    
    if active_tasks > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete director with {active_tasks} active tasks"
        )
    
    await db.delete(director)
    await db.commit()
    
    logger.info(f"Director {director.name} deleted by {current_user.username}")
    
    return {"message": f"Director {director.name} deleted successfully"}


@router.get("/{director_id}/performance", response_model=DirectorPerformance)
async def get_director_performance(
    director_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_async_db)
):
    """Get detailed performance metrics for a director"""
    result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = result.scalar_one_or_none()
    
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Director not found"
        )
    
    # Get task statistics
    from_date = datetime.utcnow() - timedelta(days=days)
    
    # Completed tasks
    completed_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.assigned_director_id == director_id,
            Task.status == "completed",
            Task.completed_at >= from_date
        )
    )
    completed_count = completed_result.scalar()
    
    # Failed tasks
    failed_result = await db.execute(
        select(func.count()).select_from(Task).where(
            Task.assigned_director_id == director_id,
            Task.status == "failed",
            Task.completed_at >= from_date
        )
    )
    failed_count = failed_result.scalar()
    
    # Average execution time
    time_result = await db.execute(
        select(func.avg(Task.execution_time)).where(
            Task.assigned_director_id == director_id,
            Task.status == "completed",
            Task.completed_at >= from_date
        )
    )
    avg_execution_time = time_result.scalar() or 0.0
    
    # Quality scores
    quality_result = await db.execute(
        select(Task.quality_score).where(
            Task.assigned_director_id == director_id,
            Task.status == "completed",
            Task.completed_at >= from_date,
            Task.quality_score.isnot(None)
        )
    )
    quality_scores = [score for (score,) in quality_result]
    
    # Task distribution by priority
    priority_result = await db.execute(
        select(Task.priority, func.count()).where(
            Task.assigned_director_id == director_id,
            Task.completed_at >= from_date
        ).group_by(Task.priority)
    )
    task_distribution = {priority: count for priority, count in priority_result}
    
    return DirectorPerformance(
        director_id=director.id,
        director_name=director.name,
        period_days=days,
        tasks_completed=completed_count,
        tasks_failed=failed_count,
        success_rate=completed_count / (completed_count + failed_count) if (completed_count + failed_count) > 0 else 0.0,
        average_execution_time=avg_execution_time,
        average_quality_score=sum(quality_scores) / len(quality_scores) if quality_scores else 0.0,
        quality_scores=quality_scores,
        task_distribution=task_distribution,
        specialties=director.specialties,
        overall_score=director.overall_score
    )


@router.post("/{director_id}/reset-metrics", response_model=MessageResponse)
async def reset_director_metrics(
    director_id: str,
    current_user: User = Depends(get_current_superuser),
    db: AsyncSession = Depends(get_async_db)
):
    """Reset performance metrics for a director (admin only)"""
    result = await db.execute(
        select(Director).where(Director.id == director_id)
    )
    director = result.scalar_one_or_none()
    
    if not director:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Director not found"
        )
    
    # Reset metrics
    director.tasks_completed = 0
    director.tasks_failed = 0
    director.total_execution_time = 0.0
    director.quality_scores = []
    director.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info(f"Metrics reset for director {director.name} by {current_user.username}")
    
    return {"message": f"Metrics reset for director {director.name}"}


from datetime import timedelta  # Add this import at the top