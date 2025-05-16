import logging
from enum import Enum
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from api.crud import invoices as crud_invoices
from api.crud import jobs as crud_jobs
from core.db import models
from core.logic.pipeline import DocumentPipeline
from core.schemas import invoice as invoice_schemas
from core.schemas import job as job_schemas
from core.schemas.classifier import DocumentType
from core.schemas.common import PaginatedResponse
from core.services.factories import EXTRACTOR_REGISTRY, PARSER_REGISTRY
from core.utils.auth import get_current_user, is_admin_or_entity_owner
from core.utils.database import get_db
from core.utils.idsvc import generate_id


class ParserOption(str, Enum):  # noqa: D101
    llamaparse = "llamaparse"
    azure = "azure"


class ModelOption(str, Enum):  # noqa: D101
    openai = "openai"
    azure = "azure"


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=invoice_schemas.InvoiceResponse)
async def create_invoice(
    invoice: invoice_schemas.InvoiceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> invoice_schemas.InvoiceResponse:
    """Create a new invoice in the database."""
    invoice_id = generate_id("I")
    invoice = invoice_schemas.InvoiceCreate(
        id=invoice_id, **invoice.model_dump(exclude={"id"})
    )
    created_invoice = await crud_invoices.create_invoice(db, invoice, current_user)
    return invoice_schemas.InvoiceResponse.model_validate(
        created_invoice, from_attributes=True
    )


@router.get("/")
async def get_all_invoices(  # noqa: PLR0913
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
            description="Free text search in supplier name, address, vat nr \
                or invoice number"
        ),
    ] = None,
) -> PaginatedResponse[invoice_schemas.InvoiceResponse]:
    """Retrieve a list of all users in the database."""
    invoices = await crud_invoices.get_all_invoices(
        db,
        current_user,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=query,
    )

    return PaginatedResponse(
        total_pages=invoices["total_pages"],
        total_items=invoices["total_items"],
        current_page=invoices["current_page"],
        items=[
            invoice_schemas.InvoiceResponse.model_validate(invoice)
            for invoice in invoices["items"]
        ],
    )


@router.get("/stats", response_model=invoice_schemas.InvoiceCounts)
async def get_invoice_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> invoice_schemas.InvoiceCounts:
    """Get total number of invoices and counts per status."""
    counts = await crud_invoices.get_invoice_counts(db, current_user)
    return invoice_schemas.InvoiceCounts(**counts)


@router.get("/{invoice_id}", response_model=invoice_schemas.InvoiceResponse)
async def get_invoice(
    invoice_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> invoice_schemas.InvoiceResponse:
    """Retrieve an invoice's details."""
    invoice = await crud_invoices.get_invoice_by_id(db, invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")

    return invoice_schemas.InvoiceResponse.model_validate(invoice)


@router.put("/{invoice_id}", response_model=invoice_schemas.InvoiceResponse)
async def update_invoice(
    invoice_id: str,
    invoice_update: invoice_schemas.InvoiceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        models.User,
        Depends(
            is_admin_or_entity_owner(
                crud_invoices.get_invoice_by_id,
                entity_name="Invoice",
                entity_id_param="invoice_id",
            )
        ),
    ],
) -> invoice_schemas.InvoiceResponse:
    """Update an existing invoice's details."""
    updated_invoice = await crud_invoices.update_invoice(db, invoice_id, invoice_update)
    return invoice_schemas.InvoiceResponse.model_validate(
        updated_invoice, from_attributes=True
    )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _current_user: Annotated[
        models.User,
        Depends(
            is_admin_or_entity_owner(
                crud_invoices.get_invoice_by_id,
                entity_name="Invoice",
                entity_id_param="invoice_id",
            )
        ),
    ],
) -> None:
    """Delete an existing invoice from the database. This is a hard delete."""
    await crud_invoices.delete_invoice(db, invoice_id)


@router.post("/generate", response_model=invoice_schemas.Invoice)
async def generate(
    file: Annotated[UploadFile, File(...)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
    parser: ParserOption = ParserOption.llamaparse,
    model: ModelOption = ModelOption.openai,
) -> invoice_schemas.Invoice:
    """Receive a document and return structured Invoice data."""
    suffix = Path(file.filename or "").suffix.lower()

    if parser not in PARSER_REGISTRY:
        raise HTTPException(status_code=400, detail=f"Unknown parser: {parser}")
    if (model, "invoice") not in EXTRACTOR_REGISTRY:
        raise HTTPException(
            status_code=400, detail=f"Unknown extractor for invoice with model: {model}"
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

        pipeline = DocumentPipeline[invoice_schemas.Invoice](
            parser=parser_instance,
            extractor=EXTRACTOR_REGISTRY[(model, "invoice")](),
            document_type=DocumentType.INVOICE,
            db=db,
            job_id=job_id,
        )
        result, _doc_type = await pipeline.run()
        return result

    finally:
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except OSError as exc:
            logger.exception("Failed to clean up temporary file: %s", exc)  # noqa: TRY401
