from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import orders as crud_orders
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import order as order_schemas
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.auth import get_current_user
from core.utils.database import get_db


class ParserOption(str, Enum):  # noqa: D101
    llamaparse = "llamaparse"
    azure = "azure"


class ModelOption(str, Enum):  # noqa: D101
    openai = "openai"
    azure = "azure"


router = APIRouter()


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
async def generate(
    file: Annotated[UploadFile, File(...)],
    parser: ParserOption = ParserOption.llamaparse,
    model: ModelOption = ModelOption.openai,
) -> order_schemas.Order:
    """Receive a document and return structured Order data."""
    suffix = Path(file.filename or "").suffix.lower()

    if parser not in PARSER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown parser: {parser}")
    if model not in EXTRACTOR_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown model: {model}")

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = Path(tmp.name)

        try:
            parser_instance = PARSER_REGISTRY[parser](tmp_path, "en")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        pipeline = DocumentPipeline(
            parser=parser_instance,
            extractor=EXTRACTOR_REGISTRY[model](),
        )
        return await pipeline.run()

    finally:
        if tmp_path.exists():
            tmp_path.unlink()
