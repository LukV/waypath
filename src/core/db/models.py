from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from core.utils.database import Base


class User(Base):  # noqa: D101
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship("Order", back_populates="user")


class Order(Base):  # noqa: D101
    __tablename__ = "orders"

    id = Column(String, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    customer_address = Column(String, nullable=False)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    order_date = Column(String, nullable=False)
    due_date = Column(String, nullable=False)
    total_excl_vat = Column(Float, nullable=False)
    vat = Column(Float, nullable=False)
    total_incl_vat = Column(Float, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lines = relationship(
        "OrderLine", back_populates="order", cascade="all, delete-orphan"
    )
    user = relationship("User", back_populates="orders")


class OrderLine(Base):  # noqa: D101
    __tablename__ = "order_lines"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )

    product_code = Column(String, nullable=False)
    description = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    order = relationship("Order", back_populates="lines")
