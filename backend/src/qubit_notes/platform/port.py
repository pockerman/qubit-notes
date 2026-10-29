from contextvars import ContextVar
from enum import StrEnum
from typing import Any, Literal, Protocol

from pydantic import BaseModel


class PlatformHealth(BaseModel):
    reachable: bool
    # service name to its status, e.g. {"gateway": "SERVING", "llms": "NOT_SERVING"}
    services: dict[str, str] = {}
    error: str | None = None
    # where the platform is gogi, whether gogi takes the app's key; gogi answers its health without one
    authenticated: bool = True
    # the model providers whose keys the platform needs and doesn't have, e.g. ["anthropic"]
    missing_keys: list[str] = []

    @property
    def serving(self) -> bool:
        return self.reachable and self.authenticated and all(status == "SERVING" for status in self.services.values())


# the provider and model a student chose to answer them, for the request being answered, rather than the app's
# (features/ai_model.feature); None: the app's
chosen_ai: ContextVar[tuple[str, str] | None] = ContextVar("chosen_ai", default=None)


class PlatformError(Exception):
    """The platform failed a request, e.g. it was unreachable or rejected it."""

    def __init__(self, code: str, details: str):
        super().__init__(f"{code}: {details}")
        self.code = code
        self.details = details


class MemberRole(StrEnum):
    OWNER = "owner"
    READER = "reader"


class IndexInfo(BaseModel):
    name: str
    # the user who created the index
    owner: str
    # user to role; includes the creator
    members: dict[str, MemberRole]


class IngestStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IngestJob(BaseModel):
    job_id: str
    document_id: str
    status: IngestStatus
    error: str | None = None


class DocumentInfo(BaseModel):
    document_id: str
    index_name: str
    filename: str
    metadata: dict[str, str] = {}
    # the status of the document's ingestion
    status: IngestStatus = IngestStatus.PENDING
    content_type: str = ""
    size_bytes: int = 0
    # changes when the document's content is replaced: the id of the job that ingested its current content
    version: str = ""


class Section(BaseModel):
    """A section of a document: a chapter or a heading within one, or a page of a PDF without an outline"""

    # 1-based, in the order of the document; identifies the section within its document
    position: int
    # empty for text before a document's first heading
    title: str = ""
    # 1 for a chapter, 2 for a heading within it, and so on
    level: int = 1
    page_start: int | None = None
    page_end: int | None = None


class SectionText(BaseModel):
    section: Section
    # the section's own text, without its subsections'
    content: str


class DownloadedFile(BaseModel):
    filename: str
    content_type: str
    content: bytes
    # the size of the whole file, when content is part of it
    size: int = 0


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float
    metadata: dict[str, str] = {}


class Message(BaseModel):
    """a message of a conversation with the AI"""

    role: Literal["user", "assistant"]
    content: str


class StudyPlatform(Protocol):
    """What qubit-notes needs of a platform.

    The domain depends on this port only. ``StandalonePlatform`` implements it with the app's own database, files and
    model providers, ``GogiPlatform`` with the gogi-python SDK, and the tests in memory. Methods return
    ``None``/``False`` for things that don't exist, rather than raising, so the domain decides what a missing thing
    means.
    """

    def health(self) -> PlatformHealth: ...

    # the app's own credentials in gogi, e.g. its Anthropic key; their values are never given back. The app's own
    # platform keeps none: it takes its keys from its settings
    def store_credential(self, name: str, value: str) -> None: ...

    def list_credentials(self) -> list[str]: ...

    # whether the platform keeps the app's model providers' keys itself, as gogi does; else the app keeps them
    keeps_keys: bool

    def use_key(self, provider: str, key: str | None) -> None:
        """the platform calls the model provider with this key from now on; None: it has no key for it from now on"""
        ...

    def use_model(self, provider: str, model: str) -> None:
        """the platform's AI is this model of this provider from now on (features/ai_model.feature)"""
        ...

    def has_key(self, provider: str) -> bool:
        """whether the platform has the app's key for the model provider; the key itself is never given back"""
        ...

    # indexes and their members
    def create_index(self, name: str, owner: str) -> IndexInfo: ...

    def get_index(self, name: str) -> IndexInfo | None: ...

    def list_member_indexes(self, user: str) -> list[IndexInfo]: ...

    def set_index_member(self, name: str, user: str, role: MemberRole) -> IndexInfo: ...

    def remove_index_member(self, name: str, user: str) -> IndexInfo: ...

    def delete_index(self, name: str) -> bool: ...

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
        """ingest the document; with store_only, keep the file without ingesting it, e.g. a video"""
        ...

    def replace_document(
        self,
        index_name: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> IngestJob:
        """give the document new content, e.g. after it was edited; it's ingested again"""
        ...

    def get_ingest_job(self, job_id: str) -> IngestJob | None: ...

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]: ...

    def get_document(self, index_name: str, document_id: str) -> DocumentInfo | None: ...

    def delete_document(self, index_name: str, document_id: str) -> bool: ...

    # reading: a document has no sections until its ingestion has completed
    def list_sections(self, index_name: str, document_id: str) -> list[Section]: ...

    def read_section(self, index_name: str, document_id: str, position: int) -> list[SectionText] | None:
        """the section at the position followed by its subsections, or None if there's no such section"""
        ...

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile | None:
        """the uploaded file, or length bytes of it from offset (to its end if length is 0)"""
        ...

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]: ...

    # the AI: an answer to the prompt, following the system prompt; with a JSON schema, a JSON object matching it.
    # The history is the conversation so far, oldest first, given to the AI before the prompt
    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str: ...

    # conversations with the AI, kept by the platform; a conversation's id is the caller's
    def start_conversation(self, user: str, conversation_id: str) -> None: ...

    def add_to_conversation(self, conversation_id: str, messages: list[Message]) -> None: ...

    def conversation_context(self, conversation_id: str) -> list[Message]:
        """the recent messages of the conversation, oldest first, as many as the AI is given"""
        ...

    def end_conversation(self, conversation_id: str) -> bool:
        """forgets the conversation; returns whether there was one"""
        ...

    # a user's long-term memories, key to a JSON-serialisable value
    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None: ...

    def get_memories(self, user: str) -> dict[str, Any]: ...

    def delete_memory(self, user: str, key: str) -> bool: ...
