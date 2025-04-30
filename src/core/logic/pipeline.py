from dataclasses import dataclass

from core.schemas.order import Order
from core.services.document_parser import DocumentParser
from core.services.structuring import OrderExtractor


@dataclass
class DocumentPipeline:
    """Pipeline service to parse and extract structured order data from a document."""

    parser: DocumentParser
    extractor: OrderExtractor

    async def run(self) -> Order:
        """Run the full pipeline: PDF → Markdown → Order.

        Args:
            path: Path to the PDF file.

        Returns:
            An Order object with extracted fields.

        """
        markdown = await self.parser.parse()
        return await self.extractor.extract_order(markdown)
