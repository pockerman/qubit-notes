"""the titles of courses

Revision ID: 0007
Revises: 0006
Create Date: 2026-10-24 15:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "course_titles",
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("course_id", name=op.f("pk_course_titles")),
    )


def downgrade() -> None:
    op.drop_table("course_titles")
