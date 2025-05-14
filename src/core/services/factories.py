from collections.abc import Callable
from pathlib import Path
from typing import Any, TypeVar

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

# Parser registry remains unchanged
PARSER_REGISTRY: dict[str, Callable[[Path, str], AbstractDocumentParser]] = {
    "llamaparse": lambda path, lang: LlamaParseParser(path=Path(path), language=lang),
    "azure": lambda path, lang: AzureDocumentParser(path=Path(path), language=lang),
}

# Extractor registry is now typed per (model, entity) pair
EXTRACTOR_REGISTRY: dict[tuple[str, str], Callable[[], AbstractExtractor[Any]]] = {
    ("openai", "order"): lambda: PydanticOpenAIExtractor(),
    ("azure", "order"): lambda: PydanticAzureExtractor(),
    ("openai", "invoice"): lambda: PydanticOpenAIInvoiceExtractor(),
    ("azure", "invoice"): lambda: PydanticAzureInvoiceExtractor(),
}
