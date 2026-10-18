"""What summaries and quizzes share: they are written by the AI about a scope, saved per student, and the newest
one is shown until the student asks for a new one."""

from datetime import UTC, datetime

from sqlalchemy import Table, delete, select

from study_assistant.domain.sources import Scope


def now() -> datetime:
    return datetime.now(UTC)


def scope_values(student: str, scope: Scope) -> dict:
    return {
        "student": student,
        "course_id": scope.course_id,
        "document_id": scope.document_id,
        "section": scope.section,
        "subject": scope.subject,
        "topic": scope.topic,
    }


def of_scope(table: Table, student: str, scope: Scope):
    """a query of the student's rows about exactly the scope, newest first"""
    conditions = [table.c.student == student, table.c.course_id == scope.course_id]
    for column in ("document_id", "section", "subject", "topic"):
        value = getattr(scope, column)
        conditions.append(table.c[column].is_(None) if value is None else table.c[column] == value)
    return select(table).where(*conditions).order_by(table.c.created_at.desc())


def scope_of(row) -> Scope:
    return Scope(
        course_id=row.course_id,
        document_id=row.document_id,
        section=row.section,
        subject=row.subject,
        topic=row.topic,
    )


def forget_course_rows(connection, table: Table, course_id: str) -> list[str]:
    """deletes the rows about anything in the deleted course; returns their ids"""
    ids = [row.id for row in connection.execute(select(table.c.id).where(table.c.course_id == course_id))]
    connection.execute(delete(table).where(table.c.course_id == course_id))
    return ids


def forget_document(connection, table: Table, document_id: str) -> list[str]:
    """deletes the rows about the deleted document (its sections and itself, not its topic); returns their ids"""
    ids = [row.id for row in connection.execute(select(table.c.id).where(table.c.document_id == document_id))]
    connection.execute(delete(table).where(table.c.document_id == document_id))
    return ids
