import re
from dataclasses import dataclass

from qubit_notes.domain.errors import Conflict, InvalidRequest, NotAllowed, NotFound
from qubit_notes.platform.port import IndexInfo, MemberRole, StudyPlatform

# lowercase words joined by single hyphens, e.g. "numerical-methods"
SLUG = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# separates the creator from the course name in an index name: course names are unique per creator only,
# while gogi index names are unique across the platform
INDEX_SEPARATOR = "--"


@dataclass(frozen=True)
class Location:
    """Where material lives: ``<course>/<subject>/<topic>``."""

    course: str
    subject: str
    topic: str

    @classmethod
    def parse(cls, location: str) -> "Location":
        parts = location.split("/")
        if len(parts) != 3 or not all(SLUG.match(part) for part in parts):
            raise InvalidRequest(
                f"invalid location {location!r}: expected <course>/<subject>/<topic> in lowercase words joined by "
                "hyphens, e.g. aeronautics/numerical-methods/finite-elements"
            )
        return cls(*parts)

    def __str__(self) -> str:
        return f"{self.course}/{self.subject}/{self.topic}"


@dataclass(frozen=True)
class Course:
    """A course is a gogi index; its members are the index's members."""

    id: str
    name: str
    owner: str
    members: dict[str, MemberRole]

    @classmethod
    def from_index(cls, index: IndexInfo) -> "Course":
        return cls(id=index.name, name=course_name(index.name), owner=index.owner, members=dict(index.members))

    def role_of(self, student: str) -> MemberRole | None:
        return self.members.get(student)


def index_name(creator: str, course: str) -> str:
    return f"{creator}{INDEX_SEPARATOR}{course}"


def course_name(index: str) -> str:
    return index.split(INDEX_SEPARATOR, 1)[-1]


class Courses:
    """A student's courses, and who they are shared with."""

    def __init__(self, platform: StudyPlatform):
        self._platform = platform
        # called with every deleted course, before its index is, to forget what was in it
        self._on_delete = []

    def on_delete(self, forget) -> None:
        self._on_delete.append(forget)

    def list(self, student: str) -> list[Course]:
        courses = [Course.from_index(index) for index in self._platform.list_member_indexes(student)]
        return sorted(courses, key=lambda course: (course.name, course.owner))

    def find(self, student: str, name: str) -> Course | None:
        """The course called ``name`` that ``student`` can see: their own if they have one, else a shared one."""
        visible = [course for course in self.list(student) if course.name == name]
        own = [course for course in visible if course.owner == student]
        return (own or visible or [None])[0]

    def get(self, student: str, name: str) -> Course:
        course = self.find(student, name)
        if course is None:
            raise NotFound(f"no course {name!r}")
        return course

    def get_by_id(self, student: str, course_id: str) -> Course:
        """The course with the id, which ``student`` must be a member of"""
        index = self._platform.get_index(course_id)
        if index is None:
            raise NotFound(f"no course {course_id!r}")
        course = Course.from_index(index)
        if course.role_of(student) is None:
            raise NotAllowed(f"{course.name!r} is not shared with you")
        return course

    def create(self, student: str, name: str) -> Course:
        """a new course of the student's, of which they're the owner"""
        if not SLUG.match(name):
            raise InvalidRequest(
                f"invalid course name {name!r}: use lowercase words joined by hyphens, e.g. computer-science"
            )
        if any(course.name == name and course.owner == student for course in self.list(student)):
            raise Conflict(f"you already have the course {name!r}")
        return Course.from_index(self._platform.create_index(index_name(student, name), owner=student))

    def get_or_create(self, student: str, name: str) -> Course:
        course = self.find(student, name)
        if course is None:
            if not SLUG.match(name):
                raise InvalidRequest(f"invalid course name {name!r}")
            course = Course.from_index(self._platform.create_index(index_name(student, name), owner=student))
        return course

    def require_owner(self, student: str, course: Course) -> None:
        if course.role_of(student) != MemberRole.OWNER:
            raise NotAllowed(f"only the owners of {course.name!r} can do that")

    def delete(self, student: str, name: str) -> Course:
        """deletes the course and everything in it, for every member; only its creator can"""
        course = self.get(student, name)
        if course.owner != student:
            raise NotAllowed(f"only {course.owner}, who created {course.name!r}, can delete it")
        for forget in self._on_delete:
            forget(course)
        self._platform.delete_index(course.id)
        return course

    def share(self, student: str, name: str, with_student: str, role: MemberRole) -> Course:
        course = self.get(student, name)
        self.require_owner(student, course)
        return Course.from_index(self._platform.set_index_member(course.id, with_student, role))

    def unshare(self, student: str, name: str, with_student: str) -> Course:
        course = self.get(student, name)
        self.require_owner(student, course)
        if with_student not in course.members:
            raise NotFound(f"{name!r} is not shared with {with_student!r}")
        owners = [member for member, role in course.members.items() if role == MemberRole.OWNER]
        if owners == [with_student]:
            raise Conflict("a course must keep at least one owner")
        return Course.from_index(self._platform.remove_index_member(course.id, with_student))
