"""checks of a student's understanding

Revision ID: 0020
Revises: 0019
Create Date: 2026-11-11 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0020"
down_revision: str | None = "0019"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comprehension_checks",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=True),
        sa.Column("section", sa.Integer(), nullable=True),
        sa.Column("subject", sa.String(), nullable=True),
        sa.Column("topic", sa.String(), nullable=True),
        sa.Column("sources", sa.JSON(), nullable=False),
        sa.Column("documents", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("exchanges", sa.JSON(), nullable=False),
        sa.Column("verdict", sa.JSON(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_comprehension_checks")),
    )
    op.create_index(op.f("ix_comprehension_checks_student"), "comprehension_checks", ["student"])
    op.create_index(op.f("ix_comprehension_checks_document_id"), "comprehension_checks", ["document_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_comprehension_checks_document_id"), table_name="comprehension_checks")
    op.drop_index(op.f("ix_comprehension_checks_student"), table_name="comprehension_checks")
    op.drop_table("comprehension_checks")
