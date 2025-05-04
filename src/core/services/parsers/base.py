from abc import ABC, abstractmethod


class AbstractDocumentParser(ABC):  # noqa: D101
    @abstractmethod
    async def parse(self) -> str:  # noqa: D102
        pass
