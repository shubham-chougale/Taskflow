"""refactor task ownership and assignee

Revision ID: 56c03196e6d3
Revises: 46f712ed5b51
Create Date: 2026-01-09 11:15:18.893230

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '56c03196e6d3'
down_revision: Union[str, Sequence[str], None] = '46f712ed5b51'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Rename user_id → created_by_id
    op.alter_column(
        "tasks",
        "user_id",
        new_column_name="created_by_id"
    )

    # 2. Add assigned_to_id
    op.add_column(
        "tasks",
        sa.Column(
            "assigned_to_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id"),
            nullable=True,
        )
    )


def downgrade():
    op.drop_column("tasks", "assigned_to_id")

    op.alter_column(
        "tasks",
        "created_by_id",
        new_column_name="user_id"
    )
