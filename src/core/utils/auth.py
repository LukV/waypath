import os
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

from fastapi import Depends, HTTPException
from fastapi import Path as FastAPIPath
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import users as crud_users
from core.db import models
from core.utils.database import Base, get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("Environment variable 'SECRET_KEY' is not set.")  # noqa: TRY003

SECRET_KEY_BYTES = SECRET_KEY.encode()
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default to HS256 if not set
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),  # noqa: B008
) -> models.User:
    """Retrieve the current user from the provided JWT token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY_BYTES, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc

    user = await crud_users.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return str(pwd_context.hash(password))


async def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return bool(pwd_context.verify(plain_password, hashed_password))


async def create_access_token(data: dict[str, Any]) -> str:
    """Create an access JWT token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, SECRET_KEY_BYTES, algorithm=ALGORITHM))


async def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a refresh JWT token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, SECRET_KEY_BYTES, algorithm=ALGORITHM))


async def create_password_reset_token(user_id: str) -> str:
    """Generate a password reset token for a given user ID."""
    expires = datetime.now(UTC) + timedelta(hours=1)  # Token expires in 1 hour
    to_encode = {"exp": expires, "sub": str(user_id)}
    return str(jwt.encode(to_encode, SECRET_KEY_BYTES, algorithm=ALGORITHM))


async def is_admin(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.User:
    """Evaluate if the logged in user has role admin."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user


def is_admin_or_entity_owner(
    entity_getter: Callable[[AsyncSession, str], Awaitable[Base]],
    entity_name: str = "Entity",
    ownership_field: str = "user_id",
    entity_id_param: str = "entity_id",
) -> Callable[..., Awaitable[models.User]]:
    """Return a dependency that verifies if the current user is admin or the owner."""

    async def dependency(
        entity_id: str = FastAPIPath(..., alias=entity_id_param),
        db: AsyncSession = Depends(get_db),  # noqa: B008
        current_user: models.User = Depends(get_current_user),  # noqa: B008
    ) -> models.User:
        if current_user is None:
            raise HTTPException(status_code=401, detail="User not authenticated")

        if current_user.role == "admin":
            return current_user

        entity = await entity_getter(db, entity_id)
        if not entity:
            raise HTTPException(status_code=404, detail=f"{entity_name} not found.")

        if getattr(entity, ownership_field) != current_user.id:
            raise HTTPException(status_code=403, detail="Operation not permitted.")

        return current_user

    return dependency
