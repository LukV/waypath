# core/schemas/classifier.py
from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Enum for different document types."""

    ORDER = "order"
    INVOICE = "invoice"
    UNKNOWN = "unknown"


class DocumentTypePrediction(BaseModel):
    """Schema for document type prediction."""

    document_type: DocumentType = Field(..., description="Type of the document")
