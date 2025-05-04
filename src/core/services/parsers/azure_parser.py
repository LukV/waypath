import os
from io import BytesIO
from pathlib import Path

import anyio
from azure.ai.formrecognizer.aio import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

from .base import AbstractDocumentParser

SUPPORTED_AZURE_FORMATS = {".pdf", ".jpg", ".jpeg", ".png", ".tiff", ".bmp"}


class AzureDocumentParser(AbstractDocumentParser):
    """Azure Document Intelligence parser returning Markdown text."""

    def __init__(self, path: Path, language: str = "en") -> None:  # noqa: D107
        self.path = path
        self.language = language

        # Validate supported file format
        if self.path.suffix.lower() not in SUPPORTED_AZURE_FORMATS:
            msg = f"Unsupported file format for \
                    AzureDocumentParser: '{self.path.suffix}'. \
                        Supported formats are: {', '.join(SUPPORTED_AZURE_FORMATS)}."
            raise ValueError(msg)

        self.endpoint = os.environ["AZURE_DI_ENDPOINT"]
        self.key = os.environ["AZURE_DI_KEY"]
        self.client = DocumentAnalysisClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.key),
        )

    async def parse(self) -> str:
        """Asynchronously parse a PDF using Azure Form Recognizer
        and return markdown.
        """
        async with await anyio.open_file(self.path, "rb") as f:
            file_bytes = await f.read()

        # Wrap the bytes in a stream — this avoids double content_type injection
        stream = BytesIO(file_bytes)

        poller = await self.client.begin_analyze_document(
            model_id="prebuilt-layout",
            document=stream,
        )
        result = await poller.result()

        markdown = []
        for page in result.pages:
            markdown.append(f"# Page {page.page_number}\n")
            markdown.extend([line.content for line in page.lines])
            markdown.append("\n")

        return "\n".join(markdown)
