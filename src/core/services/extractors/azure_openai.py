import os

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from core.schemas.invoice import Invoice
from core.schemas.order import Order
from core.services.extractors.base import AbstractExtractor


class PydanticAzureExtractor(AbstractExtractor[Order]):  # noqa: D101
    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        # Log the environment vars (only safe ones!)
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-07-01-preview",
            azure_deployment="gpt-4",
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=Order)

    async def extract(self, markdown: str) -> Order:
        """Extract order information from markdown text using an AI agent."""
        result = await self.agent.run(markdown)
        return result.output


class PydanticAzureInvoiceExtractor(AbstractExtractor[Invoice]):  # noqa: D101
    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        # Log the environment vars (only safe ones!)
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-07-01-preview",
            azure_deployment="gpt-4",
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=Invoice)

    async def extract(self, markdown: str) -> Invoice:
        """Extract order information from markdown text using an AI agent."""
        result = await self.agent.run(markdown)
        return result.output
