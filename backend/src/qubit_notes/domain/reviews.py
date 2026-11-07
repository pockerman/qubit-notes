"""When a student reviews each of their flashcards: spaced repetition, as in SM-2 (features/reviews.feature).

A card is due as soon as its deck is written. Reviewing it, the student says how well they remembered it, and that
changes its ease and decides its next interval: the better they remember it, the longer until it is due again. Only
the cards of the courses the student is a member of are reviewed: a reader's are hidden once they're removed from the
course, and come back, as they were, if it is shared with them again. Every review is also kept as it was made, in
``card_reviews``, for what the schedule of a card can't tell: how the student's memory of it has gone over time.
"""

import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import and_, func, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Course, Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound
from qubit_notes.domain.papers import PaperRecords
from qubit_notes.domain.sources import Source
from qubit_notes.domain.topics import Topics, named
from qubit_notes.domain.written import now
from qubit_notes.platform.port import StudyPlatform

ANSWERS = ("again", "hard", "good", "easy")
FIRST_EASE, MIN_EASE = 2.5, 1.3
# a card forgotten is due again soon, the same day
AGAIN = timedelta(minutes=10)


class ReviewCard(BaseModel):
    id: str
    deck_id: str
    course_id: str
    front: str
    back: str
    source: Source
    # the subject of its material, by id and by what it is called, which the student sees as it is now; none for a
    # paper, whose subject no one sees
    subject: str = ""
    subject_name: str = ""
    due_at: datetime
    # how long until it was due again, the last time it was reviewed
    interval_days: int
    reviewed_at: datetime | None = None


class Due(BaseModel):
    """the cards due for review, oldest due first, and when the next of the others is due"""

    cards: list[ReviewCard]
    next_due_at: datetime | None = None


class ReviewRecord(BaseModel):
    """a review of a card, as it was made"""

    id: str
    card_id: str
    course_id: str
    # the material of the card, and its subject, as on ReviewCard
    document_id: str
    subject: str = ""
    subject_name: str = ""
    front: str
    answer: str
    # when the card was due
    due_at: datetime
    ease_before: float
    ease_after: float
    interval_before: int
    interval_after: int
    reviewed_at: datetime


def next_schedule(ease: float, interval_days: int, repetitions: int, answer: str) -> tuple[float, int, int]:
    """the card's ease, interval and repetitions once the student remembered it so; an interval of 0 is due again
    in 10 minutes"""
    if answer == "again":
        return max(MIN_EASE, ease - 0.2), 0, 0
    if answer == "hard":
        return max(MIN_EASE, ease - 0.15), max(1, _rounded(interval_days * 1.2)), repetitions + 1
    if answer == "good":
        interval = 1 if repetitions == 0 else 6 if repetitions == 1 else _rounded(interval_days * ease)
        return ease, interval, repetitions + 1
    ease += 0.15
    return ease, 4 if repetitions == 0 else _rounded(interval_days * ease * 1.3), repetitions + 1


def _rounded(days: float) -> int:
    # halves up, unlike round()
    return int(days + 0.5)


def _utc(moment: datetime | None) -> datetime | None:
    # SQLite gives back the moments it keeps without their time zone, which is UTC
    return moment.replace(tzinfo=UTC) if moment is not None and moment.tzinfo is None else moment


