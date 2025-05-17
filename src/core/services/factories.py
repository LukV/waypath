from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.crud.invoices import create_invoice
from core.crud.orders import create_order
from core.db import models
from core.schemas.classifier import DocumentType
from core.schemas.invoice import InvoiceCreate, InvoiceResponse
from core.schemas.order import OrderCreate, OrderResponse
from core.services.classifiers.azure_openai import PydanticAzureClassifier
from core.services.classifiers.base import AbstractClassifier
from core.services.classifiers.openai import PydanticOpenAIClassifier
from core.services.extractors.azure_openai import (
    PydanticAzureExtractor,
    PydanticAzureInvoiceExtractor,
)
from core.services.extractors.base import AbstractExtractor
from core.services.extractors.openai import (
    PydanticOpenAIExtractor,
    PydanticOpenAIInvoiceExtractor,
)
from core.services.parsers.azure_parser import AzureDocumentParser
from core.services.parsers.base import AbstractDocumentParser
from core.services.parsers.llamaparse_parser import LlamaParseParser

T = TypeVar("T")

PARSER_REGISTRY: dict[str, Callable[[Path, str], AbstractDocumentParser]] = {
    "llamaparse": lambda path, lang: LlamaParseParser(path=Path(path), language=lang),
    "azure": lambda path, lang: AzureDocumentParser(path=Path(path), language=lang),
}

EXTRACTOR_REGISTRY: dict[tuple[str, str], Callable[[], AbstractExtractor[Any]]] = {
    ("openai", "order"): lambda: PydanticOpenAIExtractor(),
    ("azure", "order"): lambda: PydanticAzureExtractor(),
    ("openai", "invoice"): lambda: PydanticOpenAIInvoiceExtractor(),
    ("azure", "invoice"): lambda: PydanticAzureInvoiceExtractor(),
}

CLASSIFIER_REGISTRY: dict[str, Callable[[], AbstractClassifier]] = {
    "openai": PydanticOpenAIClassifier,
    "azure": PydanticAzureClassifier,
}

CREATE_FN_REGISTRY: dict[
    DocumentType, Callable[[AsyncSession, BaseModel, models.User], Any]
] = {
    DocumentType.ORDER: create_order,  # type: ignore  # noqa: PGH003
    DocumentType.INVOICE: create_invoice,  # type: ignore  # noqa: PGH003
}

CREATE_SCHEMA_REGISTRY: dict[DocumentType, type[OrderCreate | InvoiceCreate]] = {
    DocumentType.ORDER: OrderCreate,
    DocumentType.INVOICE: InvoiceCreate,
}

RESPONSE_SCHEMA_REGISTRY: dict[DocumentType, type[BaseModel]] = {
    DocumentType.ORDER: OrderResponse,
    DocumentType.INVOICE: InvoiceResponse,
}
