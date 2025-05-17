from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from core.crud import jobs as crud_jobs
from core.schemas.classifier import DocumentType
from core.schemas.job import ProcessingJobUpdate
from core.services.extractors.base import AbstractExtractor
from core.services.factories import CLASSIFIER_REGISTRY, EXTRACTOR_REGISTRY
from core.services.parsers.base import AbstractDocumentParser
from core.utils.config import DEFAULT_MODEL, ProcessingStatus

T = TypeVar("T")


@dataclass
class DocumentPipeline(Generic[T]):
    """Pipeline to convert a document into structured data of type T."""

    parser: AbstractDocumentParser
    extractor: AbstractExtractor[T] | None = None
    document_type: DocumentType | None = None
    db: AsyncSession | None = None
    job_id: str | None = None

    async def run(self) -> tuple[T, DocumentType]:
        """Run the document processing pipeline and track job status if enabled."""
        if self.db and self.job_id:
            await crud_jobs.update_job(
                self.db,
                self.job_id,
                ProcessingJobUpdate(status=ProcessingStatus.PROCESSING),
            )

        try:
            # Parse the document to extract markdown text
            markdown = await self.parser.parse()

            # If the document_type is not set, classify the document type
            if self.extractor is None or self.document_type is None:
                classifier = CLASSIFIER_REGISTRY[DEFAULT_MODEL]()
                predicted_type = await classifier.classify(markdown)

                if predicted_type == DocumentType.UNKNOWN or None:
                    raise ValueError("❌ Could not determine document type")  # noqa: TRY003, TRY301

                self.document_type = predicted_type

            # Extract structured data from the markdown text
            self.extractor = EXTRACTOR_REGISTRY[
                (DEFAULT_MODEL, self.document_type.value)
            ]()

            result = await self.extractor.extract(markdown)

            if self.db and self.job_id:
                await crud_jobs.update_job(
                    self.db,
                    self.job_id,
                    ProcessingJobUpdate(status=ProcessingStatus.SUCCESS),
                )

            return result, self.document_type  # noqa: TRY300

        except Exception as e:
            if self.db and self.job_id:
                await crud_jobs.update_job(
                    self.db,
                    self.job_id,
                    ProcessingJobUpdate(
                        status=ProcessingStatus.FAILED, error_message=str(e)
                    ),
                )
            raise
