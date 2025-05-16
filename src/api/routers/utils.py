import logging
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, cast

import anyio
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    BackgroundTasks,
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

from api.crud import jobs as crud_jobs
from api.crud import users as crud_users
from core.db import models
from core.schemas import job as job_schemas
from core.schemas.invoice import InvoiceResponse
from core.schemas.order import OrderResponse
from core.utils.auth import get_current_user
from core.utils.background import run_document_pipeline_background
from core.utils.database import get_db
from core.utils.idsvc import generate_id
from core.utils.process import (
    is_dangerous_file,
    process_uploaded_document,
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


@router.post("/inbound-email", response_model=list[OrderResponse | InvoiceResponse])
async def receive(  # noqa: PLR0913
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    sender: Annotated[str | None, Form()] = None,
    recipient: Annotated[str | None, Form()] = None,  # noqa: ARG001
    subject: Annotated[str | None, Form()] = None,
    body_plain: Annotated[str | None, Form()] = None,  # noqa: ARG001
    body_html: Annotated[str | None, Form()] = None,  # noqa: ARG001
) -> list[OrderResponse | InvoiceResponse]:
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

    results: list[OrderResponse | InvoiceResponse] = []

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
                job_id = generate_id("J")

                await crud_jobs.create_job(
                    db,
                    job_schemas.ProcessingJobCreate(
                        id=job_id,
                        file_name=filename,
                        created_by=user.id,
                    ),
                )

                parsed = await process_uploaded_document(
                    db=db, user=user, job_id=job_id, file_path=file_path
                )

                results.append(cast("OrderResponse | InvoiceResponse", parsed))

            finally:
                file_path.unlink(missing_ok=True)

    if not results:
        raise HTTPException(status_code=422, detail="No valid attachments found")

    return results


@router.post("/upload")
async def upload_order_from_web(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
) -> job_schemas.JobQueuedResponse:
    """Support authenticated frontend users uploading a document asynchronously."""
    logger.info("🌐 Upload received from %s", current_user.email)

    filename = sanitize_filename(file.filename or "upload.pdf")
    tmp_path = Path(f"/tmp/{filename}")  # noqa: S108

    async with await anyio.open_file(tmp_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    job_id = generate_id("J")

    await crud_jobs.create_job(
        db,
        job_schemas.ProcessingJobCreate(
            id=job_id,
            file_name=tmp_path.name,
            created_by=current_user.id,
        ),
    )

    background_tasks.add_task(
        run_document_pipeline_background,
        db=db,
        user=current_user,
        file_path=str(tmp_path),
        job_id=job_id,
    )

    return job_schemas.JobQueuedResponse(job_id=job_id)
