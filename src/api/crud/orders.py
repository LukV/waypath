from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.db import models
from core.schemas import order as order_schemas
from core.utils.idsvc import generate_id


async def create_order(
    db: AsyncSession, order: order_schemas.OrderCreate, current_user: models.User
) -> models.Order:
    """Create a new order in the database."""
    db_order = models.Order(
        id=generate_id("O"),
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

    # Now load lines explicitly
    stmt = (
        select(models.Order)
        .options(selectinload(models.Order.lines))
        .where(models.Order.id == db_order.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()
