import uuid
from typing import Any

from study_assistant.platform.port import (
    Chunk,
    DocumentInfo,
    IndexInfo,
    IngestJob,
    IngestStatus,
    MemberRole,
    PlatformHealth,
)

SERVICES = ("gateway", "documents", "indexes", "llms", "prompts", "llm-sessions", "llm-tools", "guardrails")


class FakePlatform:
    """In-memory ``StudyPlatform`` for fast scenarios that need no gogi stack or API keys.

    Ingestion completes at once, and search ranks a document's text by how many query words it contains.
    """

    def __init__(self):
        self.reachable = True
        self.down: set[str] = set()
        self.indexes: dict[str, IndexInfo] = {}
        # index name to document id to (document, text)
        self.documents: dict[str, dict[str, tuple[DocumentInfo, str]]] = {}
        self.jobs: dict[str, IngestJob] = {}
        self.memories: dict[str, dict[str, Any]] = {}

    def health(self) -> PlatformHealth:
        if not self.reachable:
            return PlatformHealth(reachable=False, error="UNAVAILABLE: connection refused")
        return PlatformHealth(
            reachable=True,
            services={name: "NOT_SERVING" if name in self.down else "SERVING" for name in SERVICES},
        )

    # indexes

    def create_index(self, name: str, owner: str) -> IndexInfo:
        if name in self.indexes:
            raise ValueError(f"index {name} exists")
        self.indexes[name] = IndexInfo(name=name, owner=owner, members={owner: MemberRole.OWNER})
        self.documents[name] = {}
        return self.indexes[name]

    def get_index(self, name: str) -> IndexInfo | None:
        return self.indexes.get(name)

    def list_member_indexes(self, user: str) -> list[IndexInfo]:
        return [index for index in self.indexes.values() if user in index.members]

    def set_index_member(self, name: str, user: str, role: MemberRole) -> IndexInfo:
        self.indexes[name].members[user] = role
        return self.indexes[name]

    def remove_index_member(self, name: str, user: str) -> IndexInfo:
        self.indexes[name].members.pop(user, None)
        return self.indexes[name]

    def delete_index(self, name: str) -> bool:
        self.documents.pop(name, None)
        return self.indexes.pop(name, None) is not None

    # documents

    def ingest_document(
        self, index_name: str, filename: str, content: bytes, content_type: str, metadata: dict[str, str]
    ) -> IngestJob:
        document_id = uuid.uuid4().hex
        document = DocumentInfo(
            document_id=document_id,
            index_name=index_name,
            filename=filename,
            metadata=metadata,
            status=IngestStatus.COMPLETED,
        )
        self.documents[index_name][document_id] = (document, content.decode(errors="ignore"))
        job = IngestJob(job_id=uuid.uuid4().hex, document_id=document_id, status=IngestStatus.COMPLETED)
        self.jobs[job.job_id] = job
        return job

    def get_ingest_job(self, job_id: str) -> IngestJob | None:
        return self.jobs.get(job_id)

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]:
        return [
            document
            for document, _ in self.documents.get(index_name, {}).values()
            if _matches(document.metadata, metadata_filter)
        ]

    def delete_document(self, index_name: str, document_id: str) -> bool:
        return self.documents.get(index_name, {}).pop(document_id, None) is not None

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]:
        words = set(query.lower().split())
        hits = []
        for document, text in self.documents.get(index_name, {}).values():
            score = sum(word in text.lower() for word in words)
            if score and _matches(document.metadata, metadata_filter):
                hits.append(
                    Chunk(
                        chunk_id=f"{document.document_id}-0",
                        document_id=document.document_id,
                        content=text,
                        score=float(score),
                        metadata=document.metadata,
                    )
                )
        return sorted(hits, key=lambda chunk: -chunk.score)[:top_k]

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        self.memories.setdefault(user, {})[key] = value

    def get_memories(self, user: str) -> dict[str, Any]:
        return dict(self.memories.get(user, {}))

    def delete_memory(self, user: str, key: str) -> bool:
        return self.memories.get(user, {}).pop(key, None) is not None


def _matches(metadata: dict[str, str], metadata_filter: dict[str, str] | None) -> bool:
    return all(metadata.get(key) == value for key, value in (metadata_filter or {}).items())
