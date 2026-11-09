"""audio of materials

Revision ID: 0017
Revises: 0016
Create Date: 2026-11-09 14:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0017"
down_revision: str | None = "0016"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "material_audio",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("document_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("instructions", sa.Text(), nullable=False),
        sa.Column("suggestions", sa.Text(), nullable=False),
        sa.Column("narration", sa.Text(), nullable=False),
        sa.Column("voice", sa.Text(), nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("size", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_material_audio")),
        sa.UniqueConstraint("student", "document_id", name=op.f("uq_material_audio_student")),
    )
    op.create_index(op.f("ix_material_audio_course_id"), "material_audio", ["course_id"])
    op.create_index(op.f("ix_material_audio_document_id"), "material_audio", ["document_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_material_audio_document_id"), table_name="material_audio")
    op.drop_index(op.f("ix_material_audio_course_id"), table_name="material_audio")
    op.drop_table("material_audio")
