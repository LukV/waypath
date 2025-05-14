from datetime import datetime

from pydantic import BaseModel


class InvoiceLine(BaseModel):
    """Represents a line item in an invoice."""

    description: str
    quantity: int
    unit_price: float
    subtotal: float


class Invoice(BaseModel):
    """Represents an invoice with its details."""

    supplier_vat: str
    invoice_number: str
    invoice_date: str
    due_date: str
    total_excl_vat: float
    vat: float
    total_incl_vat: float
    lines: list[InvoiceLine]


class InvoiceResponse(Invoice):
    """Response model for an invoice."""

    id: str
    file_name: str | None
    created_at: datetime
    created_by: str
