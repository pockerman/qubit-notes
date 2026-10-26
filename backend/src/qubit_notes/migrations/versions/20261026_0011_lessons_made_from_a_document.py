"""lessons made from a document

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-26 16:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "lesson_imports",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("topics", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_lesson_imports")),
    )
    with op.batch_alter_table("lesson_imports", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_lesson_imports_course_id"), ["course_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("lesson_imports", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_lesson_imports_course_id"))
    op.drop_table("lesson_imports")
