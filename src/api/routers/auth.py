from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import users as crud_users
from core.schemas.auth import LoginRequest, TokenPair
from core.utils import auth
from core.utils.database import get_db

router = APIRouter()


@router.post("/login", response_model=TokenPair)
async def login(
    login_data: LoginRequest, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, str]:
    """Endpoint for user login with credentials."""
    if not login_data.username or not login_data.password:
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    user = await crud_users.get_user_by_email(
        db, login_data.username
    ) or await crud_users.get_user_by_username(db, login_data.username)

    if not user or not await auth.verify_password(
        login_data.password, str(user.password)
    ):
        raise HTTPException(status_code=400, detail="Invalid credentials.")

    access_token = await auth.create_access_token(data={"sub": user.email})
    refresh_token = auth.create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=TokenPair)
async def refresh_token(
    token: str, db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, str]:
    """Refresh the access token using a valid refresh token."""
    try:
        if not auth.SECRET_KEY:
            raise HTTPException(
                status_code=500,
                detail={"code": "AUTH_006", "message": "Secret key is not configured."},
            )
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=401,
                detail={"code": "AUTH_005", "message": "Invalid refresh token."},
            )

        user = crud_users.get_user_by_email(db, email)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail={"code": "USER_001", "message": "User not found."},
            )

        # Generate new access and refresh tokens
        access_token = await auth.create_access_token(data={"sub": email})
        new_refresh_token = auth.create_refresh_token(data={"sub": email})
        return {  # noqa: TRY300
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    except JWTError as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "AUTH_005",
                "message": "Invalid refresh token.",
                "msgtype": "error",
            },
        ) from exc
