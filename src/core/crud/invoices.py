from typing import Any

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db import models
from core.schemas import invoice as invoice_schemas
from core.utils.config import ObjectStatus
from core.utils.idsvc import generate_id


async def create_invoice(
    db: AsyncSession, invoice: invoice_schemas.InvoiceCreate, current_user: models.User
) -> models.Invoice:
    """Create a new invoice in the database."""
    db_invoice = models.Invoice(
        id=invoice.id or generate_id("I"),
        file_name=invoice.file_name,
        status=invoice.status or ObjectStatus.TO_ACCEPT,
        supplier_name=invoice.supplier_name,
        supplier_address=invoice.supplier_address,
        supplier_vat_number=invoice.supplier_vat_number,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        total_excl_vat=invoice.total_excl_vat,
        vat=invoice.vat,
        total_incl_vat=invoice.total_incl_vat,
        created_by=current_user.id,
    )

    db.add(db_invoice)
    await db.commit()
    await db.refresh(db_invoice)

    # Add invoice lines
    for line in invoice.lines:
        db_line = models.InvoiceLine(
            invoice_id=db_invoice.id,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price,
            subtotal=line.subtotal,
        )
        db.add(db_line)

    await db.commit()
    await db.refresh(db_invoice)

    stmt = (
        select(models.Invoice)
        .options(selectinload(models.Invoice.lines))
        .where(models.Invoice.id == db_invoice.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def update_invoice(
    db: AsyncSession,
    invoice_id: str,
    invoice_update: invoice_schemas.InvoiceUpdate,
) -> models.Invoice:
    """Update an existing invoice's details in the database."""
    # Fetch the invoice to update
    result = await db.execute(
        select(models.Invoice).where(models.Invoice.id == invoice_id)
    )
    db_invoice = result.scalar_one_or_none()
    if not db_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    # Update scalar fields
    update_data = invoice_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "lines":
            # Remove all existing lines
            db_invoice.lines.clear()
            # Add new InvoiceLine instances
            db_invoice.lines.extend(models.InvoiceLine(**line) for line in value)
        else:
            setattr(db_invoice, key, value)

    # Commit and return
    await db.commit()

    # Refetch with eager loading
    result = await db.execute(
        select(models.Invoice)
        .where(models.Invoice.id == invoice_id)
        .options(selectinload(models.Invoice.lines))
    )
    return result.scalar_one()


async def delete_invoice(db: AsyncSession, invoice_id: str) -> models.Invoice | None:
    """Delete an invoice from the database."""
    stmt = select(models.Invoice).where(models.Invoice.id == invoice_id)
    result = await db.execute(stmt)
    db_invoice = result.scalar_one_or_none()
    if db_invoice:
        await db.delete(db_invoice)
        await db.commit()
    return db_invoice


async def get_all_invoices(  # noqa: PLR0913
    db: AsyncSession,
    current_user: models.User,
    page: int,
    per_page: int,
    sort_by: str | None = None,
    sort_order: str = "asc",
    search_query: str | None = None,
) -> dict[str, Any]:
    """Retrieve paginated invoices with eager-loaded lines, optional text search."""
    base_query = select(models.Invoice).options(selectinload(models.Invoice.lines))
    count_query = select(func.count())

    if current_user.role != "admin":
        base_query = base_query.where(models.Invoice.created_by == current_user.id)
        count_query = count_query.select_from(models.Invoice).where(
            models.Invoice.created_by == current_user.id
        )
    else:
        count_query = count_query.select_from(models.Invoice)

    # Search logic
    if search_query:
        tokens = search_query.strip().split()
        for token in tokens:
            ilike_token = f"%{token}%"
            base_query = base_query.where(
                or_(
                    models.Invoice.supplier_name.ilike(ilike_token),
                    models.Invoice.supplier_address.ilike(ilike_token),
                    models.Invoice.supplier_vat_number.ilike(ilike_token),
                    models.Invoice.invoice_number.ilike(ilike_token),
                )
            )
            count_query = count_query.where(
                or_(
                    models.Invoice.supplier_name.ilike(ilike_token),
                    models.Invoice.supplier_address.ilike(ilike_token),
                    models.Invoice.supplier_vat_number.ilike(ilike_token),
                    models.Invoice.invoice_number.ilike(ilike_token),
                )
            )

    # Sorting
    if sort_by:
        sort_column = getattr(models.Invoice, sort_by, None)
        if sort_column:
            base_query = base_query.order_by(
                desc(sort_column) if sort_order == "desc" else asc(sort_column)
            )

    offset = (page - 1) * per_page
    paginated_query = base_query.offset(offset).limit(per_page)

    total_items = (await db.execute(count_query)).scalar_one()
    result = await db.execute(paginated_query)
    invoices = result.scalars().all()

    return {
        "total_pages": (total_items + per_page - 1) // per_page,
        "total_items": total_items,
        "current_page": page,
        "items": invoices,
    }


async def get_invoice_by_id(db: AsyncSession, invoice_id: str) -> models.Invoice | None:
    """Fetch an invoice by its ID with lines eagerly loaded."""
    stmt = (
        select(models.Invoice)
        .where(models.Invoice.id == invoice_id)
        .options(selectinload(models.Invoice.lines))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_invoice_counts(
    db: AsyncSession, current_user: models.User
) -> dict[str, int]:
    """Return total invoice count and count per status."""
    stmt = select(models.Invoice.status, func.count().label("count")).group_by(
        models.Invoice.status
    )

    if current_user.role != "admin":
        stmt = stmt.where(models.Invoice.created_by == current_user.id)

    result = await db.execute(stmt)
    counts = {row._mapping["status"]: row._mapping["count"] for row in result.all()}  # noqa: SLF001

    total = sum(counts.values())
    return {"total": total, **counts}
