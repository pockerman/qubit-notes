"""collections of papers

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-29 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "paper_collections",
        sa.Column("course_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("course_id", name=op.f("pk_paper_collections")),
    )
    op.create_table(
        "paper_details",
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("authors", sa.JSON(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("venue", sa.String(), nullable=False),
        sa.Column("doi", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("document_id", name=op.f("pk_paper_details")),
    )
    with op.batch_alter_table("paper_details", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_paper_details_course_id"), ["course_id"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("paper_details", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_paper_details_course_id"))
    op.drop_table("paper_details")
    op.drop_table("paper_collections")
