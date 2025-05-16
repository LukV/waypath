# core/utils/background.py

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.utils.process import process_uploaded_document

logger = logging.getLogger(__name__)


async def run_document_pipeline_background(
    db: AsyncSession,
    user: models.User,
    file_path: str,
    job_id: str,
) -> None:
    """Run the document pipeline in background."""
    try:
        await process_uploaded_document(
            db=db,
            user=user,
            file_path=Path(file_path),
            job_id=job_id,
        )
    except Exception:
        logger.exception(f"💥 Background task failed for {file_path}")
