"""
Database models for Board of Directors AI System
Uses SQLAlchemy ORM with PostgreSQL
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Text, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid

Base = declarative_base()


class Director(Base):
    """AI Director/Agent model"""
    __tablename__ = "directors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False, index=True)
    role = Column(String(200), nullable=False)
    endpoint = Column(String(500), nullable=False)
    api_key_encrypted = Column(Text, nullable=True)  # Encrypted API key
    specialties = Column(JSONB, default=list)
    is_available = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Performance metrics
    tasks_completed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    total_execution_time = Column(Float, default=0.0)
    quality_scores = Column(JSONB, default=list)
    
    # Relationships
    tasks = relationship("Task", back_populates="assigned_director")
    
    __table_args__ = (
        Index('idx_director_performance', 'tasks_completed', 'tasks_failed'),
    )
    
    @property
    def success_rate(self) -> float:
        total = self.tasks_completed + self.tasks_failed
        return self.tasks_completed / total if total > 0 else 0.0
    
    @property
    def average_quality(self) -> float:
        scores = self.quality_scores or []
        return sum(scores) / len(scores) if scores else 0.0
    
    @property
    def efficiency_score(self) -> float:
        if self.tasks_completed == 0:
            return 0.0
        avg_time = self.total_execution_time / self.tasks_completed
        return min(1.0, 10.0 / (avg_time + 1))
    
    @property
    def overall_score(self) -> float:
        return (
            self.success_rate * 0.4 +
            self.average_quality * 0.4 +
            self.efficiency_score * 0.2
        )


class Task(Base):
    """Task model for delegation and tracking"""
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False, index=True)
    description = Column(Text)
    requirements = Column(JSONB, default=list)
    deliverables = Column(JSONB, default=list)
    priority = Column(String(20), default="medium", index=True)
    status = Column(String(50), default="pending", index=True)
    
    # Assignment and execution
    assigned_director_id = Column(UUID(as_uuid=True), ForeignKey("directors.id"), nullable=True)
    assigned_director = relationship("Director", back_populates="tasks")
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    execution_time = Column(Float, nullable=True)
    
    # Results and metrics
    result = Column(JSONB, nullable=True)
    quality_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # User and session tracking
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="tasks")
    session_id = Column(UUID(as_uuid=True), ForeignKey("board_sessions.id"), nullable=True)
    session = relationship("BoardSession", back_populates="tasks")
    
    __table_args__ = (
        Index('idx_task_status_priority', 'status', 'priority'),
        Index('idx_task_user_session', 'user_id', 'session_id'),
    )


class User(Base):
    """User model with authentication and authorization"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # User details
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    
    # API access
    api_key = Column(String(255), unique=True, nullable=True, index=True)
    api_key_created_at = Column(DateTime, nullable=True)
    
    # Rate limiting
    request_count = Column(Integer, default=0)
    last_request_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    
    # Relationships
    tasks = relationship("Task", back_populates="user")
    sessions = relationship("BoardSession", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")


class BoardSession(Base):
    """Board session for grouping related tasks"""
    __tablename__ = "board_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    chairperson_id = Column(UUID(as_uuid=True), ForeignKey("directors.id"), nullable=True)
    chairperson = relationship("Director", foreign_keys=[chairperson_id])
    
    # Session details
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="sessions")
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    ended_at = Column(DateTime, nullable=True)
    
    # Metrics
    total_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)
    failed_tasks = Column(Integer, default=0)
    
    # Relationships
    tasks = relationship("Task", back_populates="session")


class PrivacyShieldLog(Base):
    """Privacy shield filtering log"""
    __tablename__ = "privacy_shield_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Request details
    request_id = Column(String(100), index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Filtering details
    data_type = Column(String(50))  # 'request' or 'response'
    original_size = Column(Integer)
    filtered_size = Column(Integer)
    pii_detected = Column(JSONB, default=list)  # List of PII types detected
    
    # Performance
    processing_time = Column(Float)  # in milliseconds


class AuditLog(Base):
    """Audit log for compliance and monitoring"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="audit_logs")
    ip_address = Column(String(45))  # Supports IPv6
    user_agent = Column(String(500))
    
    # Action details
    action = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    
    # Request/Response
    request_method = Column(String(10))
    request_path = Column(String(500))
    response_status = Column(Integer)
    
    # Additional context
    details = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_timestamp_action', 'timestamp', 'action'),
    )


class SystemMetric(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Metric details
    metric_type = Column(String(50), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    value = Column(Float, nullable=False)
    unit = Column(String(20))
    
    # Context
    component = Column(String(50))  # 'backend', 'frontend', 'database', etc.
    tags = Column(JSONB, default=dict)
    
    __table_args__ = (
        Index('idx_metric_type_name', 'metric_type', 'metric_name'),
        Index('idx_metric_timestamp_type', 'timestamp', 'metric_type'),
    )


class CacheEntry(Base):
    """Cache entries for performance optimization"""
    __tablename__ = "cache_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(JSONB, nullable=False)
    
    # TTL management
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False, index=True)
    
    # Metadata
    hit_count = Column(Integer, default=0)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    data_size = Column(Integer)  # Size in bytes