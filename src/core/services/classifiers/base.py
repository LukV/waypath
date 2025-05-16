from abc import ABC, abstractmethod

from core.schemas.classifier import DocumentType


class AbstractClassifier(ABC):
    """Abstract base class for classifiers."""

    @abstractmethod
    async def classify(self, markdown: str) -> DocumentType:
        """Classify the document type based on the provided markdown text."""
        ...
