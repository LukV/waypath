import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import anyio
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from api.crud import orders as crud_orders
from api.crud import users as crud_users
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import order as order_schemas
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.auth import get_current_user
from core.utils.database import get_db
from core.utils.idsvc import generate_id

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

INBOX_ROOT = Path("inbox")
MAILGUN_SIGNING_KEY = os.environ["MAILGUN_SIGNING_KEY"]
DEFAULT_PARSER = "llamaparse"
DEFAULT_MODEL = "openai"


def is_valid_mailgun_signature(
    api_key: str, timestamp: str, token: str, signature: str
) -> bool:
    """Validate a Mailgun webhook signature."""
    import hashlib
    import hmac

    try:
        message = f"{timestamp}{token}".encode()
        key = api_key.encode("utf-8")
        expected = hmac.new(key, message, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    except (ValueError, TypeError):
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or injection."""
    filename = filename.strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def is_dangerous_file(filename: str) -> bool:
    """Block executable or suspicious file extensions."""
    forbidden_extensions = {".exe", ".bat", ".cmd", ".sh", ".js", ".php", ".py"}
    return Path(filename).suffix.lower() in forbidden_extensions


@router.post("/inbound-email", response_model=list[order_schemas.OrderResponse])
async def receive(  # noqa: PLR0913
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    sender: Annotated[str | None, Form()] = None,
    recipient: Annotated[str | None, Form()] = None,  # noqa: ARG001
    subject: Annotated[str | None, Form()] = None,
    body_plain: Annotated[str | None, Form()] = None,  # noqa: ARG001
    body_html: Annotated[str | None, Form()] = None,  # noqa: ARG001
) -> list[order_schemas.OrderResponse]:
    """Process incoming email and parse all valid attachments."""
    logger.info("✅ Received inbound email from %s", sender)

    if not sender or not subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required email fields: sender and subject are required",
        )

    form = await request.form()
    if not is_valid_mailgun_signature(
        MAILGUN_SIGNING_KEY,
        str(form.get("timestamp")),
        str(form.get("token")),
        str(form.get("signature")),
    ):
        logger.warning("🚫 Invalid Mailgun signature")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature"
        )

    user = await crud_users.get_user_by_email(db, sender)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    inbox_path = INBOX_ROOT / datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    inbox_path.mkdir(parents=True, exist_ok=True)

    results = []

    for _, value in form.multi_items():
        if isinstance(value, StarletteUploadFile):
            raw_name = value.filename or "attachment.bin"
            filename = sanitize_filename(raw_name)

            if is_dangerous_file(filename):
                logger.warning(f"⛔ Rejected dangerous file: {filename}")
                continue

            file_path = inbox_path / filename
            async with await anyio.open_file(file_path, "wb") as f:
                content = await value.read()
                await f.write(content)

            logger.info(f"📎 Saved attachment: {file_path}")

            try:
                order = await process_uploaded_order(
                    db=db, user=user, file_path=file_path
                )
                results.append(order)
            finally:
                file_path.unlink(missing_ok=True)

    if not results:
        raise HTTPException(status_code=422, detail="No valid attachments found")

    return results


@router.post("/upload", response_model=order_schemas.OrderResponse)
async def upload_order_from_web(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> order_schemas.OrderResponse:
    """Support authenticated frontend users uploading a document."""
    logger.info("🌐 Received upload from %s", current_user.email)
    return await process_uploaded_order(file=file, db=db, user=current_user)


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
        pipeline = DocumentPipeline(parser=parser, extractor=extractor)
        parsed_order = await pipeline.run()

        parsed_order_dict = parsed_order.model_dump()
        parsed_order_dict["file_name"] = tmp_path.name
        parsed_order_dict["id"] = generate_id("O")

        order_create = order_schemas.OrderCreate(**parsed_order_dict)
        created_order = await crud_orders.create_order(db, order_create, user)

        return order_schemas.OrderResponse.model_validate(
            created_order, from_attributes=True
        )
    finally:
        if delete_after:
            tmp_path.unlink(missing_ok=True)
