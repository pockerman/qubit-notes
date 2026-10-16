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
        self, index_name: str, filename: str, content: bytes, content_type: str, metadata: dict[str, str]
    ) -> IngestJob: ...

    def get_ingest_job(self, job_id: str) -> IngestJob | None: ...

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]: ...

    def delete_document(self, index_name: str, document_id: str) -> bool: ...

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]: ...

    # a user's long-term memories, key to a JSON-serialisable value
    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None: ...

    def get_memories(self, user: str) -> dict[str, Any]: ...

    def delete_memory(self, user: str, key: str) -> bool: ...
