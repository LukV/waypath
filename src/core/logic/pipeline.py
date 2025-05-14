from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import jobs as crud_jobs
from core.schemas.job import ProcessingJobUpdate
from core.schemas.order import Order
from core.services.extractors.base import AbstractOrderExtractor
from core.services.parsers.base import AbstractDocumentParser
from core.utils.config import ObjectType, ProcessingStatus


@dataclass
class DocumentPipeline:
    """Pipeline to convert a document into structured order data.

    Uses a pluggable parser (PDF → Markdown) and extractor (Markdown → Order).
    """

    parser: AbstractDocumentParser
    extractor: AbstractOrderExtractor
    object_id: str | None = None
    object_type: ObjectType | None = None
    db: AsyncSession | None = None
    job_id: str | None = None

    async def run(self) -> Order:
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
            order = await self.extractor.extract_order(markdown)

            if self.db and self.job_id:
                await crud_jobs.update_job(
                    self.db,
                    self.job_id,
                    ProcessingJobUpdate(status=ProcessingStatus.SUCCESS),
                )

            return order  # noqa: TRY300

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
