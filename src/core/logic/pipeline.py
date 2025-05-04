from dataclasses import dataclass

from core.schemas.order import Order
from core.services.extractors.base import AbstractOrderExtractor
from core.services.parsers.base import AbstractDocumentParser


@dataclass
class DocumentPipeline:
    """Pipeline to convert a document into structured order data.

    Uses a pluggable parser (PDF → Markdown) and extractor (Markdown → Order).
    """

    parser: AbstractDocumentParser
    extractor: AbstractOrderExtractor

    async def run(self) -> Order:
        """Run the pipeline."""
        markdown = await self.parser.parse()
        return await self.extractor.extract_order(markdown)
