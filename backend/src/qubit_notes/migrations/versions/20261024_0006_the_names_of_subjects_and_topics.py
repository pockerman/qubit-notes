"""the names of subjects and topics

Revision ID: 0006
Revises: 0005
Create Date: 2026-10-24 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0006"
down_revision: str | None = "0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("topics") as batch:
        batch.add_column(sa.Column("name", sa.String(), nullable=True))
    op.create_table(
        "subject_names",
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("course_id", "subject", name=op.f("pk_subject_names")),
    )


def downgrade() -> None:
    op.drop_table("subject_names")
    with op.batch_alter_table("topics") as batch:
        batch.drop_column("name")
