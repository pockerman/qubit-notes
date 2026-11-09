"""the writing assistant's replies

Revision ID: 0019
Revises: 0018
Create Date: 2026-11-10 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0019"
down_revision: str | None = "0018"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "writing_replies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("request", sa.Text(), nullable=False),
        sa.Column("reply", sa.Text(), nullable=False),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("searched", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_writing_replies")),
    )
    op.create_index(op.f("ix_writing_replies_student"), "writing_replies", ["student"])
    op.create_index(op.f("ix_writing_replies_course_id"), "writing_replies", ["course_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_writing_replies_course_id"), table_name="writing_replies")
    op.drop_index(op.f("ix_writing_replies_student"), table_name="writing_replies")
    op.drop_table("writing_replies")
