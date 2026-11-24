"""A subject pushed to a Git repository of the student's (features/subject_repository.feature).

A student connects a subject to a repository on GitHub with a token that may write to it; the token is kept encrypted
with the app's secret. Pushing writes everything of the subject that is the student's own, as Markdown, in one
commit: their notes and highlights, summaries, quizzes and flashcards, topic by topic in the order they are read, as
a downloaded subject is laid out (see subject_download.py). The material itself isn't pushed.

Pushing again writes the subject as it is then. The app remembers the files it wrote; one it wrote that isn't
written any more is removed, and files it didn't write are left as they are. A file is written only when its content
differs from the repository's, so nothing is committed when nothing changed.
"""

import hashlib
import re
from datetime import UTC, datetime
from pathlib import PurePosixPath
from typing import Protocol

from cryptography.fernet import InvalidToken
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.app_keys import fernet
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotAllowed, NotFound, StudyAssistantError
from qubit_notes.domain.flashcards import Deck, Flashcards
from qubit_notes.domain.materials import Material, Materials
from qubit_notes.domain.notes import Note, Notes, format_moment
from qubit_notes.domain.quizzes import Attempt, Quiz, Quizzes
from qubit_notes.domain.reviews import Reviews
from qubit_notes.domain.sources import Scope, Source
from qubit_notes.domain.subject_download import _csv, _Folder, _safe
from qubit_notes.domain.summaries import Summaries, Summary
from qubit_notes.domain.topics import Subject, Topics

table = storage.subject_repositories

# a repository on GitHub, by its owner and name, e.g. maria/numerical-methods
_REPOSITORY = re.compile(r"^[A-Za-z0-9-]+/[A-Za-z0-9._-]+$")


# the Git host the repositories are on


class RepositoryNotFound(StudyAssistantError):
    """the host has no such repository, or none the token can see"""


class PushRefused(StudyAssistantError):
    """the host refused to write to the repository, e.g. as the token may only read it"""


class RemoteRepository(BaseModel):
    name: str
    default_branch: str
    # whether the token may write to it
    writable: bool


class Commit(BaseModel):
    sha: str
    url: str


class GitHost(Protocol):
    def repository(self, name: str, token: str) -> RemoteRepository:
        """the repository, as the token sees it; raises RepositoryNotFound"""
        ...

    def files(self, name: str, token: str, branch: str) -> dict[str, str]:
        """the Git blob SHA of each file on the branch, by its path; none for an empty repository"""
        ...

    def commit(
        self, name: str, token: str, branch: str, write: dict[str, str], remove: list[str], message: str
    ) -> Commit:
        """one commit on the branch writing these files and removing those; raises PushRefused"""
        ...


def blob_sha(content: str) -> str:
    """the SHA Git knows a file's content by"""
    data = content.encode()
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


# what the app tells of a subject's repository


class Connection(BaseModel):
    course_id: str
    subject: str
    # the repository the subject is connected to, if it is; its token is never told
    repository: str | None = None
    connected_at: datetime | None = None
    # the last push, if it has been pushed
    pushed_at: datetime | None = None
    commit_sha: str | None = None
    commit_url: str | None = None

    @property
    def connected(self) -> bool:
        return self.repository is not None


class Pushed(BaseModel):
    # False when nothing changed since the last push, and nothing was committed
    pushed: bool
    commit_sha: str | None = None
    commit_url: str | None = None
    pushed_at: datetime | None = None
    # the files written and removed
    written: list[str] = []
    removed: list[str] = []


def _aware(moment: datetime | None) -> datetime | None:
    return moment.replace(tzinfo=UTC) if moment is not None and moment.tzinfo is None else moment


