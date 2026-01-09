"""add team_id to users

Revision ID: bf175344ad01
Revises: 8a3b6aa1cd8f
Create Date: 2026-01-08 15:56:31.164577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bf175344ad01'
down_revision: Union[str, Sequence[str], None] = '8a3b6aa1cd8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("team_id", sa.UUID(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("users", "team_id")
