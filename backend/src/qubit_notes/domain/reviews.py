"""When a student reviews each of their flashcards: spaced repetition, as in SM-2 (features/reviews.feature).

A card is due as soon as its deck is written. Reviewing it, the student says how well they remembered it, and that
changes its ease and decides its next interval: the better they remember it, the longer until it is due again. Only
the cards of the courses the student is a member of are reviewed: a reader's are hidden once they're removed from the
course, and come back, as they were, if it is shared with them again.
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from pydantic import BaseModel
from sqlalchemy import and_, func, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound
from qubit_notes.domain.sources import Source
from qubit_notes.domain.written import now

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
    due_at: datetime
    # how long until it was due again, the last time it was reviewed
    interval_days: int
    reviewed_at: datetime | None = None


class Due(BaseModel):
    """the cards due for review, oldest due first, and when the next of the others is due"""

    cards: list[ReviewCard]
    next_due_at: datetime | None = None


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

    def __init__(self, engine: Engine, courses: Courses, clock: Callable[[], datetime] = now):
        self._engine = engine
        self._courses = courses
        self.now = clock

    def new_schedule(self) -> dict:
        """the columns of a card just written: due now"""
        return {"ease": FIRST_EASE, "interval_days": 0, "repetitions": 0, "due_at": self.now(), "reviewed_at": None}

    def due(self, student: str, course_id: str | None = None) -> Due:
        """the student's cards due for review, in all their courses or in one"""
        cards = storage.flashcards
        at = self.now()
        courses = [course.id for course in self._courses.list(student)]
        if course_id is not None:
            courses = [course for course in courses if course == course_id]
        conditions = [cards.c.student == student, cards.c.due_at.is_not(None), cards.c.course_id.in_(courses)]
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(cards)
                .where(*conditions, cards.c.due_at <= at)
                .order_by(cards.c.due_at, cards.c.deck_id, cards.c.position)
            ).all()
            later = connection.execute(select(func.min(cards.c.due_at)).where(*conditions, cards.c.due_at > at))
            next_due_at = later.scalar()
        return Due(cards=[_card(row) for row in rows], next_due_at=_utc(next_due_at))

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
            reviewed = connection.execute(select(cards).where(mine)).first()
        return _card(reviewed)


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