class SubjectRepositories:
    def __init__(
        self,
        engine: Engine,
        secret: str | None,
        host: GitHost,
        courses: Courses,
        topics: Topics,
        materials: Materials,
        notes: Notes,
        summaries: Summaries,
        quizzes: Quizzes,
        flashcards: Flashcards,
        reviews: Reviews,
    ):
        self._engine = engine
        # the app's secret, which the tokens are encrypted with
        self.secret = secret
        self.host = host
        self._courses = courses
        self._topics = topics
        self._materials = materials
        self._notes = notes
        self._summaries = summaries
        self._quizzes = quizzes
        self._flashcards = flashcards
        self._reviews = reviews

    # connecting

    def connect(self, student: str, course_name: str, subject: str, repository: str, token: str) -> Connection:
        course, _ = self._subject(student, course_name, subject)
        repository, token = repository.strip(), token.strip()
        if not _REPOSITORY.match(repository):
            raise InvalidRequest(f"{repository!r} is not a repository on GitHub: write it as owner/name")
        if not token:
            raise InvalidRequest("a repository is connected with a token that may write to it")
        encrypting = fernet(self.secret)
        if encrypting is None:
            raise Conflict("the app can't keep the token without its secret: set QUBIT_NOTES_SECRET_KEY first")
        try:
            remote = self.host.repository(repository, token)
        except RepositoryNotFound:
            raise NotFound(f"GitHub has no repository {repository!r} that the token can see") from None
        if not remote.writable:
            raise NotAllowed(f"the token may not write to {repository!r}: give it read and write access to contents")

        key = self._key(student, course.id, subject)
        with self._engine.begin() as connection:
            earlier = connection.execute(select(table).where(*key)).first()
            connection.execute(delete(table).where(*key))
            same = earlier is not None and earlier.repository == remote.name
            connection.execute(
                insert(table).values(
                    student=student,
                    course_id=course.id,
                    subject=subject,
                    repository=remote.name,
                    token=encrypting.encrypt(token.encode()).decode(),
                    connected_at=datetime.now(UTC),
                    # what was pushed to the same repository is still the app's to change; another has none of it
                    pushed_at=earlier.pushed_at if same else None,
                    commit_sha=earlier.commit_sha if same else None,
                    commit_url=earlier.commit_url if same else None,
                    files=list(earlier.files) if same else [],
                )
            )
        return self.connection(student, course_name, subject)

    def connection(self, student: str, course_name: str, subject: str) -> Connection:
        course, _ = self._subject(student, course_name, subject)
        row = self._row(student, course.id, subject)
        if row is None:
            return Connection(course_id=course.id, subject=subject)
        return Connection(
            course_id=course.id,
            subject=subject,
            repository=row.repository,
            connected_at=_aware(row.connected_at),
            pushed_at=_aware(row.pushed_at),
            commit_sha=row.commit_sha,
            commit_url=row.commit_url,
        )

    def disconnect(self, student: str, course_name: str, subject: str) -> None:
        """forgets the repository and its token; the repository is left as it is"""
        course, _ = self._subject(student, course_name, subject)
        with self._engine.begin() as connection:
            removed = connection.execute(delete(table).where(*self._key(student, course.id, subject))).rowcount
        if not removed:
            raise NotFound(f"the subject {subject!r} isn't connected to a repository")

    def forget_course(self, course_id: str) -> None:
        """every student's repositories of a deleted course's subjects; the repositories are left as they are"""
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.course_id == course_id))

    # pushing

    def push(self, student: str, course_name: str, subject: str) -> Pushed:
        course, found = self._subject(student, course_name, subject)
        row = self._row(student, course.id, subject)
        if row is None:
            raise Conflict(f"the subject {found.name!r} isn't connected to a repository: connect it first")
        decrypting = fernet(self.secret)
        try:
            token = decrypting.decrypt(row.token.encode()).decode() if decrypting else None
        except InvalidToken:
            token = None
        if token is None:
            raise Conflict("the app can't read the repository's token, kept with another secret: connect it again")

        files = self.files(student, course, found)
        try:
            remote = self.host.repository(row.repository, token)
        except RepositoryNotFound:
            raise NotFound(f"GitHub has no repository {row.repository!r} that the token can see") from None
        there = self.host.files(row.repository, token, remote.default_branch)
        write = {path: content for path, content in files.items() if there.get(path) != blob_sha(content)}
        remove = [path for path in row.files if path not in files and path in there]
        if not write and not remove:
            return Pushed(pushed=False, commit_sha=row.commit_sha, commit_url=row.commit_url)
        try:
            commit = self.host.commit(
                row.repository, token, remote.default_branch, write, remove, f"Qubit Notes: {found.name}"
            )
        except PushRefused as refused:
            raise NotAllowed(f"GitHub refused the push: {refused}") from None

        pushed_at = datetime.now(UTC)
        with self._engine.begin() as connection:
            connection.execute(
                update(table)
                .where(*self._key(student, course.id, subject))
                .values(pushed_at=pushed_at, commit_sha=commit.sha, commit_url=commit.url, files=sorted(files))
            )
        return Pushed(
            pushed=True,
            commit_sha=commit.sha,
            commit_url=commit.url,
            pushed_at=pushed_at,
            written=sorted(write),
            removed=sorted(remove),
        )

    def files(self, student: str, course: Course, subject: Subject) -> dict[str, str]:
        """what is pushed of the subject: each file's content by its path"""
        topics = [t for t in self._topics.of_course(course) if t.subject == subject.subject]
        materials = self._materials.list_of(course, subject.subject)
        names = {t.topic: t.name or t.topic for t in topics}
        documents = {m.document_id: m for m in materials}
        noted = {note.document_id for note in self._notes.all(student) if note.course_id == course.id}

        def of_subject(scope: Scope) -> bool:
            return scope.document_id in documents if scope.document_id else scope.subject == subject.subject

        summaries = [s for s in self._summaries.of_course(student, course.id) if of_subject(s.scope)]
        quizzes = [q for q in self._quizzes.of_course(student, course.id) if of_subject(q.scope)]
        decks = [d for d in self._flashcards.of_course(student, course.id) if of_subject(d.scope)]

        def attempts(quiz: Quiz) -> tuple[list[int], list[Attempt]]:
            return self._quizzes.answers(student, quiz.id), self._quizzes.attempts(student, quiz.id)

        files: dict[str, str] = {}
        root = _Folder("")
        readme_name = root.name("README.md")
        csv_name = root.name("flashcards.csv")
        contents: list[tuple[str, list[str]]] = []

        def write(folder: _Folder, of: str, kept: list, render) -> None:
            if kept:
                files[folder.name(f"{of}.md")] = render(kept)

        whole = [summaries, quizzes, decks]
        subject_wide = [[x for x in kind if x.scope.kind == "subject"] for kind in whole]
        write(root, "summaries", subject_wide[0], lambda k: _summaries(f"the subject {subject.name}", k))
        write(root, "quizzes", subject_wide[1], lambda k: _quizzes(f"the subject {subject.name}", k, attempts))
        write(root, "flashcards", subject_wide[2], lambda k: _decks(f"the subject {subject.name}", k))

        for number, topic in enumerate(topics, start=1):
            folder = _Folder(root.name(f"{number} {_safe(names[topic.topic], topic.topic)}"))
            of_topic = [[x for x in kind if x.scope.kind == "topic" and x.scope.topic == topic.topic] for kind in whole]
            title = f"the topic {names[topic.topic]}"
            write(folder, "summaries", of_topic[0], lambda k, t=title: _summaries(t, k))
            write(folder, "quizzes", of_topic[1], lambda k, t=title: _quizzes(t, k, attempts))
            write(folder, "flashcards", of_topic[2], lambda k, t=title: _decks(t, k))
            held = []
            for material in (m for m in materials if m.topic == topic.topic):
                of_material = [[x for x in kind if x.scope.document_id == material.document_id] for kind in whole]
                notes = self._notes_of(student, material) if material.document_id in noted else []
                if not notes and not any(of_material):
                    continue
                inside = _Folder(folder.name(_safe(PurePosixPath(material.filename).stem, material.document_id)))
                name = material.filename
                write(inside, "notes", notes, lambda k, n=name, m=material: _notes(n, m, k))
                write(inside, "summaries", of_material[0], lambda k, n=name: _summaries(n, k))
                write(inside, "quizzes", of_material[1], lambda k, n=name: _quizzes(n, k, attempts))
                write(inside, "flashcards", of_material[2], lambda k, n=name: _decks(n, k))
                held.append(material.filename)
            contents.append((folder.path, held))

        cards = [card for card in self._reviews.cards(student, course.id) if card.subject == subject.subject]
        if cards:
            files[csv_name] = _csv(cards, materials, names)
        files[readme_name] = _readme(subject, course, contents, bool(cards))
        return files

    def _notes_of(self, student: str, material: Material) -> list[Note]:
        try:
            return self._notes.of_material(student, material.course_id, material.document_id)
        except StudyAssistantError:
            # e.g. a material not processed yet, which has no sections to place its notes in
            return []

    def _subject(self, student: str, course_name: str, subject: str) -> tuple[Course, Subject]:
        course = self._courses.get(student, course_name)
        found = next((s for s in self._topics.subjects_of(course) if s.subject == subject), None)
        if found is None:
            raise NotFound(f"no subject {subject!r} in {course_name!r}")
        return course, found

    def _row(self, student: str, course_id: str, subject: str):
        with self._engine.connect() as connection:
            return connection.execute(select(table).where(*self._key(student, course_id, subject))).first()

    @staticmethod
    def _key(student: str, course_id: str, subject: str):
        return table.c.student == student, table.c.course_id == course_id, table.c.subject == subject


