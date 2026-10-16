from typing import Any

import grpc
from gogi.gogi import Gogi
from gogi.models import DeleteLLMSessionMemoryRequest, GetLLMSessionMemoryRequest, SaveLLMSessionMemoryRequest
from gogi.models.gogi_index import GogiIndex, IndexRole
from gogi.models.ingest_document import IngestDocumentRequest
from gogi.models.search_documents import SearchDocumentsRequest
from loguru import logger

from study_assistant.platform.port import (
    Chunk,
    DocumentInfo,
    IndexInfo,
    IngestJob,
    IngestStatus,
    MemberRole,
    PlatformHealth,
)
from study_assistant.settings import Settings

_ROLES = {IndexRole.OWNER: MemberRole.OWNER, IndexRole.READER: MemberRole.READER}
_STATUSES = {
    "PENDING": IngestStatus.PENDING,
    "RUNNING": IngestStatus.RUNNING,
    "COMPLETED": IngestStatus.COMPLETED,
    "FAILED": IngestStatus.FAILED,
}


def _not_found(error: grpc.RpcError) -> bool:
    return error.code() == grpc.StatusCode.NOT_FOUND


class GogiPlatform:
    """``StudyPlatform`` implemented with the gogi-python SDK."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._gogi = Gogi(gateway_url=settings.gateway_url, logger=logger)

    def health(self) -> PlatformHealth:
        health = self._gogi.health.status()
        return PlatformHealth(
            reachable=health.reachable,
            services={name: str(status) for name, status in health.services.items()},
            error=health.error,
        )

    # indexes

    @staticmethod
    def _index(index: GogiIndex) -> IndexInfo:
        return IndexInfo(
            name=index.index_name,
            owner=index.owner,
            members={user: _ROLES[role] for user, role in index.members.items()},
        )

    def create_index(self, name: str, owner: str) -> IndexInfo:
        return self._index(self._gogi.indexes.create_index(index_name=name, owner_name=owner))

    def get_index(self, name: str) -> IndexInfo | None:
        try:
            return self._index(self._gogi.indexes.get_index_by_name(name))
        except grpc.RpcError as e:
            if _not_found(e):
                return None
            raise

    def list_member_indexes(self, user: str) -> list[IndexInfo]:
        return [self._index(index) for index in self._gogi.indexes.list_member_indexes(user)]

    def set_index_member(self, name: str, user: str, role: MemberRole) -> IndexInfo:
        return self._index(self._gogi.indexes.set_member(name, user, IndexRole(role.value)))

    def remove_index_member(self, name: str, user: str) -> IndexInfo:
        return self._index(self._gogi.indexes.remove_member(name, user))

    def delete_index(self, name: str) -> bool:
        return self._gogi.indexes.delete_index_by_name(name)

    # documents

    def ingest_document(
        self, index_name: str, filename: str, content: bytes, content_type: str, metadata: dict[str, str]
    ) -> IngestJob:
        job = self._gogi.documents.ingest_document(
            IngestDocumentRequest(
                index_name=index_name,
                filename=filename,
                content=content,
                content_type=content_type,
                metadata=metadata,
                chunk_strategy=self._settings.chunk_strategy,
                embeddings_model=self._settings.embeddings_model,
                embeddings_client=self._settings.embeddings_client,
            )
        )
        return IngestJob(job_id=job.job_id, document_id=job.document_id or "", status=_STATUSES[job.status])

    def get_ingest_job(self, job_id: str) -> IngestJob | None:
        try:
            job = self._gogi.documents.get_document_ingest_job(job_id)
        except grpc.RpcError as e:
            if _not_found(e):
                return None
            raise
        return IngestJob(
            job_id=job.job_id,
            document_id=job.document_id or "",
            status=_STATUSES[job.status],
            error=job.error_message,
        )

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]:
        return [
            DocumentInfo(
                document_id=document.document_id,
                index_name=document.index_name,
                filename=document.filename,
                metadata=document.custom_metadata or {},
                status=_STATUSES.get(document.status or "", IngestStatus.PENDING),
            )
            for document in self._gogi.documents.list_documents(index_name, metadata_filter=metadata_filter)
        ]

    def delete_document(self, index_name: str, document_id: str) -> bool:
        try:
            return self._gogi.documents.delete_document(index_name, document_id)
        except grpc.RpcError as e:
            if _not_found(e):
                return False
            raise

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]:
        response = self._gogi.documents.search_documents(
            SearchDocumentsRequest(
                index_name=index_name,
                query=query,
                top_k=top_k,
                embeddings_model=self._settings.embeddings_model,
                embeddings_client=self._settings.embeddings_client,
                metadata_filter=metadata_filter or {},
            )
        )
        return [
            Chunk(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                content=chunk.content,
                score=chunk.score,
                metadata=chunk.metadata or {},
            )
            for chunk in response.chunks
        ]

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        self._gogi.llm_session.save_memory(SaveLLMSessionMemoryRequest(user_id=user, key=key, value=value))

    def get_memories(self, user: str) -> dict[str, Any]:
        return dict(self._gogi.llm_session.get_memory(GetLLMSessionMemoryRequest(user_id=user)).memories)

    def delete_memory(self, user: str, key: str) -> bool:
        response = self._gogi.llm_session.delete_memory(DeleteLLMSessionMemoryRequest(user_id=user, key=key))
        return response.count > 0
