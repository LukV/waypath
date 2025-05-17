from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from jose import jwt
from jose.exceptions import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud import users as crud_users
from core.db import models
from core.schemas import user as user_schemas
from core.utils.auth import (
    ALGORITHM,
    SECRET_KEY_BYTES,
    create_password_reset_token,
    get_current_user,
    hash_password,
    is_admin,
    is_admin_or_entity_owner,
)
from core.utils.database import get_db
from core.utils.sendmail import send_reset_email

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


@router.get("/", response_model=list[user_schemas.UserResponse])
async def get_all_users(
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> list[user_schemas.UserResponse]:
    """Retrieve a list of all users in the database."""
    users = await crud_users.get_all_users(db)
    if current_user.role == "admin":
        return [user_schemas.AdminUserResponse(**user.__dict__) for user in users]

    return [user_schemas.UserResponse(**user.__dict__) for user in users]


@router.get("/me", response_model=user_schemas.UserResponse)
async def get_current_user_info(
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> user_schemas.UserResponse:
    """Retrieve the current user's information."""
    if current_user.role == "admin":
        return user_schemas.AdminUserResponse(**current_user.__dict__)

    return user_schemas.UserResponse(**current_user.__dict__)


@router.get("/{user_id}", response_model=user_schemas.UserResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> user_schemas.UserResponse:
    """Retrieve a user's details."""
    user = await crud_users.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.role == "admin":
        return user_schemas.AdminUserResponse(**user.__dict__)

    return user_schemas.UserResponse(**user.__dict__)


@router.put("/{user_id}", response_model=user_schemas.UserResponse)
async def update_user(
    user_id: str,
    user_update: user_schemas.UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        models.User,
        Depends(
            is_admin_or_entity_owner(
                crud_users.get_user_by_id,
                entity_name="User",
                ownership_field="id",
                entity_id_param="user_id",
            )
        ),
    ],
) -> user_schemas.UserResponse:
    """Update an existing user's details."""
    updated_user = await crud_users.update_user(db, user_id, user_update)
    return user_schemas.UserResponse.model_validate(updated_user)


@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    user_update: user_schemas.AdminUserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[models.User, Depends(is_admin)],
) -> user_schemas.AdminUserResponse:
    """Admin can update a user's role."""
    updated_user = await crud_users.admin_update_user(db, user_id, user_update)
    return user_schemas.AdminUserResponse.model_validate(updated_user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[models.User, Depends(get_current_user)],
) -> None:
    """Delete an existing user from the database. This is a hard delete."""
    await crud_users.delete_user(db, user_id)


@router.post("/request-password-reset")
async def request_password_reset(
    payload: user_schemas.PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> str:
    """Request a password reset by sending a reset link to the user's email."""
    user = await crud_users.get_user_by_email(db, email=payload.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Generate a token with an expiry
    token = await create_password_reset_token(user.id)

    # Add the email sending task to the background
    background_tasks.add_task(send_reset_email, payload.email, token)

    return "Password reset email sent."


@router.post("/reset-password")
async def reset_password(
    payload: user_schemas.PasswordReset,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, str]:
    """Reset a user's password using a token for validation."""
    try:
        # Decode the token using the auth module
        payload_data = jwt.decode(
            payload.token, SECRET_KEY_BYTES, algorithms=[ALGORITHM]
        )
        user_uid = payload_data.get("sub")
    except JWTError as exc:
        raise HTTPException(
            status_code=400, detail="Invalid or expired token."
        ) from exc

    # Verify that the email and user_uid match
    user = await crud_users.get_user_by_email(db, email=payload.email)
    if not user or str(user.id) != user_uid:
        raise HTTPException(
            status_code=404, detail="User not found, or email does not match token."
        )

    user.password = await hash_password(payload.new_password)
    await db.commit()
    return {
        "detail": "Password reset successfully",
    }


@router.post("/change-password")
async def change_password(
    request: user_schemas.PasswordChange,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> str:
    """Update the password for the authenticated user."""
    updated_user = crud_users.update_password(
        db=db, user_id=current_user.id, new_password=request.new_password
    )
    if not updated_user:
        raise HTTPException(
            status_code=404, detail="User not found or password could not be updated."
        )
    return "Password updated successfully."
