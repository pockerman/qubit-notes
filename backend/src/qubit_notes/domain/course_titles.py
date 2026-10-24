"""What courses are called (features/course_names.feature). A course is known by its name, in its links, and shown by
its title, as its creator typed it; a course without one is titled after its name. Only its creator changes it."""

from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotAllowed
from qubit_notes.domain.topics import named

table = storage.course_titles


class CourseTitles:
    def __init__(self, engine: Engine, courses: Courses):
        self._engine = engine
        self._courses = courses

    def of(self, courses: list[Course]) -> dict[str, str]:
        """the courses' titles, by their ids"""
        with self._engine.connect() as connection:
            ids = [course.id for course in courses]
            kept = dict(
                connection.execute(select(table.c.course_id, table.c.title).where(table.c.course_id.in_(ids))).all()
            )
        return {course.id: kept.get(course.id) or named(course.name) for course in courses}

    def title(self, student: str, name: str, title: str) -> Course:
        """gives the student's course the title; only its creator can"""
        course = self._courses.get(student, name)
        if course.owner != student:
            raise NotAllowed(f"only {course.owner}, who created {course.name!r}, can change its title")
        title = " ".join(title.split())
        if not title:
            raise InvalidRequest("a title can't be blank")
        mine = [c for c in self._courses.list(student) if c.owner == student and c.id != course.id]
        taken = next((t for t in self.of(mine).values() if t.casefold() == title.casefold()), None)
        if taken:
            raise Conflict(f"you already have a course titled {taken!r}")
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course.id))
            connection.execute(insert(table).values(course_id=course.id, title=title))
        return course

    def forget(self, course: Course) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course.id))
