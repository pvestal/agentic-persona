"""
Task schemas for request/response validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator, UUID4, Field


class TaskBase(BaseModel):
    """Base task schema"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    requirements: List[str] = []
    deliverables: List[Dict[str, Any]] = []
    priority: str = "medium"
    
    @validator('priority')
    def priority_valid(cls, v):
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class TaskCreate(TaskBase):
    """Schema for creating a task"""
    session_id: Optional[UUID4] = None
    auto_execute: bool = False


class TaskUpdate(BaseModel):
    """Schema for updating a task"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    deliverables: Optional[List[Dict[str, Any]]] = None
    priority: Optional[str] = None
    
    @validator('priority')
    def priority_valid(cls, v):
        if v is not None:
            valid_priorities = ["low", "medium", "high", "critical"]
            if v not in valid_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class TaskResponse(TaskBase):
    """Basic task response"""
    id: UUID4
    status: str
    user_id: Optional[UUID4]
    session_id: Optional[UUID4]
    assigned_director_id: Optional[UUID4]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_time: Optional[float]
    quality_score: Optional[float]
    error_message: Optional[str]
    
    class Config:
        orm_mode = True


class TaskWithDetails(TaskResponse):
    """Task with related details"""
    assigned_director: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    session: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    
    @classmethod
    def from_orm(cls, task):
        data = {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "requirements": task.requirements,
            "deliverables": task.deliverables,
            "priority": task.priority,
            "status": task.status,
            "user_id": task.user_id,
            "session_id": task.session_id,
            "assigned_director_id": task.assigned_director_id,
            "created_at": task.created_at,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "execution_time": task.execution_time,
            "quality_score": task.quality_score,
            "error_message": task.error_message,
            "result": task.result
        }
        
        if task.assigned_director:
            data["assigned_director"] = {
                "id": task.assigned_director.id,
                "name": task.assigned_director.name,
                "role": task.assigned_director.role
            }
        
        if task.user:
            data["user"] = {
                "id": task.user.id,
                "username": task.user.username,
                "email": task.user.email
            }
        
        if task.session:
            data["session"] = {
                "id": task.session.id,
                "name": task.session.name,
                "chairperson_id": task.session.chairperson_id
            }
        
        return cls(**data)


class TaskExecute(BaseModel):
    """Schema for task execution request"""
    director_id: Optional[UUID4] = None
    override_timeout: Optional[int] = Field(None, ge=1, le=3600)


class TaskResult(BaseModel):
    """Task execution result"""
    task_id: UUID4
    status: str
    result: Dict[str, Any]
    execution_time: float
    quality_score: Optional[float]
    error_message: Optional[str]


class TaskBulkCreate(BaseModel):
    """Schema for creating multiple tasks"""
    tasks: List[TaskCreate]
    session_name: Optional[str] = None
    auto_execute: bool = False


class TaskFilter(BaseModel):
    """Task filter parameters"""
    status: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    assigned_director_ids: Optional[List[UUID4]] = None
    session_ids: Optional[List[UUID4]] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    search: Optional[str] = None