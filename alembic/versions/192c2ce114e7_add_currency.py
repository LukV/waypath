"""add currency

Revision ID: 192c2ce114e7
Revises: c89f32aa181f
Create Date: 2025-05-19 19:23:34.263317

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '192c2ce114e7'
down_revision: Union[str, None] = 'c89f32aa181f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('invoices', sa.Column('currency', sa.Enum('EUR', 'USD', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'INR', name='currency'), nullable=False))
    op.add_column('orders', sa.Column('currency', sa.Enum('EUR', 'USD', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'INR', name='currency'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('orders', 'currency')
    op.drop_column('invoices', 'currency')
    # ### end Alembic commands ###
