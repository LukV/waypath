import os
from collections.abc import AsyncGenerator

import dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# Base class for SQLAlchemy models
class Base(DeclarativeBase):  # noqa: D101
    pass


# Load environment
dotenv.load_dotenv()

# Database connection URL
SQLALCHEMY_DATABASE_URL = os.getenv(
    "SQLALCHEMY_DATABASE_URL", "sqlite+aiosqlite:///./waypath.db"
)

# Initialize the async engine
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=True)

# Configure AsyncSession
async_session_maker = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore  # noqa: PGH003


# Dependency to get DB session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a new async database session for request lifecycle management."""
    async with async_session_maker() as session:
        yield session
