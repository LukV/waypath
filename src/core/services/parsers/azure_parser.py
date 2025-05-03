from .base import AbstractDocumentParser


class AzureDocumentParser(AbstractDocumentParser):  # noqa: D101
    def __init__(self, path: str, language: str = "en") -> None:  # noqa: D107
        self.path = path
        self.language = language

    async def parse(self) -> str:
        """Parse a document using Azure Document Intelligence service."""
        # TODO(lve): Implement actual Azure Document  # noqa: FIX002, TD003
        # Intelligence logic
        raise NotImplementedError("Azure parser not implemented yet.")
