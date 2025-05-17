from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from core.utils.config import ObjectStatus, ProcessingStatus
from core.utils.database import Base


class User(Base):
    """User model for storing user information."""

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
    invoices: Mapped[list["Invoice"]] = relationship("Invoice", back_populates="user")


class Order(Base):
    """Order model for storing order details."""

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
        "OrderLine",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    status: Mapped[ObjectStatus] = mapped_column(
        SqlEnum(ObjectStatus, name="objectstatus"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="orders")


class OrderLine(Base):
    """Order line model for storing line items in an order."""

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


class Invoice(Base):
    """Invoice model for storing invoice details."""

    __tablename__ = "invoices"

    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    file_name: Mapped[str] = mapped_column(String, nullable=True)
    supplier_name: Mapped[str] = mapped_column(String, nullable=False)
    supplier_address: Mapped[str] = mapped_column(String, nullable=False)
    supplier_vat_number: Mapped[str] = mapped_column(String, nullable=False)
    invoice_number: Mapped[str] = mapped_column(String, index=True, nullable=False)
    invoice_date: Mapped[str] = mapped_column(String, nullable=False)
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

    lines: Mapped[list["InvoiceLine"]] = relationship(
        "InvoiceLine",
        back_populates="invoice",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    status: Mapped[ObjectStatus] = mapped_column(
        SqlEnum(ObjectStatus, name="objectstatus"), nullable=False
    )
    user: Mapped["User"] = relationship("User", back_populates="invoices")


class InvoiceLine(Base):
    """Invoice line model for storing line items in an invoice."""

    __tablename__ = "invoice_lines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_id: Mapped[str] = mapped_column(
        String, ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False
    )

    description: Mapped[str] = mapped_column(String, nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[float] = mapped_column(nullable=False)
    subtotal: Mapped[float] = mapped_column(nullable=False)

    invoice: Mapped["Invoice"] = relationship("Invoice", back_populates="lines")


class ProcessingJob(Base):
    """Processing job model for tracking file processing status."""

    __tablename__ = "processing_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(
        SqlEnum(ProcessingStatus, name="processingstatus"),
        nullable=True,
        default=ProcessingStatus.PENDING,
    )
    file_name: Mapped[str] = mapped_column(String, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String, nullable=True)
    created_by: Mapped[str] = mapped_column(
        String, ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
