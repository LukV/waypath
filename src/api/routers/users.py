from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import users as crud_users
from core.db import models
from core.schemas import user as user_schemas
from core.utils.database import get_db

router = APIRouter()


@router.post("/", response_model=user_schemas.UserResponse)
async def create_user(
    user: user_schemas.UserCreate,
    db: AsyncSession = Depends(get_db),  # noqa: B008, FAST002
) -> models.User:
    """Create a new user in the database."""
    if await crud_users.get_user_by_email(
        db, user.email
    ) or await crud_users.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=400, detail="Username or email already registered."
        )
    return await crud_users.create_user(db, user)
