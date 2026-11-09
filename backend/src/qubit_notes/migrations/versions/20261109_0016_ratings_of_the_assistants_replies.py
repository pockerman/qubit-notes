"""ratings of the assistant's replies

Revision ID: 0016
Revises: 0015
Create Date: 2026-11-09 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "answer_ratings",
        sa.Column("turn_id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("rating", sa.String(), nullable=False),
        sa.Column("rated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("turn_id", name=op.f("pk_answer_ratings")),
    )
    op.create_index(op.f("ix_answer_ratings_student"), "answer_ratings", ["student"])
    op.create_index(op.f("ix_answer_ratings_course_id"), "answer_ratings", ["course_id"])
    op.create_index(op.f("ix_answer_ratings_document_id"), "answer_ratings", ["document_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_answer_ratings_document_id"), table_name="answer_ratings")
    op.drop_index(op.f("ix_answer_ratings_course_id"), table_name="answer_ratings")
    op.drop_index(op.f("ix_answer_ratings_student"), table_name="answer_ratings")
    op.drop_table("answer_ratings")
