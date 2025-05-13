from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.utils.config import OrderStatus
from core.utils.database import Base


class User(Base):  # noqa: D101
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(
        String, unique=True, index=True, nullable=False
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    password: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, default="user")
    date_created: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    orders: Mapped[list["Order"]] = relationship("Order", back_populates="user")


class Order(Base):  # noqa: D101
    __tablename__ = "orders"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String, nullable=True)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    customer_address: Mapped[str] = mapped_column(String, nullable=False)
    invoice_number: Mapped[str] = mapped_column(String, index=True, nullable=False)
    order_date: Mapped[str] = mapped_column(String, nullable=False)
    due_date: Mapped[str] = mapped_column(String, nullable=False)
    total_excl_vat: Mapped[float] = mapped_column(Float, nullable=False)
    vat: Mapped[float] = mapped_column(Float, nullable=False)
    total_incl_vat: Mapped[float] = mapped_column(Float, nullable=False)
    created_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    lines: Mapped[list["OrderLine"]] = relationship(
        "OrderLine", back_populates="order", cascade="all, delete-orphan"
    )
    status: Mapped[OrderStatus] = mapped_column(
        SqlEnum(OrderStatus, name="orderstatus"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="orders")


class OrderLine(Base):  # noqa: D101
    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    order_id: Mapped[str] = mapped_column(
        String, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )

    product_code: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column(nullable=False)
    subtotal: Mapped[float] = mapped_column(nullable=False)

    order: Mapped["Order"] = relationship("Order", back_populates="lines")
