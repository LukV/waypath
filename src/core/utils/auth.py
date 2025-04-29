import os
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from api.crud import users as crud_users
from api.models import users as model_users
from core.utils.database import get_db

SECRET_KEY = os.getenv("SECRET_KEY")
if SECRET_KEY is None:
    raise ValueError("Environment variable 'SECRET_KEY' is not set.")  # noqa: TRY003

SECRET_KEY_BYTES = SECRET_KEY.encode()
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # Default to HS256 if not set
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),  # noqa: B008
) -> model_users.User:
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

    user = crud_users.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception
    return user


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a hashed password."""
    return bool(pwd_context.verify(plain_password, hashed_password))


def create_access_token(data: dict[str, Any]) -> str:
    """Create an access JWT token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, SECRET_KEY_BYTES, algorithm=ALGORITHM))


def create_refresh_token(data: dict[str, Any]) -> str:
    """Create a refresh JWT token."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, SECRET_KEY_BYTES, algorithm=ALGORITHM))
