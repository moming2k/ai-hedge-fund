"""add_line_items_table

Revision ID: fc69adc28bff
Revises: b0d465e2eef3
Create Date: 2025-10-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc69adc28bff'
down_revision: Union[str, None] = 'b0d465e2eef3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - create line_items table."""
    op.create_table(
        'line_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ticker', sa.String(length=20), nullable=False),
        sa.Column('report_period', sa.Date(), nullable=False),
        sa.Column('period_type', sa.String(length=20), nullable=False),
        sa.Column('statement_type', sa.String(length=50), nullable=False),
        sa.Column('line_item_name', sa.String(length=200), nullable=False),
        sa.Column('value', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_line_items_id'), 'line_items', ['id'], unique=False)
    op.create_index(op.f('ix_line_items_ticker'), 'line_items', ['ticker'], unique=False)
    op.create_index(op.f('ix_line_items_report_period'), 'line_items', ['report_period'], unique=False)
    op.create_index(op.f('ix_line_items_line_item_name'), 'line_items', ['line_item_name'], unique=False)
    op.create_index('idx_ticker_period_statement', 'line_items', ['ticker', 'report_period', 'statement_type'], unique=False)
    op.create_index('idx_ticker_line_item', 'line_items', ['ticker', 'line_item_name'], unique=False)


def downgrade() -> None:
    """Downgrade schema - drop line_items table."""
    op.drop_index('idx_ticker_line_item', table_name='line_items')
    op.drop_index('idx_ticker_period_statement', table_name='line_items')
    op.drop_index(op.f('ix_line_items_line_item_name'), table_name='line_items')
    op.drop_index(op.f('ix_line_items_report_period'), table_name='line_items')
    op.drop_index(op.f('ix_line_items_ticker'), table_name='line_items')
    op.drop_index(op.f('ix_line_items_id'), table_name='line_items')
    op.drop_table('line_items')
