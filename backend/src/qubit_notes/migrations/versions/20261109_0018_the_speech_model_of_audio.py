"""the speech model of audio

Revision ID: 0018
Revises: 0017
Create Date: 2026-11-09 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0018"
down_revision: str | None = "0017"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # the audio made before the student chose the speech model was read by the app's own, gpt-4o-mini-tts by default
    with op.batch_alter_table("material_audio", schema=None) as batch_op:
        batch_op.add_column(sa.Column("model", sa.String(), nullable=False, server_default="gpt-4o-mini-tts"))


def downgrade() -> None:
    with op.batch_alter_table("material_audio", schema=None) as batch_op:
        batch_op.drop_column("model")
