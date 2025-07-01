"""
GridWorks Infra - Database Session Management
Async PostgreSQL session handling with connection pooling
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
)
from sqlalchemy.pool import NullPool, QueuePool
from contextlib import asynccontextmanager
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database connections and sessions
    Supports read replicas and connection pooling
    """
    
    def __init__(self):
        self._engine: Optional[AsyncEngine] = None
        self._read_engine: Optional[AsyncEngine] = None
        self._sessionmaker: Optional[async_sessionmaker] = None
        self._read_sessionmaker: Optional[async_sessionmaker] = None
    
    async def initialize(self):
        """Initialize database engines and session makers"""
        
        # Main database engine (write operations)
        self._engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DATABASE_ECHO,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW,
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections after 1 hour
            poolclass=QueuePool,
            connect_args={
                "server_settings": {
                    "application_name": "gridworks-infra",
                    "jit": "off"
                },
                "command_timeout": 60,
                "connection_timeout": 10,
            }
        )
        
        # Read replica engine (if configured)
        if settings.DATABASE_READ_URL:
            self._read_engine = create_async_engine(
                settings.DATABASE_READ_URL,
                echo=False,
                pool_size=settings.DATABASE_POOL_SIZE * 2,  # More connections for reads
                max_overflow=settings.DATABASE_MAX_OVERFLOW * 2,
                pool_pre_ping=True,
                pool_recycle=3600,
                poolclass=QueuePool,
                connect_args={
                    "server_settings": {
                        "application_name": "gridworks-infra-read",
                        "jit": "off"
                    },
                    "command_timeout": 60,
                    "connection_timeout": 10,
                }
            )
        else:
            self._read_engine = self._engine
        
        # Create session makers
        self._sessionmaker = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        self._read_sessionmaker = async_sessionmaker(
            self._read_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        logger.info("Database engines initialized successfully")
    
    async def close(self):
        """Close all database connections"""
        if self._engine:
            await self._engine.dispose()
        if self._read_engine and self._read_engine != self._engine:
            await self._read_engine.dispose()
        logger.info("Database engines closed")
    
    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session for write operations"""
        if not self._sessionmaker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._sessionmaker() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    @asynccontextmanager
    async def read_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get a database session for read-only operations"""
        if not self._read_sessionmaker:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        async with self._read_sessionmaker() as session:
            try:
                yield session
            finally:
                await session.close()
    
    async def execute_raw(self, query: str, params: dict = None):
        """Execute raw SQL query"""
        async with self.session() as session:
            result = await session.execute(query, params)
            return result
    
    async def health_check(self) -> bool:
        """Check database connectivity"""
        try:
            async with self.session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()


# Dependency injection for FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    Usage: db: AsyncSession = Depends(get_db)
    """
    async with db_manager.session() as session:
        yield session


async def get_read_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get read-only database session
    Usage: db: AsyncSession = Depends(get_read_db)
    """
    async with db_manager.read_session() as session:
        yield session


# Lifecycle management for FastAPI
async def init_db():
    """Initialize database on application startup"""
    await db_manager.initialize()
    
    # Create tables if needed (development only)
    if settings.ENVIRONMENT == "development":
        from .models import Base
        async with db_manager._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created")


async def close_db():
    """Close database connections on application shutdown"""
    await db_manager.close()