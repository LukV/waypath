import logging
import re
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import TypeVar

import anyio
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import invoices as crud_invoices
from api.crud import orders as crud_orders
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import invoice as invoice_schemas
from core.schemas import order as order_schemas
from core.services.extractors.base import AbstractExtractor
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.config import DEFAULT_MODEL, DEFAULT_PARSER, ObjectType
from core.utils.database import Base
from core.utils.idsvc import generate_id

logger = logging.getLogger(__name__)

T = TypeVar("T")

TCreate = TypeVar("TCreate", bound=BaseModel)
TResponse = TypeVar("TResponse", bound=BaseModel)
TSchema = TypeVar("TSchema", bound=BaseModel)
TOrm = TypeVar("TOrm", bound=Base)


def sanitize_filename(filename: str) -> str:
    """Sanitize the filename to remove any dangerous characters."""
    filename = filename.strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def is_dangerous_file(filename: str) -> bool:
    """Check if the file has a dangerous extension."""
    forbidden_extensions = {".exe", ".bat", ".cmd", ".sh", ".js", ".php", ".py"}
    return Path(filename).suffix.lower() in forbidden_extensions


async def process_uploaded_document(  # noqa: PLR0913
    *,
    db: AsyncSession,
    user: models.User,
    object_type: ObjectType,
    extractor: AbstractExtractor[TSchema],
    create_fn: Callable[[AsyncSession, TCreate, models.User], Awaitable[Base]],
    schema_create: type[TCreate],
    schema_response: type[TResponse],
    job_id: str,
    file: UploadFile | None = None,
    file_path: Path | None = None,
    lang: str = "en",
    prefix: str = "D",
) -> TResponse:
    """Process an uploaded document and create in the database."""
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
        object_id = generate_id(prefix)

        pipeline = DocumentPipeline[TSchema](
            parser=PARSER_REGISTRY[DEFAULT_PARSER](tmp_path, lang),
            extractor=extractor,
            object_id=object_id,
            object_type=object_type,
            db=db,
            job_id=job_id,
        )
        parsed_entity: TSchema = await pipeline.run()
        parsed_dict = parsed_entity.model_dump()
        parsed_dict["file_name"] = tmp_path.name
        parsed_dict["id"] = object_id

        created = await create_fn(db, schema_create(**parsed_dict), user)
        return schema_response.model_validate(created, from_attributes=True)
    finally:
        if delete_after:
            tmp_path.unlink(missing_ok=True)


async def process_uploaded_order(  # noqa: PLR0913
    db: AsyncSession,
    user: models.User,
    job_id: str,
    file: UploadFile | None = None,
    file_path: Path | None = None,
    lang: str = "en",
) -> order_schemas.OrderResponse:
    """Process an uploaded order document."""
    if file_path is None:
        raise ValueError("file_path cannot be None")  # noqa: TRY003
    extractor = EXTRACTOR_REGISTRY[(DEFAULT_MODEL, "order")]()
    return await process_uploaded_document(
        db=db,
        user=user,
        object_type=ObjectType.ORDER,
        extractor=extractor,
        create_fn=crud_orders.create_order,
        schema_create=order_schemas.OrderCreate,
        schema_response=order_schemas.OrderResponse,
        file=file,
        file_path=file_path,
        lang=lang,
        prefix="O",
        job_id=job_id,
    )


async def process_uploaded_invoice(  # noqa: PLR0913
    db: AsyncSession,
    user: models.User,
    job_id: str,
    file: UploadFile | None = None,
    file_path: Path | None = None,
    lang: str = "en",
) -> invoice_schemas.InvoiceResponse:
    """Process an uploaded invoice document."""
    if file_path is None:
        raise ValueError("file_path cannot be None")  # noqa: TRY003
    extractor = EXTRACTOR_REGISTRY[(DEFAULT_MODEL, "invoice")]()
    return await process_uploaded_document(
        db=db,
        user=user,
        object_type=ObjectType.INVOICE,
        extractor=extractor,
        create_fn=crud_invoices.create_invoice,
        schema_create=invoice_schemas.InvoiceCreate,
        schema_response=invoice_schemas.InvoiceResponse,
        file=file,
        file_path=file_path,
        lang=lang,
        prefix="I",
        job_id=job_id,
    )
