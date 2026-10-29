"""Papers, under My Papers: see features/papers.feature.

A collection of papers is a course of the platform that the app keeps apart from the student's courses, in
``storage.paper_collections``; so it is shared, and deleted, as a course is. Its papers are its material, all in one
topic of it (``SUBJECT``/``TOPIC``), which no one sees: a paper is read, noted and asked about as material is, and
the assistant on the topic is the assistant on the whole collection. Each paper is marked with an id of its own
(``PAPER``), by which the assistant searches it alone. Its details are kept in ``storage.paper_details``.
"""

import uuid
from pathlib import PurePosixPath

from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.conversion.details import Details, details
from qubit_notes.domain.course_titles import CourseTitles
from qubit_notes.domain.courses import SLUG, Course, Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotFound
from qubit_notes.domain.materials import TEXT_TYPES, Material, Materials, Upload
from qubit_notes.domain.topics import named
from qubit_notes.platform.port import MemberRole

# where a collection's papers are, in it
SUBJECT = "papers"
TOPIC = "papers"
# the metadata marking each paper with an id of its own
PAPER = "paper"


class Collection(BaseModel):
    id: str
    # in its links: lowercase words joined by hyphens
    name: str
    title: str
    owner: str
    role: MemberRole
    papers: int


class Paper(BaseModel):
    """a paper of a collection: the material, and its details"""

    material: Material
    details: Details


class PaperRecords:
    """Which courses are collections of papers, and the details of their papers."""

    def __init__(self, engine: Engine):
        self._engine = engine

    def collections(self) -> set[str]:
        """the ids of the courses that are collections"""
        with self._engine.connect() as connection:
            return set(connection.execute(select(storage.paper_collections.c.course_id)).scalars())

    def is_collection(self, course_id: str) -> bool:
        table = storage.paper_collections
        with self._engine.connect() as connection:
            found = connection.execute(select(table.c.course_id).where(table.c.course_id == course_id)).first()
        return found is not None

    def add_collection(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(insert(storage.paper_collections).values(course_id=course_id))

    def details(self, document_ids: list[str]) -> dict[str, Details]:
        table = storage.paper_details
        with self._engine.connect() as connection:
            rows = connection.execute(select(table).where(table.c.document_id.in_(document_ids))).all()
        return {
            row.document_id: Details(
                title=row.title, authors=list(row.authors), year=row.year, venue=row.venue, doi=row.doi
            )
            for row in rows
        }

    def keep(self, course_id: str, document_id: str, kept: Details) -> None:
        table = storage.paper_details
        values = kept.model_dump()
        with self._engine.begin() as connection:
            found = connection.execute(select(table.c.document_id).where(table.c.document_id == document_id)).first()
            if found:
                connection.execute(update(table).where(table.c.document_id == document_id).values(**values))
            else:
                connection.execute(insert(table).values(document_id=document_id, course_id=course_id, **values))

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(storage.paper_details).where(storage.paper_details.c.document_id == document_id))

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(storage.paper_details).where(storage.paper_details.c.course_id == course_id))
            table = storage.paper_collections
            connection.execute(delete(table).where(table.c.course_id == course_id))


