from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db.models import User
from core.schemas import user as user_schemas
from core.utils import auth, idsvc


async def create_user(
    db: AsyncSession, user: user_schemas.UserCreate, role: str = "user"
) -> User:
    """Create a new user in the database."""
    hashed_password = await auth.hash_password(user.password) if user.password else None
    user_id = idsvc.generate_id("U")
    db_user = User(
        id=user_id,
        username=user.username,
        email=user.email,
        password=hashed_password,
        role=role,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def update_user(
    db: AsyncSession, user_id: str, user_update: user_schemas.UserUpdate
) -> User:
    """Update an existing user's details in the database."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def admin_update_user(
    db: AsyncSession, user_id: str, user_update: user_schemas.AdminUserUpdate
) -> User:
    """Admin can update any user's details, including role."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    update_data = user_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: str) -> User | None:
    """Delete an existing user from the database."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    db_user = result.scalar_one_or_none()
    if db_user:
        await db.delete(db_user)
        await db.commit()
    return db_user


async def get_all_users(db: AsyncSession) -> list[User]:
    """Retrieve all users from the database."""
    result = await db.execute(select(User))
    return list(result.scalars().all())


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
