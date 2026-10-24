"""The order a topic's material is meant to be read in (features/reading_order.feature). A material is added after
the topic's others when it's uploaded; its owners can set another order. Material uploaded before the order was kept
has no place in it, and goes after the material that has."""

from sqlalchemy import delete, func, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage

table = storage.material_order


class MaterialOrder:
    def __init__(self, engine: Engine):
        self._engine = engine

    def append(self, course_id: str, subject: str, topic: str, document_id: str) -> None:
        """puts the material after the topic's others"""
        with self._engine.begin() as connection:
            last = connection.execute(
                select(func.max(table.c.position)).where(
                    table.c.course_id == course_id, table.c.subject == subject, table.c.topic == topic
                )
            ).scalar()
            connection.execute(delete(table).where(table.c.course_id == course_id, table.c.document_id == document_id))
            connection.execute(
                insert(table).values(
                    course_id=course_id,
                    document_id=document_id,
                    subject=subject,
                    topic=topic,
                    position=(last if last is not None else -1) + 1,
                )
            )

    def set(self, course_id: str, subject: str, topic: str, document_ids: list[str]) -> None:
        """puts the topic's material in the order given"""
        with self._engine.begin() as connection:
            connection.execute(
                delete(table).where(table.c.course_id == course_id, table.c.subject == subject, table.c.topic == topic)
            )
            connection.execute(
                insert(table),
                [
                    {
                        "course_id": course_id,
                        "document_id": document_id,
                        "subject": subject,
                        "topic": topic,
                        "position": position,
                    }
                    for position, document_id in enumerate(document_ids)
                ],
            )

    def positions(self, course_id: str) -> dict[str, int]:
        """the place of each material of the course that has one, by its document id"""
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(table.c.document_id, table.c.position).where(table.c.course_id == course_id)
            )
            return {row.document_id: row.position for row in rows}

    def forget(self, course_id: str, document_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course_id, table.c.document_id == document_id))

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course_id))
