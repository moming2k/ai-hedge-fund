"""change_volume_to_bigint

Revision ID: b0d465e2eef3
Revises: 4a7b8c9d0e3f
Create Date: 2025-10-25 22:53:45.369126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0d465e2eef3'
down_revision: Union[str, None] = '4a7b8c9d0e3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - change volume column to BIGINT."""
    # Change volume column in historical_prices table from INTEGER to BIGINT
    op.alter_column('historical_prices', 'volume',
                    type_=sa.BigInteger(),
                    existing_type=sa.Integer(),
                    nullable=False)


def downgrade() -> None:
    """Downgrade schema - revert volume column to INTEGER."""
    # Revert volume column in historical_prices table from BIGINT to INTEGER
    op.alter_column('historical_prices', 'volume',
                    type_=sa.Integer(),
                    existing_type=sa.BigInteger(),
                    nullable=False)
