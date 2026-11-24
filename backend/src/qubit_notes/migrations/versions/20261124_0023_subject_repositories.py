"""the repository a student pushes a subject to

Revision ID: 0023
Revises: 0022
Create Date: 2026-11-24 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0023"
down_revision: str | None = "0022"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subject_repositories",
        sa.Column("student", sa.String(), nullable=False),
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("repository", sa.String(), nullable=False),
        sa.Column("token", sa.Text(), nullable=False),
        sa.Column("connected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("pushed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("commit_sha", sa.String(), nullable=True),
        sa.Column("commit_url", sa.String(), nullable=True),
        sa.Column("files", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("student", "course_id", "subject", name=op.f("pk_subject_repositories")),
    )
    op.create_index(op.f("ix_subject_repositories_course_id"), "subject_repositories", ["course_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_subject_repositories_course_id"), table_name="subject_repositories")
    op.drop_table("subject_repositories")
