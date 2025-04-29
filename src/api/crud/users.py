from sqlalchemy.orm import Session

from api.models.users import User
from api.schemas import user as user_schemas
from core.utils import auth, idsvc


def create_user(db: Session, user: user_schemas.UserCreate, role: str = "user") -> User:
    """Create a new user in the database."""
    hashed_password = auth.hash_password(user.password) if user.password else None
    user_id = idsvc.generate_id("U")
    db_user = User(
        id=user_id,
        username=user.username,
        email=user.email,
        password=hashed_password,
        icon=user.icon,
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_email(db: Session, email: str) -> User | None:
    """Fetch a user by their email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    """Fetch a user by their id."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Fetch a user by their username."""
    return db.query(User).filter(User.username == username).first()
