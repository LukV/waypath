import os
from pathlib import Path

from llama_cloud_services import LlamaParse

from .base import AbstractDocumentParser

LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")


class LlamaParseParser(AbstractDocumentParser):  # noqa: D101
    def __init__(self, path: Path, language: str = "en") -> None:  # noqa: D107
        self.parser = LlamaParse(
            api_key=LLAMA_CLOUD_API_KEY,
            language=language,
            num_workers=4,
            verbose=True,
        )
        self.path = path

    async def parse(self) -> str:
        """Parse a document into markdown text."""
        result = await self.parser.aparse(self.path)
        markdown_documents = result.get_markdown_documents(split_by_page=True)
        return "\n\n".join(doc.text for doc in markdown_documents)