# the files, as Markdown


def _when(moment: datetime) -> str:
    return _aware(moment).strftime("%Y-%m-%d %H:%M UTC")


def _what(scope: Scope, sources: list[Source]) -> str:
    """what a summary, a quiz or a deck is of: a section, by its title, or a whole material, topic or subject"""
    if scope.section is not None:
        title = next((s.title for s in sources if s.section == scope.section), None)
        return f"the section {title}" if title else f"section {scope.section}"
    return {"document": "the whole material", "topic": "the whole topic"}.get(scope.kind, "the whole subject")


def _demoted(markdown: str) -> str:
    """the AI's Markdown with its headings under the file's own"""
    return re.sub(r"^(#{1,4}) ", r"\1## ", markdown, flags=re.M)


def _notes(filename: str, material: Material, notes: list[Note]) -> str:
    lines = [f"# Notes on {filename}", ""]
    if material.kind == "video":
        for note in notes:
            lines += [f"## {format_moment(note.at_seconds or 0)}", "", note.text, ""]
        return "\n".join(lines)
    section = None
    for note in notes:
        heading = "Notes whose passage is no longer in the material" if note.detached else note.section_title
        if heading != section:
            section = heading
            lines += [f"## {heading}", ""]
        lines += [f"> {' '.join((note.passage or '').split())}", ""]
        if note.text:
            lines += [note.text, ""]
    return "\n".join(lines)


