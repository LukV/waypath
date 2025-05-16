from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from core.schemas.classifier import DocumentType, DocumentTypePrediction
from core.services.classifiers.base import AbstractClassifier


class PydanticOpenAIClassifier(AbstractClassifier):
    """Classifier for document types using OpenAI's GPT model."""

    def __init__(self, model_name: str = "gpt-4o") -> None:  # noqa: D107
        provider = OpenAIProvider()
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=DocumentTypePrediction)

    async def classify(self, markdown: str) -> DocumentType:
        """Classify the document type based on the provided markdown text."""
        result = await self.agent.run(markdown)
        return result.output.document_type
