from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.utils.config import Currency, ObjectStatus


class OrderLine(BaseModel):
    """Order line schema for creating and updating order lines."""

    product_code: str = Field(..., description="Product code or SKU")
    description: str = Field(..., description="Product description")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit in EUR")
    subtotal: float = Field(..., description="Subtotal for this line")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):
    """Order schema for creating and updating orders."""

    customer_name: str = Field(..., description="Name of the customer")
    customer_address: str = Field(..., description="Address of the customer")
    invoice_number: str = Field(..., description="Order or invoice number")
    order_date: str = Field(..., description="Order date as written in the document")
    due_date: str = Field(..., description="Due date or payment term")
    total_excl_vat: float = Field(..., description="Total amount excluding VAT in EUR")
    currency: Currency = Field(..., description="Currency of the order")
    vat: float = Field(..., description="VAT amount in EUR")
    total_incl_vat: float = Field(..., description="Total amount including VAT in EUR")
    status: ObjectStatus = Field(..., description="Order processing status")
    lines: list[OrderLine] = Field(..., description="Line items in the order")

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(Order):
    """Order schema for creating new orders."""

    id: str | None = None
    file_name: str | None = Field(None, description="Filename of the source document")
    status: ObjectStatus = Field(ObjectStatus.TO_ACCEPT, description="Order status")

    model_config = {"from_attributes": True}


class OrderUpdate(BaseModel):
    """Order schema for updating existing orders."""

    customer_name: str | None = Field(None, description="Name of the customer")
    customer_address: str | None = Field(None, description="Address of the customer")
    invoice_number: str | None = Field(None, description="Order or invoice number")
    order_date: str | None = Field(
        None, description="Order date as written in the document"
    )
    due_date: str | None = Field(None, description="Due date or payment term")
    total_excl_vat: float | None = Field(
        None, description="Total amount excluding VAT in EUR"
    )
    currency: Currency | None = Field(None, description="Currency of the order")
    vat: float | None = Field(None, description="VAT amount in EUR")
    total_incl_vat: float | None = Field(
        None, description="Total amount including VAT in EUR"
    )
    status: ObjectStatus | None = Field(None, description="Order processing status")
    lines: list[OrderLine] | None = Field(None, description="Line items in the order")

    model_config = {"extra": "forbid"}


class OrderResponse(Order):
    """Order schema for returning order details."""

    id: str
    file_name: str | None
    created_at: datetime
    created_by: str  # user ID


class OrderCounts(BaseModel):  # noqa: D101
    total: int
    to_accept: int | None = 0
    accepted: int | None = 0
    archived: int | None = 0
    deleted: int | None = 0
    rejected: int | None = 0
    needs_review: int | None = 0
