import os
from pathlib import Path

from llama_cloud_services import LlamaParse  # type: ignore[import-untyped]

LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")


class DocumentParser:
    """Service for converting PDF documents to Markdown using LlamaParse."""

    def __init__(self, path: Path, language: str = "en") -> None:
        """Initialize the parser with language and optional API key."""
        self.parser = LlamaParse(
            api_key=LLAMA_CLOUD_API_KEY,
            language=language,
            num_workers=4,
            verbose=True,
        )
        self.path = path

    async def parse(self) -> str:
        """Parse a document and return the concatenated Markdown output.

        Args:
            path: Path to the file.

        Returns:
            A single Markdown string representing the document.

        """
        result = await self.parser.aparse(self.path)
        markdown_documents = result.get_markdown_documents(split_by_page=True)
        return "\n\n".join(doc.text for doc in markdown_documents)
