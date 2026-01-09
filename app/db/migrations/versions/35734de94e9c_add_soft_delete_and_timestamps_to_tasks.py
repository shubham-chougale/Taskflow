"""add soft delete and timestamps to tasks

Revision ID: 35734de94e9c
Revises: 56c03196e6d3
Create Date: 2026-01-09 11:21:28.622598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '35734de94e9c'
down_revision: Union[str, Sequence[str], None] = '56c03196e6d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    conn = op.get_bind()

    # is_deleted (does NOT exist yet)
    conn.execute(text("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN NOT NULL DEFAULT false
    """))

    # created_at (already exists → skip safely)
    conn.execute(text("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT now()
    """))

    # updated_at (add if missing)
    conn.execute(text("""
        ALTER TABLE tasks
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE
        NOT NULL DEFAULT now()
    """))

def downgrade():
    op.drop_column("tasks", "updated_at")
    op.drop_column("tasks", "created_at")
    op.drop_column("tasks", "is_deleted")

