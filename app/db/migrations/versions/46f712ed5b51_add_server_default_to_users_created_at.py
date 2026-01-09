"""add server default to users.created_at

Revision ID: 46f712ed5b51
Revises: 6d53fa3517de
Create Date: 2026-01-09 10:25:50.963408

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46f712ed5b51'
down_revision: Union[str, Sequence[str], None] = '6d53fa3517de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        server_default=sa.text("NOW()"),
        nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "created_at",
        server_default=None,
        nullable=False,
    )
