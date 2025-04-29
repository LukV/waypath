import os
from collections.abc import Generator

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


# Base class for SQLAlchemy models
class Base(DeclarativeBase):  # noqa: D101
    pass


# Database connection URL
dotenv.load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL", "sqlite:///./waypath.db")

# Initialize the engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Configure SessionLocal and Base
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a new database session for request lifecycle management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
