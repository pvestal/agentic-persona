"""
Database service for persistence
"""

from sqlalchemy import create_engine, Column, String, DateTime, Float, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from datetime import datetime
from typing import Generator

from config.settings import settings

Base = declarative_base()

# Models

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    content = Column(Text, nullable=False)
    platform = Column(String, nullable=False)
    sender = Column(String, nullable=False)
    recipient = Column(String)
    subject = Column(String)
    thread_id = Column(String)
    urgency = Column(Float, default=0.5)
    sentiment = Column(String)
    category = Column(String)
    response = Column(Text)
    action_taken = Column(String)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    message_metadata = Column(JSON)

class AgentState(Base):
    __tablename__ = "agent_states"
    
    agent_name = Column(String, primary_key=True)
    version = Column(String, nullable=False)
    configuration = Column(JSON)
    statistics = Column(JSON)
    last_evolved = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LearningData(Base):
    __tablename__ = "learning_data"
    
    id = Column(String, primary_key=True)
    agent_name = Column(String, nullable=False)
    interaction_type = Column(String)
    original_input = Column(Text)
    generated_output = Column(Text)
    user_feedback = Column(String)
    edited_output = Column(Text)
    patterns = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    communication_style = Column(String, default="balanced")
    vip_contacts = Column(JSON, default=list)
    platform_settings = Column(JSON, default=dict)
    autonomy_settings = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database setup

engine = None
async_engine = None
SessionLocal = None
AsyncSessionLocal = None

async def init_db():
    """Initialize database"""
    global engine, async_engine, SessionLocal, AsyncSessionLocal
    
    # Create async engine
    async_engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        future=True
    )
    
    # Create sync engine for migrations
    sync_url = settings.database_url.replace("+aiosqlite", "")
    engine = create_engine(sync_url, echo=settings.debug)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session factories
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    AsyncSessionLocal = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    print("✅ Database initialized")

def get_db() -> Generator[Session, None, None]:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_async_db() -> AsyncSession:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        yield session

# Helper functions

async def save_message(db: AsyncSession, message_data: dict):
    """Save message to database"""
    message = Message(**message_data)
    db.add(message)
    await db.commit()
    return message

async def get_message_history(
    db: AsyncSession,
    platform: str = None,
    sender: str = None,
    limit: int = 50
):
    """Get message history with filters"""
    from sqlalchemy import select, desc
    
    query = select(Message).order_by(desc(Message.created_at)).limit(limit)
    
    if platform:
        query = query.where(Message.platform == platform)
    if sender:
        query = query.where(Message.sender == sender)
    
    result = await db.execute(query)
    return result.scalars().all()

async def save_learning_data(
    db: AsyncSession,
    agent_name: str,
    interaction_data: dict
):
    """Save learning data"""
    learning = LearningData(
        id=f"learn_{datetime.now().timestamp()}",
        agent_name=agent_name,
        **interaction_data
    )
    db.add(learning)
    await db.commit()
    return learning

async def get_agent_state(db: AsyncSession, agent_name: str):
    """Get agent state"""
    from sqlalchemy import select
    
    query = select(AgentState).where(AgentState.agent_name == agent_name)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_agent_state(
    db: AsyncSession,
    agent_name: str,
    state_data: dict
):
    """Update agent state"""
    from sqlalchemy import update
    
    stmt = update(AgentState).where(
        AgentState.agent_name == agent_name
    ).values(**state_data)
    
    await db.execute(stmt)
    await db.commit()