from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import jobs as crud_jobs
from core.schemas.job import ProcessingJobUpdate
from core.services.extractors.base import AbstractExtractor
from core.services.parsers.base import AbstractDocumentParser
from core.utils.config import ObjectType, ProcessingStatus

T = TypeVar("T")


@dataclass
class DocumentPipeline(Generic[T]):
    """Pipeline to convert a document into structured data of type T."""

    parser: AbstractDocumentParser
    extractor: AbstractExtractor[T]
    object_id: str | None = None
    object_type: ObjectType | None = None
    db: AsyncSession | None = None
    job_id: str | None = None

    async def run(self) -> T:
        """Run the document processing pipeline and track job status if enabled."""
        if self.db and self.job_id:
            await crud_jobs.update_job(
                self.db,
                self.job_id,
                ProcessingJobUpdate(
                    status=ProcessingStatus.PROCESSING,
                    object_id=self.object_id,
                    object_type=self.object_type,
                ),
            )

        try:
            markdown = await self.parser.parse()
            result = await self.extractor.extract(markdown)

            if self.db and self.job_id:
                await crud_jobs.update_job(
                    self.db,
                    self.job_id,
                    ProcessingJobUpdate(status=ProcessingStatus.SUCCESS),
                )

            return result  # noqa: TRY300

        except Exception as e:
            if self.db and self.job_id:
                await crud_jobs.update_job(
                    self.db,
                    self.job_id,
                    ProcessingJobUpdate(
                        status=ProcessingStatus.FAILED,
                        error_message=str(e),
                        object_id=self.object_id,
                        object_type=self.object_type,
                    ),
                )
            raise
