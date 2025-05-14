import logging
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import jobs as crud_jobs
from api.crud import orders as crud_orders
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import job as job_schemas
from core.schemas import order as order_schemas
from core.schemas.common import PaginatedResponse
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.auth import get_current_user, is_admin_or_entity_owner
from core.utils.database import get_db
from core.utils.idsvc import generate_id
from core.utils.process import process_uploaded_order


class ParserOption(str, Enum):  # noqa: D101
    llamaparse = "llamaparse"
    azure = "azure"


class ModelOption(str, Enum):  # noqa: D101
    openai = "openai"
    azure = "azure"


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=order_schemas.OrderResponse)
async def create_order(
    order: order_schemas.OrderCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> order_schemas.OrderResponse:
    """Create a new order in the database."""
    order_id = generate_id("O")
    order = order_schemas.OrderCreate(id=order_id, **order.model_dump(exclude={"id"}))
    created_order = await crud_orders.create_order(db, order, current_user)
    return order_schemas.OrderResponse.model_validate(
        created_order, from_attributes=True
    )


@router.get("/")
async def get_all_orders(  # noqa: PLR0913
    current_user: Annotated[models.User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number (1-based index)")] = 1,
    per_page: Annotated[
        int, Query(ge=1, le=100, description="Number of records per page (max 100)")
    ] = 50,
    sort_by: Annotated[
        str | None, Query(description="Field to sort by (e.g., 'created_at', 'title')")
    ] = None,
    sort_order: Annotated[
        str,
        Query(regex="^(asc|desc)$", description="Sort order ('asc' or 'desc')"),
    ] = "asc",
    query: Annotated[
        str | None,
        Query(
            description="Free text search in customer name, address, or invoice number"
        ),
    ] = None,
) -> PaginatedResponse[order_schemas.OrderResponse]:
    """Retrieve a list of all users in the database."""
    orders = await crud_orders.get_all_orders(
        db,
        current_user,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=query,
    )

    return PaginatedResponse(
        total_pages=orders["total_pages"],
        total_items=orders["total_items"],
        current_page=orders["current_page"],
        items=[
            order_schemas.OrderResponse.model_validate(order)
            for order in orders["items"]
        ],
    )


@router.get("/stats", response_model=order_schemas.OrderCounts)
async def get_order_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> order_schemas.OrderCounts:
    """Get total number of orders and counts per status."""
    counts = await crud_orders.get_order_counts(db, current_user)
    return order_schemas.OrderCounts(**counts)


@router.get("/{order_id}", response_model=order_schemas.OrderResponse)
async def get_order(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> order_schemas.OrderResponse:
    """Retrieve an order's details."""
    order = await crud_orders.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="order not found")

    return order_schemas.OrderResponse.model_validate(order)


@router.put("/{order_id}", response_model=order_schemas.OrderResponse)
async def update_order(
    order_id: str,
    order_update: order_schemas.OrderUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        models.User,
        Depends(
            is_admin_or_entity_owner(
                crud_orders.get_order_by_id,
                entity_name="Order",
                entity_id_param="order_id",
            )
        ),
    ],
) -> order_schemas.OrderResponse:
    """Update an existing order's details."""
    updated_order = await crud_orders.update_order(db, order_id, order_update)
    return order_schemas.OrderResponse.model_validate(
        updated_order, from_attributes=True
    )


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        models.User,
        Depends(
            is_admin_or_entity_owner(
                crud_orders.get_order_by_id,
                entity_name="Order",
                entity_id_param="order_id",
            )
        ),
    ],
) -> None:
    """Delete an existing order from the database. This is a hard delete."""
    await crud_orders.delete_order(db, order_id)


@router.post("/upload", response_model=order_schemas.OrderResponse)
async def upload_order_from_web(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> order_schemas.OrderResponse:
    """Support authenticated frontend users uploading a document."""
    logger.info("🌐 Received upload from %s", current_user.email)
    return await process_uploaded_order(file=file, db=db, user=current_user)


@router.post("/generate", response_model=order_schemas.Order)
async def generate(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    parser: ParserOption = ParserOption.llamaparse,
    model: ModelOption = ModelOption.openai,
) -> order_schemas.Order:
    """Receive a document and return structured Order data."""
    suffix = Path(file.filename or "").suffix.lower()

    if parser not in PARSER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown parser: {parser}")
    if (model, "order") not in EXTRACTOR_REGISTRY:
        raise HTTPException(
            status_code=400, detail=f"Unknown extractor for order with model: {model}"
        )

    tmp_path: Path

    try:
        with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = Path(tmp.name)

        try:
            parser_instance = PARSER_REGISTRY[parser](tmp_path, "en")
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e

        job_id = generate_id("J")

        await crud_jobs.create_job(
            db,
            job_schemas.ProcessingJobCreate(
                id=job_id,
                file_name=tmp_path.name,
                created_by=current_user.id,
            ),
        )

        pipeline = DocumentPipeline[order_schemas.Order](
            parser=parser_instance,
            extractor=EXTRACTOR_REGISTRY[(model, "order")](),
            db=db,
            job_id=job_id,
        )
        return await pipeline.run()

    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError as exc:
            logger.exception("Failed to clean up temporary file: %s", exc)  # noqa: TRY401
