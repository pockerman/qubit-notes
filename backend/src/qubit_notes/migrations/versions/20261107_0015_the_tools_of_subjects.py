"""the tools of subjects

Revision ID: 0015
Revises: 0014
Create Date: 2026-11-07 20:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subject_tools",
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("tool", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("course_id", "subject", "tool", name=op.f("pk_subject_tools")),
    )


def downgrade() -> None:
    op.drop_table("subject_tools")
