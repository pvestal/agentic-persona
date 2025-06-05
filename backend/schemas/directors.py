"""
Director schemas for request/response validation
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, validator, UUID4, HttpUrl


class DirectorBase(BaseModel):
    """Base director schema"""
    name: str
    role: str
    endpoint: str
    specialties: List[str] = []
    is_available: bool = True
    
    @validator('name')
    def name_valid(cls, v):
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v
    
    @validator('endpoint')
    def endpoint_valid(cls, v):
        if not v.startswith(('http://', 'https://')):
            raise ValueError('Endpoint must be a valid URL')
        return v


class DirectorCreate(DirectorBase):
    """Schema for creating a director"""
    api_key: Optional[str] = None


class DirectorUpdate(BaseModel):
    """Schema for updating a director"""
    name: Optional[str] = None
    role: Optional[str] = None
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    specialties: Optional[List[str]] = None
    is_available: Optional[bool] = None
    
    @validator('endpoint')
    def endpoint_valid(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Endpoint must be a valid URL')
        return v


class DirectorResponse(DirectorBase):
    """Schema for director responses"""
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True


class DirectorMetrics(BaseModel):
    """Director performance metrics"""
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    average_quality: float
    efficiency_score: float
    overall_score: float
    total_execution_time: float


class DirectorWithMetrics(DirectorResponse):
    """Director with performance metrics"""
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    average_quality: float
    efficiency_score: float
    overall_score: float
    
    @classmethod
    def from_orm(cls, director):
        return cls(
            id=director.id,
            name=director.name,
            role=director.role,
            endpoint=director.endpoint,
            specialties=director.specialties,
            is_available=director.is_available,
            created_at=director.created_at,
            updated_at=director.updated_at,
            tasks_completed=director.tasks_completed,
            tasks_failed=director.tasks_failed,
            success_rate=director.success_rate,
            average_quality=director.average_quality,
            efficiency_score=director.efficiency_score,
            overall_score=director.overall_score
        )


class DirectorPerformance(BaseModel):
    """Detailed performance report for a director"""
    director_id: UUID4
    director_name: str
    period_days: int
    tasks_completed: int
    tasks_failed: int
    success_rate: float
    average_execution_time: float
    average_quality_score: float
    quality_scores: List[float]
    task_distribution: Dict[str, int]
    specialties: List[str]
    overall_score: float