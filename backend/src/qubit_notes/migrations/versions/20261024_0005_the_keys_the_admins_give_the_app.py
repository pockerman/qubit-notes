"""the keys the admins give the app

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-24 09:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "app_keys",
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("encrypted", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("provider", name=op.f("pk_app_keys")),
    )


def downgrade() -> None:
    op.drop_table("app_keys")
