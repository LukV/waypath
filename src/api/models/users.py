from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func

from core.utils.database import Base


class User(Base):  # noqa: D101
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
