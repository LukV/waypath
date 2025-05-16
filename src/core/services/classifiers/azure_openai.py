import os

from openai import AsyncAzureOpenAI
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from core.schemas.classifier import DocumentType, DocumentTypePrediction
from core.services.classifiers.base import AbstractClassifier


class PydanticAzureClassifier(AbstractClassifier):
    """Classifier for document types using Azure OpenAI's GPT model."""

    def __init__(self, model_name: str = "gpt-4o") -> None:
        """Initialize the classifier with the specified model name."""
        client = AsyncAzureOpenAI(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            api_version="2024-07-01-preview",
            azure_deployment="gpt-4",
        )
        provider = OpenAIProvider(openai_client=client)
        model = OpenAIModel(model_name, provider=provider)
        self.agent = Agent(model, output_type=DocumentTypePrediction)

    async def classify(self, markdown: str) -> DocumentType:
        """Classify the document type based on the provided markdown text."""
        result = await self.agent.run(markdown)
        return result.output.document_type
