from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.utils.database import Base


class User(Base):  # noqa: D101
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    icon = Column(String, nullable=True)
    role = Column(String, default="user")
    date_created = Column(DateTime(timezone=True), server_default=func.now())  # pylint: disable=E1102
    hypotheses = relationship("Hypothesis", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
