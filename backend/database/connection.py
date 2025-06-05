"""
PostgreSQL database connection and session management
Implements connection pooling, retry logic, and health checks
"""

import asyncio
import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine, event, pool, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import OperationalError, DisconnectionError
from sqlalchemy.pool import NullPool, QueuePool

from backend.database.models import Base
from backend.config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections with pooling and health checks"""
    
    def __init__(self):
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
        self._initialized = False
        
    def initialize(self):
        """Initialize database connections"""
        if self._initialized:
            return
            
        # Synchronous engine with connection pooling
        self.engine = create_engine(
            settings.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,  # Verify connections before using
            echo=settings.DEBUG,
            connect_args={
                "connect_timeout": 10,
                "application_name": "board_of_directors",
                "options": "-c statement_timeout=30000"  # 30 second statement timeout
            }
        )
        
        # Async engine for async operations
        self.async_engine = create_async_engine(
            settings.ASYNC_DATABASE_URL,
            poolclass=QueuePool,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_pre_ping=True,
            echo=settings.DEBUG
        )
        
        # Session factories
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
            expire_on_commit=False
        )
        
        self.AsyncSessionLocal = async_sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.async_engine,
            expire_on_commit=False,
            class_=AsyncSession
        )
        
        # Set up event listeners
        self._setup_event_listeners()
        
        self._initialized = True
        logger.info("Database manager initialized successfully")
        
    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners for monitoring"""
        
        @event.listens_for(self.engine, "connect")
        def receive_connect(dbapi_connection, connection_record):
            """Log new connections"""
            logger.debug(f"New database connection established: {id(dbapi_connection)}")
            
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkouts from pool"""
            logger.debug(f"Connection checked out from pool: {id(dbapi_connection)}")
            
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection returns to pool"""
            logger.debug(f"Connection returned to pool: {id(dbapi_connection)}")
            
    async def create_tables(self):
        """Create all database tables"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
    async def drop_tables(self):
        """Drop all database tables (use with caution!)"""
        async with self.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            logger.warning("All database tables dropped!")
            
    @contextmanager
    def get_db(self) -> Generator[Session, None, None]:
        """Get synchronous database session"""
        if not self._initialized:
            self.initialize()
            
        db = self.SessionLocal()
        try:
            yield db
            db.commit()
        except Exception as e:
            db.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            db.close()
            
    @asynccontextmanager
    async def get_async_db(self) -> AsyncGenerator[AsyncSession, None]:
        """Get asynchronous database session"""
        if not self._initialized:
            self.initialize()
            
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Async database error: {e}")
                raise
            finally:
                await session.close()
                
    async def health_check(self) -> dict:
        """Perform database health check"""
        try:
            async with self.get_async_db() as db:
                result = await db.execute(text("SELECT 1"))
                await db.execute(text("SELECT version()"))
                
            pool_status = self.engine.pool.status()
            
            return {
                "status": "healthy",
                "pool_size": self.engine.pool.size(),
                "pool_checked_out": self.engine.pool.checked_out_connections(),
                "pool_overflow": self.engine.pool.overflow(),
                "pool_total": self.engine.pool.total(),
                "details": pool_status
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e)
            }
            
    async def execute_with_retry(self, func, max_retries: int = 3, retry_delay: float = 1.0):
        """Execute database operation with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                return await func()
            except (OperationalError, DisconnectionError) as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(f"Database operation failed (attempt {attempt + 1}/{max_retries}): {e}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    
                    # Reset connection pool if needed
                    if isinstance(e, DisconnectionError):
                        await self.async_engine.dispose()
                else:
                    logger.error(f"Database operation failed after {max_retries} attempts: {e}")
                    
        raise last_error
        
    async def close(self):
        """Close all database connections"""
        if self.engine:
            self.engine.dispose()
            logger.info("Synchronous database connections closed")
            
        if self.async_engine:
            await self.async_engine.dispose()
            logger.info("Asynchronous database connections closed")
            
        self._initialized = False
        
    def get_pool_status(self) -> dict:
        """Get current connection pool status"""
        if not self.engine:
            return {"status": "not_initialized"}
            
        return {
            "size": self.engine.pool.size(),
            "checked_out": self.engine.pool.checked_out_connections(),
            "overflow": self.engine.pool.overflow(),
            "total": self.engine.pool.total()
        }


# Global database manager instance
db_manager = DatabaseManager()


# Dependency injection functions for FastAPI
def get_db() -> Generator[Session, None, None]:
    """Dependency for synchronous database sessions"""
    with db_manager.get_db() as db:
        yield db
        

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for asynchronous database sessions"""
    async with db_manager.get_async_db() as db:
        yield db