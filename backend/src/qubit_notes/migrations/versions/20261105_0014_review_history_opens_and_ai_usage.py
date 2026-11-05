"""the history of reviews, the sections opened, and the AI's usage

Revision ID: 0014
Revises: 0013
Create Date: 2026-11-05 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_usage",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("purpose", sa.String(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False),
        sa.Column("output_tokens", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("ai_usage", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_ai_usage_created_at"), ["created_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_ai_usage_student"), ["student"], unique=False)

    op.create_table(
        "card_reviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("card_id", sa.String(), nullable=False),
        sa.Column("deck_id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("answer", sa.String(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ease_before", sa.Float(), nullable=False),
        sa.Column("ease_after", sa.Float(), nullable=False),
        sa.Column("interval_before", sa.Integer(), nullable=False),
        sa.Column("interval_after", sa.Integer(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("card_reviews", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_card_reviews_card_id"), ["card_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_card_reviews_deck_id"), ["deck_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_card_reviews_reviewed_at"), ["reviewed_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_card_reviews_student"), ["student"], unique=False)

    op.create_table(
        "section_opens",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("section", sa.Integer(), nullable=False),
        sa.Column("opened_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("section_opens", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_section_opens_course_id"), ["course_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_section_opens_document_id"), ["document_id"], unique=False)
        batch_op.create_index(batch_op.f("ix_section_opens_opened_at"), ["opened_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_section_opens_student"), ["student"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("section_opens", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_section_opens_student"))
        batch_op.drop_index(batch_op.f("ix_section_opens_opened_at"))
        batch_op.drop_index(batch_op.f("ix_section_opens_document_id"))
        batch_op.drop_index(batch_op.f("ix_section_opens_course_id"))
    op.drop_table("section_opens")

    with op.batch_alter_table("card_reviews", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_card_reviews_student"))
        batch_op.drop_index(batch_op.f("ix_card_reviews_reviewed_at"))
        batch_op.drop_index(batch_op.f("ix_card_reviews_deck_id"))
        batch_op.drop_index(batch_op.f("ix_card_reviews_card_id"))
    op.drop_table("card_reviews")

    with op.batch_alter_table("ai_usage", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_ai_usage_student"))
        batch_op.drop_index(batch_op.f("ix_ai_usage_created_at"))
    op.drop_table("ai_usage")
