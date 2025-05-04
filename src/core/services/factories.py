from collections.abc import Callable
from pathlib import Path

from core.services.extractors.azure_openai import PydanticAzureExtractor
from core.services.extractors.base import AbstractOrderExtractor
from core.services.extractors.openai import PydanticOpenAIExtractor
from core.services.parsers.azure_parser import AzureDocumentParser
from core.services.parsers.base import AbstractDocumentParser
from core.services.parsers.llamaparse_parser import LlamaParseParser

PARSER_REGISTRY: dict[str, Callable[[Path, str], AbstractDocumentParser]] = {
    "llamaparse": lambda path, lang: LlamaParseParser(path=Path(path), language=lang),
    "azure": lambda path, lang: AzureDocumentParser(path=Path(path), language=lang),
}

EXTRACTOR_REGISTRY: dict[str, type[AbstractOrderExtractor]] = {
    "openai": PydanticOpenAIExtractor,
    "azure": PydanticAzureExtractor,
}
