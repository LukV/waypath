from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from core.schemas.order import Order

from .base import AbstractOrderExtractor


class PydanticOpenAIExtractor(AbstractOrderExtractor):  # noqa: D101
    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        provider = OpenAIProvider()
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=Order)

    async def extract_order(self, markdown: str) -> Order:
        """Extract an order from the provided markdown string using the agent."""
        result = await self.agent.run(markdown)
        return result.output
