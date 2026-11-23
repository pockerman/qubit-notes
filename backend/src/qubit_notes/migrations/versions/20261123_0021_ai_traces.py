"""traces of the AI, and the trace of each reply

Revision ID: 0021
Revises: 0020
Create Date: 2026-11-23 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0021"
down_revision: str | None = "0020"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_traces",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_ai_traces")),
    )
    op.create_index(op.f("ix_ai_traces_student"), "ai_traces", ["student"])
    op.create_index(op.f("ix_ai_traces_course_id"), "ai_traces", ["course_id"])
    op.create_table(
        "ai_trace_documents",
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("trace_id", "document_id", name=op.f("pk_ai_trace_documents")),
    )
    op.create_index(op.f("ix_ai_trace_documents_document_id"), "ai_trace_documents", ["document_id"])
    op.create_table(
        "ai_trace_deletions",
        sa.Column("trace_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("trace_id", name=op.f("pk_ai_trace_deletions")),
    )
    for table in ("conversation_turns", "writing_replies", "answer_ratings"):
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("trace_id", sa.String(), nullable=True))


def downgrade() -> None:
    for table in ("answer_ratings", "writing_replies", "conversation_turns"):
        with op.batch_alter_table(table) as batch:
            batch.drop_column("trace_id")
    op.drop_table("ai_trace_deletions")
    op.drop_index(op.f("ix_ai_trace_documents_document_id"), table_name="ai_trace_documents")
    op.drop_table("ai_trace_documents")
    op.drop_index(op.f("ix_ai_traces_course_id"), table_name="ai_traces")
    op.drop_index(op.f("ix_ai_traces_student"), table_name="ai_traces")
    op.drop_table("ai_traces")
