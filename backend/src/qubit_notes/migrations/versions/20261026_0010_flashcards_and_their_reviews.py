"""flashcards and their reviews

Revision ID: 0010
Revises: 0009
Create Date: 2026-10-26 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "flashcard_decks",
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
        sa.Column("count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_flashcard_decks")),
    )
    with op.batch_alter_table("flashcard_decks", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_flashcard_decks_document_id"), ["document_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_flashcard_decks_student"), ["student"], unique=False)

    op.create_table(
        "flashcards",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("deck_id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("front", sa.Text(), nullable=False),
        sa.Column("back", sa.Text(), nullable=False),
        sa.Column("source", sa.JSON(), nullable=False),
        sa.Column("ease", sa.Float(), nullable=False),
        sa.Column("interval_days", sa.Integer(), nullable=False),
        sa.Column("repetitions", sa.Integer(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_flashcards")),
    )
    with op.batch_alter_table("flashcards", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_flashcards_deck_id"), ["deck_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_flashcards_due_at"), ["due_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_flashcards_student"), ["student"], unique=False)

    with op.batch_alter_table("conversation_turns", schema=None) as batch_op:
        batch_op.add_column(sa.Column("deck_id", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("conversation_turns", schema=None) as batch_op:
        batch_op.drop_column("deck_id")

    with op.batch_alter_table("flashcards", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_flashcards_student"))
        batch_op.drop_index(batch_op.f("ix_flashcards_due_at"))
        batch_op.drop_index(batch_op.f("ix_flashcards_deck_id"))
    op.drop_table("flashcards")

    with op.batch_alter_table("flashcard_decks", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_flashcard_decks_student"))
        batch_op.drop_index(batch_op.f("ix_flashcard_decks_document_id"))
    op.drop_table("flashcard_decks")
