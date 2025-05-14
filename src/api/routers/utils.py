import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import anyio
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.datastructures import UploadFile as StarletteUploadFile

from api.crud import users as crud_users
from core.schemas import order as order_schemas
from core.utils.database import get_db
from core.utils.process import (
    is_dangerous_file,
    process_uploaded_order,
    sanitize_filename,
)

load_dotenv()
router = APIRouter()
logger = logging.getLogger(__name__)

INBOX_ROOT = Path("inbox")
MAILGUN_SIGNING_KEY = os.environ["MAILGUN_SIGNING_KEY"]


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
