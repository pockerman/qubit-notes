import json
import uuid
from datetime import datetime

from loguru import logger
from pydantic import BaseModel, ValidationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.errors import InvalidRequest
from qubit_notes.domain.quizzes import AIFailed
from qubit_notes.domain.reviews import Reviews
from qubit_notes.domain.sources import OutOfDate, Scope, Source, Sources, SourceText
from qubit_notes.domain.written import (
    Row,
    forget_course_rows,
    forget_document,
    material,
    now,
    of_scope,
    scope_of,
    scope_values,
)
from qubit_notes.platform.port import StudyPlatform

MIN_CARDS, MAX_CARDS = 1, 30
# the most text a deck is written from; each section gets an equal share of it
MAX_CHARACTERS = 60_000

SYSTEM = """You write flashcards that help a student learn their study material by heart. Each card has a front, a
short question or a term, and a back, its answer, in a sentence or two. Make each card about one thing: a term, a
fact, a definition or an idea worth remembering. Cover the material evenly, and use only the material you are given.
Every card names the section it comes from by its reference, e.g. S3."""


class WrittenCard(BaseModel):
    front: str
    back: str
    # the reference of the section the card is from, e.g. "S3"
    source: str


class WrittenDeck(BaseModel):
    cards: list[WrittenCard]


class Card(BaseModel):
    id: str
    front: str
    back: str
    source: Source


class Deck(BaseModel):
    id: str
    scope: Scope
    cards: list[Card]
    sources: list[Source]
    created_at: datetime
    out_of_date: OutOfDate | None = None


class Flashcards:
    """Decks of flashcards on a section, a document or a topic, written by the AI from the material. Each student's
    decks are their own; the newest of a scope and size is shown until they ask for a new one. A deck's cards are
    reviewed (see reviews.py); a new deck of a scope takes the place of the earlier ones in the reviews."""

    def __init__(self, engine: Engine, platform: StudyPlatform, sources: Sources, reviews: Reviews):
        self._engine = engine
        self._platform = platform
        self._sources = sources
        self._reviews = reviews

    def get(self, student: str, scope: Scope, count: int, new: bool = False) -> Deck:
        if not MIN_CARDS <= count <= MAX_CARDS:
            raise InvalidRequest(f"a deck has between {MIN_CARDS} and {MAX_CARDS} cards")
        if not new:
            saved = [deck for deck in self._rows(student, scope) if deck.count == count]
            if saved:
                return self._deck(student, saved[0])
        return self._write(student, scope, count)

    def history(self, student: str, scope: Scope) -> list[Deck]:
        return [self._deck(student, row) for row in self._rows(student, scope)]

    def by_id(self, student: str, deck_id: str) -> Deck | None:
        """the student's deck, or None if it was deleted with its material"""
        decks = storage.flashcard_decks
        with self._engine.connect() as connection:
            row = connection.execute(select(decks).where(decks.c.id == deck_id, decks.c.student == student)).first()
        return self._deck(student, row) if row else None

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            ids = forget_document(connection, storage.flashcard_decks, document_id)
            if ids:
                connection.execute(delete(storage.flashcards).where(storage.flashcards.c.deck_id.in_(ids)))

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            ids = forget_course_rows(connection, storage.flashcard_decks, course_id)
            if ids:
                connection.execute(delete(storage.flashcards).where(storage.flashcards.c.deck_id.in_(ids)))

    def _write(self, student: str, scope: Scope, count: int) -> Deck:
        gathered = self._sources.gather(student, scope)
        cited = {f"S{i}": source for i, source in enumerate(gathered.sources, start=1)}
        prompt = f"Write {count} flashcards on this material.\n\n{material(gathered.sources, MAX_CHARACTERS)}"

        cards = None
        for _ in range(2):
            cards = self._cards(prompt, cited, count)
            if cards:
                break
        if not cards:
            raise AIFailed("the assistant could not write the flashcards; try again")

        sources = [Source(**source.model_dump(exclude={"content"})) for source in gathered.sources]
        row = {
            "id": uuid.uuid4().hex,
            **scope_values(student, scope),
            "sources": [source.model_dump() for source in sources],
            "documents": {d: ref.model_dump() for d, ref in gathered.documents.items()},
            "count": count,
            "created_at": now(),
        }
        earlier = [deck.id for deck in self._rows(student, scope)]
        schedule = self._reviews.new_schedule()
        with self._engine.begin() as connection:
            connection.execute(insert(storage.flashcard_decks).values(**row))
            connection.execute(
                insert(storage.flashcards),
                [
                    {
                        "id": uuid.uuid4().hex,
                        "deck_id": row["id"],
                        "student": student,
                        "course_id": scope.course_id,
                        "position": position,
                        **card,
                        **schedule,
                    }
                    for position, card in enumerate(cards)
                ],
            )
            if earlier:
                connection.execute(
                    update(storage.flashcards).where(storage.flashcards.c.deck_id.in_(earlier)).values(due_at=None)
                )
        return self._deck(student, Row(row))

    def _cards(self, prompt: str, cited: dict[str, SourceText], count: int) -> list[dict] | None:
        """the cards the AI writes, if there are at least ``count`` well-formed ones"""
        answer = self._platform.complete(SYSTEM, prompt, json_schema=WrittenDeck.model_json_schema())
        try:
            written = WrittenDeck.model_validate(json.loads(answer))
        except (ValueError, ValidationError) as e:
            logger.warning(f"the AI's flashcards are not valid: {e}")
            return None
        valid = [
            {
                "front": card.front.strip(),
                "back": card.back.strip(),
                "source": cited[card.source].model_dump(exclude={"content"}),
            }
            for card in written.cards
            if card.front.strip() and card.back.strip() and card.source in cited
        ]
        return valid[:count] if len(valid) >= count else None

    def _rows(self, student: str, scope: Scope) -> list:
        with self._engine.connect() as connection:
            return connection.execute(of_scope(storage.flashcard_decks, student, scope)).all()

    def _deck(self, student: str, row) -> Deck:
        cards = storage.flashcards
        with self._engine.connect() as connection:
            card_rows = connection.execute(
                select(cards).where(cards.c.deck_id == row.id).order_by(cards.c.position)
            ).all()
        scope = scope_of(row)
        return Deck(
            id=row.id,
            scope=scope,
            cards=[Card(id=c.id, front=c.front, back=c.back, source=Source(**c.source)) for c in card_rows],
            sources=[Source(**source) for source in row.sources],
            created_at=row.created_at,
            out_of_date=self._sources.out_of_date(student, scope, row.documents),
        )
