import logging
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import anyio
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile

from api.crud import orders as crud_orders
from api.crud import users as crud_users
from core.logic.pipeline import DocumentPipeline
from core.schemas import order as order_schemas
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.database import get_db

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

INBOX_ROOT = Path("inbox")
MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
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
    except Exception:  # noqa: BLE001
        return False


def sanitize_filename(filename: str) -> str:
    """Sanitize filename to prevent path traversal or injection."""
    filename = filename.strip().replace("\\", "_").replace("/", "_")
    return re.sub(r"[^a-zA-Z0-9._-]", "_", filename)


def is_dangerous_file(filename: str) -> bool:
    """Block executable or suspicious file extensions."""
    forbidden_extensions = {".exe", ".bat", ".cmd", ".sh", ".js", ".php", ".py"}
    return Path(filename).suffix.lower() in forbidden_extensions


@router.post("/inbound-email")
async def receive(  # noqa: PLR0913
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    sender: Annotated[str | None, Form()] = None,
    recipient: Annotated[str | None, Form()] = None,  # noqa: ARG001
    subject: Annotated[str | None, Form()] = None,
    body_plain: Annotated[str | None, Form()] = None,  # noqa: ARG001
    body_html: Annotated[str | None, Form()] = None,  # noqa: ARG001
) -> order_schemas.OrderResponse:
    """Process incoming email data and securely save attachments."""
    logger.info("✅ Received inbound email from %s", sender)

    if not sender or not subject:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required email fields: sender and subject are required",
        )

    form = await request.form()

    timestamp = str(form.get("timestamp"))
    token = str(form.get("token"))
    signature = str(form.get("signature"))

    if not is_valid_mailgun_signature(MAILGUN_API_KEY, timestamp, token, signature):
        logger.warning("🚫 Invalid Mailgun signature")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid signature"
        )

    logger.info(f"📧 From: {sender}")
    logger.info(f"📨 Subject: {subject}")

    timestamp = datetime.now(tz=UTC).strftime("%Y%m%d-%H%M%S")
    inbox_path = INBOX_ROOT / timestamp
    inbox_path.mkdir(parents=True, exist_ok=True)

    for _, value in form.multi_items():
        if isinstance(value, UploadFile):
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

            # Apply the parsing pipeline (only on first valid file)
            try:
                parser = PARSER_REGISTRY[DEFAULT_PARSER](file_path, "en")
                extractor = EXTRACTOR_REGISTRY[DEFAULT_MODEL]()
                pipeline = DocumentPipeline(parser=parser, extractor=extractor)
                parsed_order = await pipeline.run()

                # Store in DB
                order_create = order_schemas.OrderCreate(**parsed_order.model_dump())
                user = await crud_users.get_user_by_email(db, sender)
                if user is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                    )
                created_order = await crud_orders.create_order(db, order_create, user)

                return order_schemas.OrderResponse.model_validate(
                    created_order, from_attributes=True
                )
            finally:
                file_path.unlink(missing_ok=True)

    raise HTTPException(status_code=422, detail="No valid attachments found")
