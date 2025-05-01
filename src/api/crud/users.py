from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import User
from core.schemas import user as user_schemas
from core.utils import auth, idsvc


async def create_user(db: AsyncSession, user: user_schemas.UserCreate) -> User:
    """Create a new user in the database."""
    hashed_password = await auth.hash_password(user.password) if user.password else None
    user_id = idsvc.generate_id("U")
    db_user = User(
        id=user_id, username=user.username, email=user.email, password=hashed_password
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Fetch a user by their email."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Fetch a user by their id."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    """Fetch a user by their username."""
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()
