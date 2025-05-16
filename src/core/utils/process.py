import logging
import re
from pathlib import Path
from typing import Any, TypeVar

import anyio
from fastapi import HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas.classifier import DocumentType
from core.services.factories import (
    CREATE_FN_REGISTRY,
    CREATE_SCHEMA_REGISTRY,
    PARSER_REGISTRY,
    RESPONSE_SCHEMA_REGISTRY,
)
from core.utils.config import DEFAULT_PARSER
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
    job_id: str,
    file: UploadFile | None = None,
    file_path: Path | None = None,
    lang: str = "en",
    prefix_map: dict[DocumentType, str] = {  # noqa: B006
        DocumentType.ORDER: "O",
        DocumentType.INVOICE: "I",
    },
) -> BaseModel:
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
        pipeline: DocumentPipeline[Any] = DocumentPipeline(
            parser=PARSER_REGISTRY[DEFAULT_PARSER](tmp_path, lang),
            db=db,
            job_id=job_id,
        )
        parsed_entity, document_type = await pipeline.run()

        if document_type is None:
            raise ValueError("❌ Document type could not be determined")  # noqa: TRY003

        parsed_dict = parsed_entity.model_dump()
        parsed_dict["file_name"] = tmp_path.name
        parsed_dict["id"] = generate_id(prefix_map[document_type])

        create_fn = CREATE_FN_REGISTRY[document_type]
        schema_create = CREATE_SCHEMA_REGISTRY[document_type](**parsed_dict)
        created = await create_fn(db, schema_create, user)

        schema_response = RESPONSE_SCHEMA_REGISTRY[document_type]
        return schema_response.model_validate(created, from_attributes=True)

    finally:
        if delete_after:
            tmp_path.unlink(missing_ok=True)
