"""create tasks table

Revision ID: 6d53fa3517de
Revises: 881133f07c27
Create Date: 2026-01-08 17:32:05.115857

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '6d53fa3517de'
down_revision: Union[str, Sequence[str], None] = '881133f07c27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_status_enum = postgresql.ENUM(
    "OPEN",
    "IN_PROGRESS",
    "DONE",
    name="taskstatus",
    create_type=False,
)

# def upgrade():
#     bind = op.get_bind()

#     task_status_enum.create(bind, checkfirst=True)

#     op.create_table(
#         "tasks",
#         sa.Column("id", sa.UUID(), primary_key=True),
#         sa.Column("title", sa.String(length=255), nullable=False),
#         sa.Column("description", sa.Text(), nullable=True),
#         sa.Column(
#             "status",
#             task_status_enum,
#             nullable=False,
#             server_default="OPEN",
#         ),
#         sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
#         sa.Column("team_id", sa.UUID(), sa.ForeignKey("teams.id"), nullable=False),
#         sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
#         sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
#     )

def upgrade():
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'taskstatus') THEN
                CREATE TYPE taskstatus AS ENUM ('OPEN', 'IN_PROGRESS', 'DONE');
            END IF;
        END$$;
    """)

    op.create_table(
        "tasks",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column(
            "status",
            task_status_enum,   # safe now
            nullable=False,
            server_default="OPEN",
        ),
        sa.Column("user_id", sa.UUID(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("team_id", sa.UUID(), sa.ForeignKey("teams.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("tasks")
    op.execute("DROP TYPE IF EXISTS taskstatus")

