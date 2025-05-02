from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import orders as crud_orders
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import order as order_schemas
from core.services.document_parser import DocumentParser
from core.services.structuring import OrderExtractor
from core.utils.auth import get_current_user
from core.utils.database import get_db

router = APIRouter()

SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx", ".md", ".txt", ".html"}


@router.post("/", response_model=order_schemas.OrderResponse)
async def create_order(
    order: order_schemas.OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> order_schemas.OrderResponse:
    """Create a new order in the database."""
    created_order = await crud_orders.create_order(db, order, current_user)
    return order_schemas.OrderResponse.model_validate(
        created_order, from_attributes=True
    )


@router.post("/generate", response_model=order_schemas.Order)
async def generate(file: Annotated[UploadFile, File(...)]) -> order_schemas.Order:
    """Receive a document and return structured Order data."""
    suffix = Path(file.filename or "").suffix.lower()

    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {suffix}. \
                Must be one of {', '.join(SUPPORTED_EXTENSIONS)}",
        )

    try:
        # Save to temporary file
        with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = Path(tmp.name)

        # Run pipeline
        pipeline = DocumentPipeline(
            parser=DocumentParser(path=tmp_path),
            extractor=OrderExtractor(),
        )
        return await pipeline.run()

    finally:
        # Optional: clean up temp file if you want
        if tmp_path.exists():
            tmp_path.unlink()
