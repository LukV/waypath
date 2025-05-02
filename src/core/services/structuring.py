from pydantic_ai import Agent

from core.schemas.order import Order


class OrderExtractor:
    """Service for structuring Markdown content into an Order Pydantic model."""

    def __init__(self) -> None:  # noqa: D107
        self.agent = Agent(
            "openai:gpt-4o",
            output_type=Order,
            system_prompt="Extract structured order information from the \
                following Markdown.",
        )

    async def extract_order(self, markdown: str) -> Order:
        """Parse Markdown into a structured Order object using an LLM.

        Args:
            markdown: A string of Markdown content from the parsed PDF.

        Returns:
            An Order Pydantic model populated from the Markdown content.

        """
        result = await self.agent.run(markdown)
        return result.output
