import uuid
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from typing import Any

import numpy as np
from loguru import logger
from sqlalchemy import Float, bindparam, delete, insert, select, text, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.platform.port import (
    Chunk,
    DocumentInfo,
    DownloadedFile,
    IndexInfo,
    IngestJob,
    IngestStatus,
    MemberRole,
    Message,
    PlatformError,
    PlatformHealth,
    Section,
    SectionText,
)
from qubit_notes.platform.standalone import chunking, parsing
from qubit_notes.platform.standalone.ai import AI, ProviderAI
from qubit_notes.platform.standalone.embeddings import Embedder, embedder_from
from qubit_notes.platform.standalone.files import Files, files_from
from qubit_notes.settings import Settings

indexes = storage.platform_indexes
members = storage.platform_index_members
documents = storage.platform_documents
jobs = storage.platform_jobs
sections = storage.platform_sections
chunks = storage.platform_chunks
conversations = storage.platform_conversations
messages = storage.platform_messages
memories = storage.platform_memories

# a job that still has to be done: left so when the app stopped, it's done when the app starts again
UNFINISHED = (IngestStatus.PENDING, IngestStatus.RUNNING)


def _now() -> datetime:
    return datetime.now(UTC)


def _file(document_id: str) -> str:
    return f"documents/{document_id}"


def _tokens(message: Message) -> int:
    """a message's tokens, estimated: about four characters each"""
    return len(message.content) // 4 + 1


class Ingestion:
    """Runs the ingestions in the background, a few at a time; inline where the database is in memory, as in tests,
    since its one connection can't be shared by threads that write at once."""

    def __init__(self, ingest: Callable[[str], None], workers: int, inline: bool):
        self._ingest = ingest
        self._executor = None if inline else ThreadPoolExecutor(workers, thread_name_prefix="ingestion")
        self._stopped = False

    def submit(self, job_id: str) -> None:
        if self._stopped:
            return
        if self._executor is None:
            self._ingest(job_id)
        else:
            self._executor.submit(self._ingest, job_id)

    def stop(self) -> None:
        """stops ingesting, as if the app stopped: unfinished jobs are left for when it starts again"""
        self._stopped = True
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)


