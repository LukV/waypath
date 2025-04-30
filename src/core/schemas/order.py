from pydantic import BaseModel, Field


class OrderLine(BaseModel):  # noqa: D101
    product_code: str = Field(..., description="Product code or SKU")
    description: str = Field(..., description="Product description")
    quantity: int = Field(..., description="Quantity ordered")
    unit_price: float = Field(..., description="Price per unit in EUR")
    subtotal: float = Field(..., description="Subtotal for this line")


class Order(BaseModel):  # noqa: D101
    customer_name: str = Field(..., description="Name of the customer")
    customer_address: str = Field(..., description="Address of the customer")
    invoice_number: str = Field(..., description="Order or invoice number")
    order_date: str = Field(..., description="Order date as written in the document")
    due_date: str = Field(..., description="Due date or payment term")
    total_excl_vat: float = Field(..., description="Total amount excluding VAT in EUR")
    vat: float = Field(..., description="VAT amount in EUR")
    total_incl_vat: float = Field(..., description="Total amount including VAT in EUR")
    lines: list[OrderLine] = Field(..., description="Line items in the order")
