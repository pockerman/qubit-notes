import uuid
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.sources import OutOfDate, Scope, Source, Sources, SourceText
from qubit_notes.domain.written import forget_course_rows, forget_document, now, of_scope, scope_of, scope_values
from qubit_notes.platform.port import StudyPlatform

SYSTEM = """You help a student revise. You write summaries of their study material: clear, accurate and concise,
in Markdown, keeping the key definitions, results and reasoning. Use only the material you are given."""

# the most text summarised at once; more is summarised in parts, and the parts' summaries summarised
MAX_CHARACTERS = 60_000


class Summary(BaseModel):
    id: str
    scope: Scope
    content: str
    sources: list[Source]
    created_at: datetime
    # how a topic's material changed since the summary was written, if it has
    out_of_date: OutOfDate | None = None


def _material(sources: list[SourceText]) -> str:
    return "\n\n".join(f"## {s.filename} › {s.title}\n\n{s.content}" for s in sources)


def _batches(sources: list[SourceText]) -> list[list[SourceText]]:
    batches, batch, size = [], [], 0
    for source in sources:
        length = len(source.content) + len(source.title) + len(source.filename)
        if batch and size + length > MAX_CHARACTERS:
            batches.append(batch)
            batch, size = [], 0
        batch.append(source)
        size += length
    return batches + [batch] if batch else batches


class Summaries:
    """Summaries of a section, a document or a topic, written by the AI from the material. Each student's
    summaries are their own; the newest is shown until they ask for a new one."""

    def __init__(self, engine: Engine, platform: StudyPlatform, sources: Sources):
        self._engine = engine
        self._platform = platform
        self._sources = sources

    def get(self, student: str, scope: Scope, new: bool = False) -> Summary:
        """the newest saved summary of the scope, or a new one if there's none or ``new``"""
        if not new:
            saved = self.history(student, scope)
            if saved:
                return saved[0]
        return self._write(student, scope)

    def history(self, student: str, scope: Scope) -> list[Summary]:
        with self._engine.connect() as connection:
            rows = connection.execute(of_scope(storage.summaries, student, scope)).all()
        return [self._summary(student, row) for row in rows]

    def by_id(self, student: str, summary_id: str) -> Summary | None:
        """the student's summary, or None if it was deleted with its material"""
        table = storage.summaries
        with self._engine.connect() as connection:
            row = connection.execute(select(table).where(table.c.id == summary_id, table.c.student == student)).first()
        return self._summary(student, row) if row else None

    def forget_material(self, document_id: str) -> None:
        with self._engine.begin() as connection:
            forget_document(connection, storage.summaries, document_id)

    def forget_course(self, course_id: str) -> None:
        with self._engine.begin() as connection:
            forget_course_rows(connection, storage.summaries, course_id)

    def _write(self, student: str, scope: Scope) -> Summary:
        gathered = self._sources.gather(student, scope)
        batches = _batches(gathered.sources)
        if len(batches) == 1:
            content = self._summarise(_material(batches[0]))
        else:
            parts = [self._summarise(_material(batch)) for batch in batches]
            content = self._summarise("\n\n".join(parts), of_summaries=True)

        sources = [Source(**source.model_dump(exclude={"content"})) for source in gathered.sources]
        row = {
            "id": uuid.uuid4().hex,
            **scope_values(student, scope),
            "sources": [source.model_dump() for source in sources],
            "documents": {d: ref.model_dump() for d, ref in gathered.documents.items()},
            "content": content,
            "created_at": now(),
        }
        with self._engine.begin() as connection:
            connection.execute(insert(storage.summaries).values(**row))
        return Summary(id=row["id"], scope=scope, content=content, sources=sources, created_at=row["created_at"])

    def _summarise(self, material: str, of_summaries: bool = False) -> str:
        what = "these summaries of parts of the material into one summary" if of_summaries else "this material"
        return self._platform.complete(SYSTEM, f"Summarise {what}.\n\n{material}").strip()

    def _summary(self, student: str, row) -> Summary:
        scope = scope_of(row)
        return Summary(
            id=row.id,
            scope=scope,
            content=row.content,
            sources=[Source(**source) for source in row.sources],
            created_at=row.created_at,
            out_of_date=self._sources.out_of_date(student, scope, row.documents),
        )
