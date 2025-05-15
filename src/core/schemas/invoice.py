from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.utils.config import ObjectStatus


class InvoiceLine(BaseModel):
    """Represents a line item in an invoice."""

    description: str
    quantity: int
    unit_price: float
    subtotal: float

    model_config = ConfigDict(from_attributes=True)


class Invoice(BaseModel):
    """Represents an invoice with its details."""

    supplier_name: str = Field(..., description="Name of the supplier")
    supplier_address: str = Field(..., description="Address of the supplier")
    supplier_vat_number: str = Field(..., description="VAT number of the supplier")
    invoice_number: str = Field(..., description="Invoice number")
    invoice_date: str = Field(
        ..., description="Invoice date as written in the document"
    )
    due_date: str = Field(..., description="Due date or payment term")
    total_excl_vat: float = Field(..., description="Total amount excluding VAT")
    vat: float = Field(..., description="VAT amount")
    total_incl_vat: float = Field(..., description="Total amount including VAT")
    lines: list[InvoiceLine] = Field(..., description="Line items in the invoice")

    model_config = ConfigDict(from_attributes=True)


class InvoiceCreate(Invoice):
    """Invoice schema for creating new invoices."""

    id: str | None = None
    file_name: str | None = Field(None, description="Filename of the source document")
    status: ObjectStatus = Field(ObjectStatus.TO_ACCEPT, description="Object status")

    model_config = {"from_attributes": True}


class InvoiceUpdate(BaseModel):
    """Invoice schema for updating existing invoices."""

    customer_name: str | None = Field(None, description="Name of the customer")
    customer_address: str | None = Field(None, description="Address of the customer")
    invoice_number: str | None = Field(None, description="Invoice or invoice number")
    Invoice_date: str | None = Field(
        None, description="Invoice date as written in the document"
    )
    due_date: str | None = Field(None, description="Due date or payment term")
    total_excl_vat: float | None = Field(
        None, description="Total amount excluding VAT in EUR"
    )
    vat: float | None = Field(None, description="VAT amount in EUR")
    total_incl_vat: float | None = Field(
        None, description="Total amount including VAT in EUR"
    )
    status: ObjectStatus | None = Field(None, description="Invoice processing status")
    lines: list[InvoiceLine] | None = Field(
        None, description="Line items in the invoice"
    )

    model_config = {"extra": "forbid"}


class InvoiceResponse(Invoice):
    """Response model for an invoice."""

    id: str
    file_name: str | None
    created_at: datetime
    created_by: str


class InvoiceCounts(BaseModel):  # noqa: D101
    total: int
    to_accept: int | None = 0
    accepted: int | None = 0
    archived: int | None = 0
    deleted: int | None = 0
    rejected: int | None = 0
    needs_review: int | None = 0
