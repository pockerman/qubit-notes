"""the AI model the admins choose

Revision ID: 0009
Revises: 0008
Create Date: 2026-10-24 21:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_settings",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("value", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("name", name=op.f("pk_app_settings")),
    )


def downgrade() -> None:
    op.drop_table("app_settings")