class Reviews:
    """Each student's reviews of the cards of their decks. ``now`` is the clock the reviews go by."""

    def __init__(
        self,
        engine: Engine,
        courses: Courses,
        platform: StudyPlatform,
        topics: Topics,
        papers: PaperRecords,
        clock: Callable[[], datetime] = now,
    ):
        self._engine = engine
        self._courses = courses
        self._platform = platform
        self._topics = topics
        self._papers = papers
        self.now = clock

    def new_schedule(self) -> dict:
        """the columns of a card just written: due now"""
        return {"ease": FIRST_EASE, "interval_days": 0, "repetitions": 0, "due_at": self.now(), "reviewed_at": None}

    def due(self, student: str, course_id: str | None = None) -> Due:
        """the student's cards due for review, in all their courses or in one"""
        cards = storage.flashcards
        at = self.now()
        courses = self._of(student, course_id)
        ids = [course.id for course in courses]
        conditions = [cards.c.student == student, cards.c.due_at.is_not(None), cards.c.course_id.in_(ids)]
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(cards)
                .where(*conditions, cards.c.due_at <= at)
                .order_by(cards.c.due_at, cards.c.deck_id, cards.c.position)
            ).all()
            later = connection.execute(select(func.min(cards.c.due_at)).where(*conditions, cards.c.due_at > at))
            next_due_at = later.scalar()
        return Due(cards=self._with_subjects(rows, courses), next_due_at=_utc(next_due_at))

    def _of(self, student: str, course_id: str | None) -> list[Course]:
        """the student's courses, or the one if they are a member of it"""
        return [course for course in self._courses.list(student) if course_id in (None, course.id)]

    def _with_subjects(self, rows, courses: list[Course]) -> list[ReviewCard]:
        subjects = self._subjects(rows, courses)
        return [_card(row).model_copy(update=subjects.get(row.source["document_id"], {})) for row in rows]

    def _subjects(self, rows, courses: list[Course]) -> dict[str, dict[str, str]]:
        """the subject of each material of the courses of the rows, but for the papers of collections, by the
        material's id"""
        found = {}
        among = {row.course_id for row in rows}
        for course in courses:
            if course.id not in among or self._papers.is_collection(course.id):
                continue
            names = {subject.subject: subject.name for subject in self._topics.subjects_of(course)}
            for document in self._platform.list_documents(course.id):
                subject = document.metadata.get("subject", "")
                found[document.document_id] = {"subject": subject, "subject_name": names.get(subject, named(subject))}
        return found

    def review(self, student: str, card_id: str, answer: str) -> ReviewCard:
        """schedules the card's next review by how well the student remembered it: again, hard, good or easy"""
        answer = answer.strip().lower()
        if answer not in ANSWERS:
            raise InvalidRequest("answer again, hard, good or easy")
        cards = storage.flashcards
        courses = [course.id for course in self._courses.list(student)]
        mine = and_(
            cards.c.id == card_id,
            cards.c.student == student,
            cards.c.due_at.is_not(None),
            cards.c.course_id.in_(courses),
        )
        with self._engine.begin() as connection:
            row = connection.execute(select(cards).where(mine)).first()
            if row is None:
                raise NotFound(f"no card {card_id!r} to review")
            ease, interval, repetitions = next_schedule(row.ease, row.interval_days, row.repetitions, answer)
            at = self.now()
            due_at = at + (timedelta(days=interval) if interval else AGAIN)
            connection.execute(
                update(cards)
                .where(mine)
                .values(ease=ease, interval_days=interval, repetitions=repetitions, due_at=due_at, reviewed_at=at)
            )
            connection.execute(
                insert(storage.card_reviews).values(
                    id=uuid.uuid4().hex,
                    card_id=row.id,
                    deck_id=row.deck_id,
                    student=student,
                    course_id=row.course_id,
                    answer=answer,
                    due_at=row.due_at,
                    ease_before=row.ease,
                    ease_after=ease,
                    interval_before=row.interval_days,
                    interval_after=interval,
                    reviewed_at=at,
                )
            )
            reviewed = connection.execute(select(cards).where(mine)).first()
        return _card(reviewed)

    def not_reviewed(self, student: str, course_id: str | None = None, limit: int = 100) -> list[ReviewCard]:
        """the student's cards they have never reviewed, oldest first, in all their courses or in one; those of an
        earlier deck are no longer reviewed, so are not among them"""
        cards = storage.flashcards
        courses = self._of(student, course_id)
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(cards)
                .where(
                    cards.c.student == student,
                    cards.c.course_id.in_([course.id for course in courses]),
                    cards.c.due_at.is_not(None),
                    cards.c.reviewed_at.is_(None),
                )
                .order_by(cards.c.due_at, cards.c.deck_id, cards.c.position)
                .limit(limit)
            ).all()
        return self._with_subjects(rows, courses)

    def history(self, student: str, course_id: str | None = None, limit: int = 100) -> list[ReviewRecord]:
        """the student's reviews, newest first, in all their courses or in one"""
        reviews, cards = storage.card_reviews, storage.flashcards
        courses = self._of(student, course_id)
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(reviews, cards.c.front, cards.c.source)
                .join(cards, cards.c.id == reviews.c.card_id)
                .where(reviews.c.student == student, reviews.c.course_id.in_([course.id for course in courses]))
                .order_by(reviews.c.reviewed_at.desc())
                .limit(limit)
            ).all()
        subjects = self._subjects(rows, courses)
        return [
            ReviewRecord(
                id=row.id,
                card_id=row.card_id,
                course_id=row.course_id,
                document_id=row.source["document_id"],
                **subjects.get(row.source["document_id"], {}),
                front=row.front,
                answer=row.answer,
                due_at=_utc(row.due_at),
                ease_before=row.ease_before,
                ease_after=row.ease_after,
                interval_before=row.interval_before,
                interval_after=row.interval_after,
                reviewed_at=_utc(row.reviewed_at),
            )
            for row in rows
        ]


def _card(row) -> ReviewCard:
    return ReviewCard(
        id=row.id,
        deck_id=row.deck_id,
        course_id=row.course_id,
        front=row.front,
        back=row.back,
        source=Source(**row.source),
        due_at=_utc(row.due_at),
        interval_days=row.interval_days,
        reviewed_at=_utc(row.reviewed_at),
    )
