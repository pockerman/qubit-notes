"""the prompt, and its version, that what the AI writes was written with

Revision ID: 0022
Revises: 0021
Create Date: 2026-11-23 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0022"
down_revision: str | None = "0021"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

TABLES = (
    "summaries",
    "quizzes",
    "flashcard_decks",
    "conversation_turns",
    "writing_replies",
    "comprehension_checks",
    "material_audio",
)


def upgrade() -> None:
    for table in TABLES:
        with op.batch_alter_table(table) as batch:
            batch.add_column(sa.Column("prompt", sa.String(), nullable=True))


def downgrade() -> None:
    for table in TABLES:
        with op.batch_alter_table(table) as batch:
            batch.drop_column("prompt")
