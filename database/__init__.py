"""
Database Engine Configuration
Supports PostgreSQL and MySQL with async SQLAlchemy
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool

from config import config


class Base(DeclarativeBase):
    """Base class for all models"""
    pass


# Create async engine
engine = create_async_engine(
    config.database_url,
    echo=False,
    poolclass=NullPool,
)

# Create async session factory
async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        yield session
