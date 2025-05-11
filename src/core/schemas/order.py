from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.utils.config import OrderStatus


class OrderLine(BaseModel):  # noqa: D101
    product_code: str = Field(..., description="Product code or SKU")
    description: str = Field(..., description="Product description")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit in EUR")
    subtotal: float = Field(..., description="Subtotal for this line")

    model_config = ConfigDict(from_attributes=True)


class Order(BaseModel):  # noqa: D101
    customer_name: str = Field(..., description="Name of the customer")
    customer_address: str = Field(..., description="Address of the customer")
    invoice_number: str = Field(..., description="Order or invoice number")
    order_date: str = Field(..., description="Order date as written in the document")
    due_date: str = Field(..., description="Due date or payment term")
    total_excl_vat: float = Field(..., description="Total amount excluding VAT in EUR")
    vat: float = Field(..., description="VAT amount in EUR")
    total_incl_vat: float = Field(..., description="Total amount including VAT in EUR")
    status: OrderStatus = Field(..., description="Order processing status")
    lines: list[OrderLine] = Field(..., description="Line items in the order")

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(Order):  # noqa: D101
    model_config = {"from_attributes": True}


class OrderUpdate(BaseModel):  # noqa: D101
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
    vat: float | None = Field(None, description="VAT amount in EUR")
    total_incl_vat: float | None = Field(
        None, description="Total amount including VAT in EUR"
    )
    status: OrderStatus | None = Field(None, description="Order processing status")
    lines: list[OrderLine] | None = Field(None, description="Line items in the order")

    model_config = {"extra": "forbid"}


class OrderResponse(Order):  # noqa: D101
    id: str
    created_at: datetime
    created_by: str  # user ID
