from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")


class AbstractExtractor(ABC, Generic[T]):
    """Abstract base class for extractors."""

    @abstractmethod
    async def extract(self, markdown: str) -> T:
        """Extract structured data of type T from markdown."""