class Papers:
    def __init__(self, records: PaperRecords, courses: Courses, titles: CourseTitles, materials: Materials):
        self._records = records
        self._courses = courses
        self._titles = titles
        self._materials = materials

    # collections

    def collections(self, student: str) -> list[Collection]:
        """the student's collections, and those shared with them"""
        ids = self._records.collections()
        return self._described(student, [course for course in self._courses.list(student) if course.id in ids])

    def create(self, student: str, name: str, title: str | None = None) -> Collection:
        if not SLUG.match(name):
            raise InvalidRequest(
                f"invalid collection name {name!r}: use lowercase words joined by hyphens, e.g. reinforcement-learning"
            )
        if any(course.name == name and course.owner == student for course in self._courses.list(student)):
            raise Conflict(f"you already have a course or a collection called {name!r}")
        course = self._courses.create(student, name)
        self._records.add_collection(course.id)
        if title and title.strip():
            self._titles.title_course(student, course, title, among=self._mine(student))
        return self._described(student, [course])[0]

    def get(self, student: str, collection_id: str) -> Course:
        """the collection, which the student must be a member of"""
        if not self._records.is_collection(collection_id):
            raise NotFound(f"no collection {collection_id!r}")
        return self._courses.get_by_id(student, collection_id)

    def collection(self, student: str, collection_id: str) -> Collection:
        return self._described(student, [self.get(student, collection_id)])[0]

    def title(self, student: str, collection_id: str, title: str) -> Collection:
        course = self.get(student, collection_id)
        self._titles.title_course(student, course, title, among=self._mine(student))
        return self.collection(student, collection_id)

    def delete(self, student: str, collection_id: str) -> None:
        """deletes the collection and its papers, for every member; only its creator can"""
        self._courses.delete_course(student, self.get(student, collection_id))

    def share(self, student: str, collection_id: str, with_student: str, role: MemberRole) -> Course:
        return self._courses.share_course(student, self.get(student, collection_id), with_student, role)

    def unshare(self, student: str, collection_id: str, with_student: str) -> Course:
        return self._courses.unshare_course(student, self.get(student, collection_id), with_student)

    def _mine(self, student: str) -> list[Course]:
        ids = self._records.collections()
        return [course for course in self._courses.list(student) if course.id in ids]

    def _described(self, student: str, courses: list[Course]) -> list[Collection]:
        titles = self._titles.of(courses)
        return [
            Collection(
                id=course.id,
                name=course.name,
                title=titles[course.id],
                owner=course.owner,
                role=course.role_of(student),
                papers=len(self._materials.list_of(course, SUBJECT, TOPIC)),
            )
            for course in courses
        ]

    # papers

    def papers(self, student: str, collection_id: str) -> list[Paper]:
        """the collection's papers, by their titles"""
        materials = self._materials.list_of(self.get(student, collection_id), SUBJECT, TOPIC)
        kept = self._records.details([m.document_id for m in materials])
        found = [Paper(material=m, details=kept.get(m.document_id) or _untitled(m.filename)) for m in materials]
        return sorted(found, key=lambda paper: (paper.details.title.casefold(), paper.material.filename))

    def paper(self, student: str, collection_id: str, document_id: str) -> Paper:
        found = next((p for p in self.papers(student, collection_id) if p.material.document_id == document_id), None)
        if found is None:
            raise NotFound(f"no paper {document_id!r}")
        return found

    def upload(self, student: str, collection_id: str, filename: str, content: bytes) -> Upload:
        """adds the paper to the collection, with the details it tells of itself"""
        course = self.get(student, collection_id)
        content_type = TEXT_TYPES.get(PurePosixPath(filename).suffix.lower())
        if content_type is None:
            raise InvalidRequest(
                f"{filename!r} can't be a paper: a paper must be a PDF, an EPUB, a Markdown or a text file"
            )
        upload = self._materials.upload_to(
            student, course, SUBJECT, TOPIC, filename, content, metadata={PAPER: uuid.uuid4().hex}
        )
        told = details(content_type, content)
        if not told.title:
            told.title = _untitled(filename).title
        self._records.keep(course.id, upload.document_id, told)
        return upload

    def describe(self, student: str, collection_id: str, document_id: str, given: Details) -> Paper:
        """gives the paper the details; only the collection's owners can"""
        course = self.get(student, collection_id)
        self._courses.require_owner(student, course)
        paper = self.paper(student, collection_id, document_id)
        title = " ".join(given.title.split())
        if not title:
            raise InvalidRequest("a paper needs a title")
        kept = Details(
            title=title,
            authors=[" ".join(author.split()) for author in given.authors if author.strip()],
            year=given.year,
            venue=given.venue.strip(),
            doi=given.doi.strip(),
        )
        self._records.keep(course.id, paper.material.document_id, kept)
        return Paper(material=paper.material, details=kept)

    def delete_paper(self, student: str, collection_id: str, document_id: str) -> Paper:
        course = self.get(student, collection_id)
        paper = self.paper(student, collection_id, document_id)
        self._materials.delete_from(student, course, paper.material)
        return paper


def _untitled(filename: str) -> Details:
    """the details of a paper that doesn't tell its title: titled after its file, e.g. "Ppo" for ppo.pdf"""
    return Details(title=named(PurePosixPath(filename).stem.replace("_", "-")))
