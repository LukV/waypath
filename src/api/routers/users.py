from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.crud import users as crud_users
from api.models import users as user_models
from api.schemas import user as user_schemas
from core.utils.database import get_db

router = APIRouter()


@router.post("/", response_model=user_schemas.UserResponse)
def create_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db),  # noqa: B008, FAST002
) -> user_models.User:
    """Create a new user in the database."""
    if crud_users.get_user_by_email(db, user.email) or crud_users.get_user_by_username(
        db, user.username
    ):
        raise HTTPException(
            status_code=400, detail="Username or email already registered."
        )
    return crud_users.create_user(db, user)
