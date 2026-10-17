from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel


class PlatformHealth(BaseModel):
    reachable: bool
    # service name to its status, e.g. {"gateway": "SERVING", "llms": "NOT_SERVING"}
    services: dict[str, str] = {}
    error: str | None = None

    @property
    def serving(self) -> bool:
        return self.reachable and all(status == "SERVING" for status in self.services.values())


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


class StudyPlatform(Protocol):
    """The slice of the gogi platform the study assistant needs.

    The domain depends on this port only. ``GogiPlatform`` implements it with the gogi-python SDK, and the
    tests implement it in memory. Methods return ``None``/``False`` for things that don't exist, rather than
    raising, so the domain decides what a missing thing means.
    """

    def health(self) -> PlatformHealth: ...

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

    # the AI: an answer to the prompt, following the system prompt; with a JSON schema, a JSON object matching it
    def complete(self, system: str, prompt: str, json_schema: dict[str, Any] | None = None) -> str: ...

    # a user's long-term memories, key to a JSON-serialisable value
    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None: ...

    def get_memories(self, user: str) -> dict[str, Any]: ...

    def delete_memory(self, user: str, key: str) -> bool: ...
