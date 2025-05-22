from typing import Any

from fastapi import HTTPException
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db import models
from core.schemas import order as order_schemas
from core.utils.idsvc import generate_id
from core.validators.total_amount import validate


async def create_order(
    db: AsyncSession, order: order_schemas.OrderCreate, current_user: models.User
) -> models.Order:
    """Create a new order in the database."""
    validated_status = validate(order)

    db_order = models.Order(
        id=order.id or generate_id("O"),
        file_name=order.file_name,
        status=validated_status,
        customer_name=order.customer_name,
        customer_address=order.customer_address,
        invoice_number=order.invoice_number,
        order_date=order.order_date,
        due_date=order.due_date,
        total_excl_vat=order.total_excl_vat,
        vat=order.vat,
        total_incl_vat=order.total_incl_vat,
        created_by=current_user.id,
    )

    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)

    # Add order lines
    for line in order.lines:
        db_line = models.OrderLine(
            order_id=db_order.id,
            product_code=line.product_code,
            description=line.description,
            quantity=line.quantity,
            unit_price=line.unit_price,
            subtotal=line.subtotal,
        )
        db.add(db_line)

    await db.commit()
    await db.refresh(db_order)

    stmt = (
        select(models.Order)
        .options(selectinload(models.Order.lines))
        .where(models.Order.id == db_order.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def update_order(
    db: AsyncSession,
    order_id: str,
    order_update: order_schemas.OrderUpdate,
) -> models.Order:
    """Update an existing order's details in the database."""
    # Fetch the order to update
    result = await db.execute(select(models.Order).where(models.Order.id == order_id))
    db_order = result.scalar_one_or_none()
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Update scalar fields
    update_data = order_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        if key == "lines":
            # Remove all existing lines
            db_order.lines.clear()
            # Add new OrderLine instances
            db_order.lines.extend(models.OrderLine(**line) for line in value)
        else:
            setattr(db_order, key, value)

    # Commit and return
    await db.commit()

    # Refetch with eager loading
    result = await db.execute(
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(selectinload(models.Order.lines))
    )
    return result.scalar_one()


async def delete_order(db: AsyncSession, order_id: str) -> models.Order | None:
    """Delete an order from the database."""
    stmt = select(models.Order).where(models.Order.id == order_id)
    result = await db.execute(stmt)
    db_order = result.scalar_one_or_none()
    if db_order:
        await db.delete(db_order)
        await db.commit()
    return db_order


async def get_all_orders(  # noqa: PLR0913
    db: AsyncSession,
    current_user: models.User,
    page: int,
    per_page: int,
    sort_by: str | None = None,
    sort_order: str = "asc",
    search_query: str | None = None,
) -> dict[str, Any]:
    """Retrieve paginated orders with eager-loaded lines, optional text search."""
    base_query = select(models.Order).options(selectinload(models.Order.lines))
    count_query = select(func.count())

    if current_user.role != "admin":
        base_query = base_query.where(models.Order.created_by == current_user.id)
        count_query = count_query.select_from(models.Order).where(
            models.Order.created_by == current_user.id
        )
    else:
        count_query = count_query.select_from(models.Order)

    # Search logic
    if search_query:
        tokens = search_query.strip().split()
        for token in tokens:
            ilike_token = f"%{token}%"
            base_query = base_query.where(
                or_(
                    models.Order.customer_name.ilike(ilike_token),
                    models.Order.customer_address.ilike(ilike_token),
                    models.Order.invoice_number.ilike(ilike_token),
                )
            )
            count_query = count_query.where(
                or_(
                    models.Order.customer_name.ilike(ilike_token),
                    models.Order.customer_address.ilike(ilike_token),
                    models.Order.invoice_number.ilike(ilike_token),
                )
            )

    # Sorting
    if sort_by:
        sort_column = getattr(models.Order, sort_by, None)
        if sort_column:
            base_query = base_query.order_by(
                desc(sort_column) if sort_order == "desc" else asc(sort_column)
            )

    offset = (page - 1) * per_page
    paginated_query = base_query.offset(offset).limit(per_page)

    total_items = (await db.execute(count_query)).scalar_one()
    result = await db.execute(paginated_query)
    orders = result.scalars().all()

    return {
        "total_pages": (total_items + per_page - 1) // per_page,
        "total_items": total_items,
        "current_page": page,
        "items": orders,
    }


async def get_order_by_id(db: AsyncSession, order_id: str) -> models.Order | None:
    """Fetch an order by its ID with lines eagerly loaded."""
    stmt = (
        select(models.Order)
        .where(models.Order.id == order_id)
        .options(selectinload(models.Order.lines))
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_order_counts(
    db: AsyncSession, current_user: models.User
) -> dict[str, int]:
    """Return total order count and count per status."""
    stmt = select(models.Order.status, func.count().label("count")).group_by(
        models.Order.status
    )

    if current_user.role != "admin":
        stmt = stmt.where(models.Order.created_by == current_user.id)

    result = await db.execute(stmt)
    counts = {row._mapping["status"]: row._mapping["count"] for row in result.all()}  # noqa: SLF001

    total = sum(counts.values())
    return {"total": total, **counts}