class StandalonePlatform:
    """``StudyPlatform`` implemented by the app itself, with nothing but its database, a place for the uploaded files
    and a model provider: see ``features/standalone.feature``.

    Courses are indexes, and material is documents, kept in the app's database (``storage.platform_*``) with their
    files in ``files``. A document's ingestion reads it into its sections, divides those into chunks and embeds them,
    in the background; search ranks the chunks embedded with the app's model by their cosine similarity to the query,
    with pgvector on Postgres and in Python elsewhere. A chunk's ``score`` is that similarity: higher is closer.
    """

    def __init__(
        self,
        settings: Settings,
        engine: Engine,
        files: Files | None = None,
        embedder: Embedder | None = None,
        ai: AI | None = None,
    ):
        self._settings = settings
        self._engine = engine
        self._files = files or files_from(settings)
        self.embedder = embedder or embedder_from(settings)
        self.ai = ai or ProviderAI(settings)
        in_memory = engine.dialect.name == "sqlite" and engine.url.database in (None, "", ":memory:")
        self._ingestion = Ingestion(self._ingest, settings.ingestion_workers, inline=in_memory)
        self._resume()

    def stop(self) -> None:
        self._ingestion.stop()

    # health

    def health(self) -> PlatformHealth:
        services, errors = {}, []

        def report(service: str, why: str | None):
            services[service] = "NOT_SERVING" if why else "SERVING"
            if why:
                errors.append(why)

        try:
            with self._engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            report("database", None)
        except Exception as e:
            report("database", f"cannot reach the database: {e}")
        report("files", self._files.check())
        report("embeddings", self.embedder.missing())
        report("ai", self.ai.missing())
        return PlatformHealth(reachable=True, services=services, error="; ".join(errors) or None)

    # the app's credentials: its settings

    def store_credential(self, name: str, value: str) -> None:
        raise PlatformError(
            "UNIMPLEMENTED",
            f"the app keeps its keys in its settings: set QUBIT_NOTES_{name.upper()}_API_KEY instead",
        )

    def list_credentials(self) -> list[str]:
        keys = {
            "anthropic": self._settings.anthropic_api_key,
            "openai": self._settings.openai_api_key,
            "voyage": self._settings.voyage_api_key,
        }
        return [name for name, key in keys.items() if key]

    # indexes

    def _index(self, connection, name: str) -> IndexInfo | None:
        row = connection.execute(select(indexes).where(indexes.c.name == name)).first()
        if row is None:
            return None
        found = connection.execute(select(members).where(members.c.index_name == name)).all()
        return IndexInfo(
            name=row.name, owner=row.owner, members={member.member: MemberRole(member.role) for member in found}
        )

    def _require_index(self, connection, name: str) -> IndexInfo:
        index = self._index(connection, name)
        if index is None:
            raise PlatformError("NOT_FOUND", f"there is no index {name}")
        return index

    def create_index(self, name: str, owner: str) -> IndexInfo:
        with self._engine.begin() as connection:
            if self._index(connection, name) is not None:
                raise PlatformError("ALREADY_EXISTS", f"the index {name} exists")
            connection.execute(insert(indexes).values(name=name, owner=owner, created_at=_now()))
            connection.execute(insert(members).values(index_name=name, member=owner, role=MemberRole.OWNER.value))
            return self._index(connection, name)

    def get_index(self, name: str) -> IndexInfo | None:
        with self._engine.connect() as connection:
            return self._index(connection, name)

    def list_member_indexes(self, user: str) -> list[IndexInfo]:
        with self._engine.connect() as connection:
            names = connection.execute(
                select(members.c.index_name).where(members.c.member == user).order_by(members.c.index_name)
            ).scalars()
            return [self._index(connection, name) for name in names.all()]

    def set_index_member(self, name: str, user: str, role: MemberRole) -> IndexInfo:
        with self._engine.begin() as connection:
            self._require_index(connection, name)
            connection.execute(delete(members).where(members.c.index_name == name, members.c.member == user))
            connection.execute(insert(members).values(index_name=name, member=user, role=role.value))
            return self._index(connection, name)

    def remove_index_member(self, name: str, user: str) -> IndexInfo:
        with self._engine.begin() as connection:
            self._require_index(connection, name)
            connection.execute(delete(members).where(members.c.index_name == name, members.c.member == user))
            return self._index(connection, name)

    def delete_index(self, name: str) -> bool:
        with self._engine.begin() as connection:
            if self._index(connection, name) is None:
                return False
            document_ids = (
                connection.execute(select(documents.c.id).where(documents.c.index_name == name)).scalars().all()
            )
            for document_id in document_ids:
                self._delete_document(connection, document_id)
            connection.execute(delete(members).where(members.c.index_name == name))
            connection.execute(delete(indexes).where(indexes.c.name == name))
        for document_id in document_ids:
            self._files.delete(_file(document_id))
        return True

    # documents

    def ingest_document(
        self,
        index_name: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
        store_only: bool = False,
    ) -> IngestJob:
        document_id, job_id = uuid.uuid4().hex, uuid.uuid4().hex
        # a stored file, e.g. a video, has nothing to ingest
        status = IngestStatus.COMPLETED if store_only else IngestStatus.PENDING
        self._files.put(_file(document_id), content, content_type)
        with self._engine.begin() as connection:
            self._require_index(connection, index_name)
            connection.execute(
                insert(documents).values(
                    id=document_id,
                    index_name=index_name,
                    filename=filename,
                    content_type=content_type,
                    size_bytes=len(content),
                    metadata=metadata,
                    status=status.value,
                    job_id=job_id,
                    store_only=store_only,
                    created_at=_now(),
                )
            )
            self._add_job(connection, job_id, index_name, document_id, status)
        if not store_only:
            self._ingestion.submit(job_id)
        return IngestJob(job_id=job_id, document_id=document_id, status=status)

    def replace_document(
        self,
        index_name: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> IngestJob:
        job_id = uuid.uuid4().hex
        with self._engine.connect() as connection:
            if self._document(connection, index_name, document_id) is None:
                raise PlatformError("NOT_FOUND", f"there is no document {document_id} in {index_name}")
        self._files.put(_file(document_id), content, content_type)
        with self._engine.begin() as connection:
            # its sections and chunks are replaced once the new content is ingested
            connection.execute(
                update(documents)
                .where(documents.c.id == document_id)
                .values(
                    filename=filename,
                    content_type=content_type,
                    size_bytes=len(content),
                    metadata=metadata,
                    status=IngestStatus.PENDING.value,
                    job_id=job_id,
                    store_only=False,
                )
            )
            self._add_job(connection, job_id, index_name, document_id, IngestStatus.PENDING)
        self._ingestion.submit(job_id)
        return IngestJob(job_id=job_id, document_id=document_id, status=IngestStatus.PENDING)

    @staticmethod
    def _add_job(connection, job_id: str, index_name: str, document_id: str, status: IngestStatus) -> None:
        now = _now()
        connection.execute(
            insert(jobs).values(
                id=job_id,
                index_name=index_name,
                document_id=document_id,
                status=status.value,
                created_at=now,
                updated_at=now,
            )
        )

    def get_ingest_job(self, job_id: str) -> IngestJob | None:
        with self._engine.connect() as connection:
            row = connection.execute(select(jobs).where(jobs.c.id == job_id)).first()
        if row is None:
            return None
        return IngestJob(job_id=row.id, document_id=row.document_id, status=IngestStatus(row.status), error=row.error)

    @staticmethod
    def _info(row) -> DocumentInfo:
        return DocumentInfo(
            document_id=row.id,
            index_name=row.index_name,
            filename=row.filename,
            metadata=row.metadata or {},
            status=IngestStatus(row.status),
            content_type=row.content_type,
            size_bytes=row.size_bytes,
            version=row.job_id,
        )

    def _document(self, connection, index_name: str, document_id: str) -> DocumentInfo | None:
        row = connection.execute(
            select(documents).where(documents.c.id == document_id, documents.c.index_name == index_name)
        ).first()
        return self._info(row) if row else None

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]:
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(documents).where(documents.c.index_name == index_name).order_by(documents.c.created_at)
            ).all()
        found = [self._info(row) for row in rows]
        return [
            document
            for document in found
            if all(document.metadata.get(key) == value for key, value in (metadata_filter or {}).items())
        ]

    def get_document(self, index_name: str, document_id: str) -> DocumentInfo | None:
        with self._engine.connect() as connection:
            return self._document(connection, index_name, document_id)

    @staticmethod
    def _delete_document(connection, document_id: str) -> None:
        connection.execute(delete(chunks).where(chunks.c.document_id == document_id))
        connection.execute(delete(sections).where(sections.c.document_id == document_id))
        connection.execute(delete(jobs).where(jobs.c.document_id == document_id))
        connection.execute(delete(documents).where(documents.c.id == document_id))

    def delete_document(self, index_name: str, document_id: str) -> bool:
        with self._engine.begin() as connection:
            if self._document(connection, index_name, document_id) is None:
                return False
            self._delete_document(connection, document_id)
        self._files.delete(_file(document_id))
        return True

    # reading: a document's sections are there once its current content is ingested

    def _ready_sections(self, index_name: str, document_id: str) -> list[SectionText]:
        with self._engine.connect() as connection:
            document = self._document(connection, index_name, document_id)
            if document is None or document.status != IngestStatus.COMPLETED:
                return []
            rows = connection.execute(
                select(sections).where(sections.c.document_id == document_id).order_by(sections.c.position)
            ).all()
        return [
            SectionText(
                section=Section(
                    position=row.position,
                    title=row.title,
                    level=row.level,
                    page_start=row.page_start,
                    page_end=row.page_end,
                ),
                content=row.content,
            )
            for row in rows
        ]

    def list_sections(self, index_name: str, document_id: str) -> list[Section]:
        return [part.section for part in self._ready_sections(index_name, document_id)]

    def read_section(self, index_name: str, document_id: str, position: int) -> list[SectionText] | None:
        found = self._ready_sections(index_name, document_id)
        start = next((i for i, part in enumerate(found) if part.section.position == position), None)
        if start is None:
            return None
        level = found[start].section.level
        end = next((i for i in range(start + 1, len(found)) if found[i].section.level <= level), len(found))
        return found[start:end]

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile | None:
        document = self.get_document(index_name, document_id)
        if document is None:
            return None
        content = self._files.get(_file(document_id), offset, length)
        if content is None:
            return None
        return DownloadedFile(
            filename=document.filename,
            content_type=document.content_type or "application/octet-stream",
            content=content,
            size=document.size_bytes,
        )

    # search

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]:
        found = {
            document.document_id: document
            for document in self.list_documents(index_name, metadata_filter)
            if document.status == IngestStatus.COMPLETED
        }
        if not found:
            return []
        vector = self.embedder.embed([query], query=True)[0]
        where = [chunks.c.model == self.embedder.model, chunks.c.document_id.in_(found)]
        columns = [chunks.c.id, chunks.c.document_id, chunks.c.section, chunks.c.content]
        with self._engine.connect() as connection:
            if self._engine.dialect.name == "postgresql":
                distance = chunks.c.embedding.op("<=>", return_type=Float)(
                    bindparam("query", vector, type_=storage.Embedding())
                )
                rows = connection.execute(
                    select(*columns, (1 - distance).label("score")).where(*where).order_by(distance).limit(top_k)
                ).all()
                hits = [(row, row.score) for row in rows]
            else:
                rows = connection.execute(select(*columns, chunks.c.embedding).where(*where)).all()
                hits = _closest(rows, vector, top_k)
            titles = self._titles(connection, {(row.document_id, row.section) for row, _ in hits})
        return [
            Chunk(
                chunk_id=row.id,
                document_id=row.document_id,
                content=row.content,
                score=float(score),
                metadata={
                    **found[row.document_id].metadata,
                    "filename": found[row.document_id].filename,
                    "section": str(row.section),
                    "section_title": titles.get((row.document_id, row.section), ""),
                },
            )
            for row, score in hits
        ]

    @staticmethod
    def _titles(connection, wanted: set[tuple[str, int]]) -> dict[tuple[str, int], str]:
        if not wanted:
            return {}
        rows = connection.execute(
            select(sections.c.document_id, sections.c.position, sections.c.title).where(
                sections.c.document_id.in_({document_id for document_id, _ in wanted})
            )
        ).all()
        return {(row.document_id, row.position): row.title for row in rows}

    # ingestion

    def _resume(self) -> None:
        with self._engine.connect() as connection:
            unfinished = (
                connection.execute(
                    select(jobs.c.id)
                    .where(jobs.c.status.in_([status.value for status in UNFINISHED]))
                    .order_by(jobs.c.created_at)
                )
                .scalars()
                .all()
            )
        if unfinished:
            logger.info(f"resuming {len(unfinished)} unfinished ingestion(s)")
        for job_id in unfinished:
            self._ingestion.submit(job_id)

    def _set_status(self, connection, job_id: str, document_id: str, status: IngestStatus, error: str | None = None):
        connection.execute(
            update(jobs).where(jobs.c.id == job_id).values(status=status.value, error=error, updated_at=_now())
        )
        # the document's status is its current content's
        connection.execute(
            update(documents)
            .where(documents.c.id == document_id, documents.c.job_id == job_id)
            .values(status=status.value)
        )

    def _current(self, connection, job_id: str):
        """the job and its document, if the job still ingests the document's current content"""
        job = connection.execute(select(jobs).where(jobs.c.id == job_id)).first()
        if job is None:
            return None, None
        document = connection.execute(select(documents).where(documents.c.id == job.document_id)).first()
        if document is None or document.job_id != job_id:
            return job, None
        return job, document

    def _ingest(self, job_id: str) -> None:
        try:
            with self._engine.begin() as connection:
                job, document = self._current(connection, job_id)
                if job is None or job.status not in [status.value for status in UNFINISHED]:
                    return
                if document is None:
                    # the document was deleted, or given new content, which another job ingests
                    self._set_status(connection, job_id, job.document_id, IngestStatus.FAILED, "cancelled")
                    return
                self._set_status(connection, job_id, document.id, IngestStatus.RUNNING)

            content = self._files.get(_file(document.id))
            if content is None:
                raise RuntimeError("the uploaded file is missing")
            found = parsing.sections(document.filename, content)
            pieces = chunking.chunks(found)
            vectors = self.embedder.embed([piece for _, piece in pieces]) if pieces else []

            with self._engine.begin() as connection:
                job, current = self._current(connection, job_id)
                if current is None:
                    if job is not None:
                        self._set_status(connection, job_id, job.document_id, IngestStatus.FAILED, "cancelled")
                    return
                connection.execute(delete(sections).where(sections.c.document_id == document.id))
                connection.execute(delete(chunks).where(chunks.c.document_id == document.id))
                self._insert_sections(connection, document.id, found)
                self._insert_chunks(connection, document.index_name, document.id, job_id, pieces, vectors)
                self._set_status(connection, job_id, document.id, IngestStatus.COMPLETED)
        except Exception as e:
            logger.exception(f"the ingestion {job_id} failed")
            with self._engine.begin() as connection:
                job = connection.execute(select(jobs).where(jobs.c.id == job_id)).first()
                if job is not None:
                    self._set_status(connection, job_id, job.document_id, IngestStatus.FAILED, str(e) or repr(e))

    @staticmethod
    def _insert_sections(connection, document_id: str, found: list[SectionText]) -> None:
        if found:
            connection.execute(
                insert(sections),
                [
                    {
                        "document_id": document_id,
                        "position": part.section.position,
                        "title": part.section.title,
                        "level": part.section.level,
                        "page_start": part.section.page_start,
                        "page_end": part.section.page_end,
                        "content": part.content,
                    }
                    for part in found
                ],
            )

    def _insert_chunks(
        self,
        connection,
        index_name: str,
        document_id: str,
        version: str,
        pieces: list[tuple[int, str]],
        vectors: list[list[float]],
    ) -> None:
        if pieces:
            connection.execute(
                insert(chunks),
                [
                    {
                        "id": f"{document_id}:{version}:{self.embedder.model}:{i}",
                        "index_name": index_name,
                        "document_id": document_id,
                        "model": self.embedder.model,
                        "section": position,
                        "content": piece,
                        "embedding": vector,
                    }
                    for i, ((position, piece), vector) in enumerate(zip(pieces, vectors, strict=True))
                ],
            )

    def reembed(self, progress: Callable[[DocumentInfo], None] = lambda document: None) -> int:
        """Embeds the ingested material that has no chunks embedded with the app's model, e.g. after the model was
        changed, from the sections it was read into. Returns how many documents it embedded."""
        with self._engine.connect() as connection:
            embedded = select(chunks.c.document_id).where(chunks.c.model == self.embedder.model)
            rows = connection.execute(
                select(documents).where(
                    documents.c.status == IngestStatus.COMPLETED.value,
                    documents.c.store_only.is_(False),
                    documents.c.id.not_in(embedded),
                )
            ).all()
        count = 0
        for row in rows:
            document = self._info(row)
            pieces = chunking.chunks(self._ready_sections(document.index_name, document.document_id))
            if not pieces:
                continue
            vectors = self.embedder.embed([piece for _, piece in pieces])
            with self._engine.begin() as connection:
                self._insert_chunks(
                    connection, document.index_name, document.document_id, document.version, pieces, vectors
                )
            progress(document)
            count += 1
        return count

    # the AI

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
        return self.ai.complete(system, prompt, json_schema=json_schema, history=history)

    # conversations

    def start_conversation(self, user: str, conversation_id: str) -> None:
        with self._engine.begin() as connection:
            exists = connection.execute(select(conversations.c.id).where(conversations.c.id == conversation_id)).first()
            if exists is None:
                connection.execute(insert(conversations).values(id=conversation_id, member=user, created_at=_now()))

    def add_to_conversation(self, conversation_id: str, added: list[Message]) -> None:
        if not added:
            return
        now = _now()
        with self._engine.begin() as connection:
            connection.execute(
                insert(messages),
                [
                    {"conversation_id": conversation_id, "role": m.role, "content": m.content, "created_at": now}
                    for m in added
                ],
            )

    def conversation_context(self, conversation_id: str) -> list[Message]:
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(messages.c.role, messages.c.content)
                .where(messages.c.conversation_id == conversation_id)
                .order_by(messages.c.id.desc())
            ).all()
        recent, budget = [], self._settings.conversation_tokens
        for row in rows:
            message = Message(role=row.role, content=row.content)
            budget -= _tokens(message)
            if budget < 0:
                break
            recent.append(message)
        return list(reversed(recent))

    def end_conversation(self, conversation_id: str) -> bool:
        with self._engine.begin() as connection:
            connection.execute(delete(messages).where(messages.c.conversation_id == conversation_id))
            return connection.execute(delete(conversations).where(conversations.c.id == conversation_id)).rowcount > 0

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        with self._engine.begin() as connection:
            connection.execute(delete(memories).where(memories.c.member == user, memories.c.key == key))
            connection.execute(insert(memories).values(member=user, key=key, value=value))

    def get_memories(self, user: str) -> dict[str, Any]:
        with self._engine.connect() as connection:
            rows = connection.execute(select(memories).where(memories.c.member == user)).all()
        return {row.key: row.value for row in rows}

    def delete_memory(self, user: str, key: str) -> bool:
        with self._engine.begin() as connection:
            removed = connection.execute(delete(memories).where(memories.c.member == user, memories.c.key == key))
            return removed.rowcount > 0


def _closest(rows, vector: list[float], top_k: int) -> list[tuple[Any, float]]:
    """the rows whose embeddings are the most similar to the vector, by cosine similarity, with it"""
    if not rows:
        return []
    matrix = np.array([row.embedding for row in rows], dtype=np.float32)
    query = np.array(vector, dtype=np.float32)
    norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(query)
    similarity = matrix @ query / np.where(norms == 0, 1, norms)
    order = np.argsort(-similarity)[:top_k]
    return [(rows[i], float(similarity[i])) for i in order]
