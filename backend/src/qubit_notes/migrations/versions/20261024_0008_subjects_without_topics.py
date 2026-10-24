"""subjects without topics

Revision ID: 0008
Revises: 0007
Create Date: 2026-10-24 18:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "subjects",
        sa.Column("course_id", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("course_id", "subject", name=op.f("pk_subjects")),
    )
    # the subjects the courses have: those of their topics, and those given names
    op.execute(
        "INSERT INTO subjects (course_id, subject, created_at) "
        "SELECT course_id, subject, MIN(created_at) FROM topics GROUP BY course_id, subject"
    )
    op.execute(
        "INSERT INTO subjects (course_id, subject, created_at) "
        "SELECT course_id, subject, CURRENT_TIMESTAMP FROM subject_names n WHERE NOT EXISTS "
        "(SELECT 1 FROM subjects s WHERE s.course_id = n.course_id AND s.subject = n.subject)"
    )


def downgrade() -> None:
    op.drop_table("subjects")
