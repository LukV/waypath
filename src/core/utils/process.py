import logging
import re
from pathlib import Path

import anyio
from fastapi import (
    HTTPException,
    UploadFile,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import jobs as crud_jobs
from api.crud import orders as crud_orders
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import job as job_schemas
from core.schemas import order as order_schemas
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.config import DEFAULT_MODEL, DEFAULT_PARSER, ObjectType
from core.utils.idsvc import generate_id

logger = logging.getLogger(__name__)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or injection."""
    filename = filename.strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def is_dangerous_file(filename: str) -> bool:
    """Block executable or suspicious file extensions."""
    forbidden_extensions = {".exe", ".bat", ".cmd", ".sh", ".js", ".php", ".py"}
    return Path(filename).suffix.lower() in forbidden_extensions


async def process_uploaded_order(
    db: AsyncSession,
    user: models.User,
    file: UploadFile | None = None,
    file_path: Path | None = None,
    lang: str = "en",
) -> order_schemas.OrderResponse:
    """Shared logic to process uploaded file and store resulting Order."""
    if file is not None:
        if is_dangerous_file(file.filename or "unknown"):
            logger.warning(f"⛔ Rejected dangerous file: {file.filename}")
            raise HTTPException(status_code=400, detail="Dangerous file type")
        tmp_path = Path(f"/tmp/{sanitize_filename(file.filename or 'unknown')}")  # noqa: S108
        async with await anyio.open_file(tmp_path, "wb") as f:
            content = await file.read()
            await f.write(content)
        delete_after = True
    elif file_path is not None:
        tmp_path = file_path
        delete_after = False
    else:
        raise ValueError("Provide file or file_path")  # noqa: TRY003

    try:
        parser = PARSER_REGISTRY[DEFAULT_PARSER](tmp_path, lang)
        extractor = EXTRACTOR_REGISTRY[DEFAULT_MODEL]()
        object_id = generate_id("O")
        job_id = generate_id("J")

        await crud_jobs.create_job(
            db,
            job_schemas.ProcessingJobCreate(
                id=job_id,
                file_name=tmp_path.name,
                created_by=user.id,
            ),
        )

        pipeline = DocumentPipeline(
            parser=parser,
            extractor=extractor,
            object_id=object_id,
            object_type=ObjectType.ORDER,
            db=db,
            job_id=job_id,
        )
        parsed_order = await pipeline.run()

        parsed_order_dict = parsed_order.model_dump()
        parsed_order_dict["file_name"] = tmp_path.name
        parsed_order_dict["id"] = object_id

        order_create = order_schemas.OrderCreate(**parsed_order_dict)
        created_order = await crud_orders.create_order(db, order_create, user)

        return order_schemas.OrderResponse.model_validate(
            created_order, from_attributes=True
        )
    finally:
        if delete_after:
            tmp_path.unlink(missing_ok=True)
