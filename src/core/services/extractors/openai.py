from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from core.schemas.invoice import Invoice
from core.schemas.order import Order
from core.services.extractors.base import AbstractExtractor


class PydanticOpenAIExtractor(AbstractExtractor[Order]):
    """Extractor for orders using OpenAI's GPT model."""

    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        provider = OpenAIProvider()
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=Order)

    async def extract(self, markdown: str) -> Order:
        """Extract an order from the provided markdown string using the agent."""
        result = await self.agent.run(markdown)
        return result.output


class PydanticOpenAIInvoiceExtractor(AbstractExtractor[Invoice]):
    """Extractor for invoices using OpenAI's GPT model."""

    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        provider = OpenAIProvider()
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=Invoice)

    async def extract(self, markdown: str) -> Invoice:
        """Extract an invoice from the provided markdown string using the agent."""
        result = await self.agent.run(markdown)
        return result.output