def _summaries(of: str, summaries: list[Summary]) -> str:
    lines = [f"# Summaries of {of}", "", "Newest first.", ""]
    for summary in summaries:
        what = _what(summary.scope, summary.sources)
        lines += [f"## Summary of {what}, {_when(summary.created_at)}", "", _demoted(summary.content.strip()), ""]
    return "\n".join(lines)


def _quizzes(of: str, quizzes: list[Quiz], attempts_of) -> str:
    lines = [f"# Quizzes on {of}", "", "Newest first; the correct choice of each question is ticked.", ""]
    for quiz in quizzes:
        answers, attempts = attempts_of(quiz)
        lines += [f"## Quiz on {_what(quiz.scope, quiz.sources)}, {_when(quiz.created_at)}", ""]
        for number, (question, answer) in enumerate(zip(quiz.questions, answers), start=1):
            lines += [f"{number}. {question.question} *({question.source.filename} › {question.source.title})*"]
            lines += [f"   - [{'x' if i == answer else ' '}] {choice}" for i, choice in enumerate(question.choices)]
            lines += [""]
        if attempts:
            lines += ["Your scores:", ""]
            lines += [f"- {a.score} out of {a.total}, {_when(a.created_at)}" for a in attempts]
        else:
            lines += ["Not taken yet."]
        lines += [""]
    return "\n".join(lines)


def _decks(of: str, decks: list[Deck]) -> str:
    lines = [f"# Flashcards of {of}", "", "Newest deck first.", ""]
    for deck in decks:
        lines += [f"## Deck of {_what(deck.scope, deck.sources)}, {_when(deck.created_at)}", ""]
        for card in deck.cards:
            lines += [f"**{card.front}**", "", card.back, "", f"*{card.source.filename} › {card.source.title}*", ""]
    return "\n".join(lines)


def _readme(subject: Subject, course: Course, contents: list[tuple[str, list[str]]], cards: bool) -> str:
    lines = [
        f"# {subject.name}",
        "",
        f"What I made while studying {subject.name}, of the course {course.name}, pushed from Qubit Notes.",
        "",
        "Each topic is a folder, numbered in the order the topics are read, with a folder for each material I made"
        " something of: notes.md (my notes and highlights, in the order of the material), summaries.md, quizzes.md"
        " (each question with its correct choice ticked, and my scores) and flashcards.md. A topic's own summaries,"
        " quizzes and flashcards are in its folder. The material itself isn't here.",
        "",
    ]
    for folder, filenames in contents:
        lines.append(f"- {folder}: {', '.join(filenames)}" if filenames else f"- {folder}")
    if cards:
        lines += ["", "Every flashcard I review is in flashcards.csv (front, back, topic, material, section)."]
    return "\n".join(lines) + "\n"
