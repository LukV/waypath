import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.utils.process import process_uploaded_invoice, process_uploaded_order

logger = logging.getLogger(__name__)

ENTITY_TASKS = {
    "order": process_uploaded_order,
    "invoice": process_uploaded_invoice,
}


async def run_document_pipeline_background(
    db: AsyncSession,
    user: models.User,
    file_path: str,
    entity: str,
    job_id: str,
) -> None:
    """Run the document pipeline in background."""
    try:
        processor = ENTITY_TASKS[entity]
        await processor(db=db, user=user, file_path=Path(file_path), job_id=job_id)
    except Exception:
        logger.exception(f"💥 Background task failed for {file_path}")
