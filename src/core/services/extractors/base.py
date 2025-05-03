from abc import ABC, abstractmethod

from core.schemas.order import Order


class AbstractOrderExtractor(ABC):  # noqa: D101
    @abstractmethod
    async def extract_order(self, markdown: str) -> Order:  # noqa: D102
        pass
