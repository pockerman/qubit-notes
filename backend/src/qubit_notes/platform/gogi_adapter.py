import functools
import json
from typing import Any

import grpc
from gogi.gogi import Gogi
from gogi.models import DeleteLLMSessionMemoryRequest, GetLLMSessionMemoryRequest, SaveLLMSessionMemoryRequest
from gogi.models.gogi_index import GogiIndex, IndexRole
from gogi.models.ingest_document import IngestDocumentRequest
from gogi.models.llm.llm_message import LLMMessage
from gogi.models.llm.llm_response_format import LLMResponseFormat
from gogi.models.llm.llm_run_request_config import LLMRunRequestConfig
from gogi.models.llm.requests.llm_run_request import LLMRunRequest
from gogi.models.llm.requests.llm_session.add_messages_to_llm_session_request import AddMessagesToLLMSessionRequest
from gogi.models.llm.requests.llm_session.create_llm_session_request import CreateLLMSessionRequest
from gogi.models.llm.requests.llm_session.delete_llm_session_request import DeleteLLMSessionRequest
from gogi.models.llm.requests.llm_session.get_messages_from_llm_session_request import (
    GetMessagesFromLLMSessionRequest,
)
from gogi.models.search_documents import SearchDocumentsRequest
from loguru import logger

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
from qubit_notes.settings import Settings

_ROLES = {IndexRole.OWNER: MemberRole.OWNER, IndexRole.READER: MemberRole.READER}
_STATUSES = {
    "PENDING": IngestStatus.PENDING,
    "RUNNING": IngestStatus.RUNNING,
    "COMPLETED": IngestStatus.COMPLETED,
    "FAILED": IngestStatus.FAILED,
    # the document was deleted during its ingestion
    "CANCELLED": IngestStatus.FAILED,
}


def _not_found(error: grpc.RpcError) -> bool:
    return error.code() == grpc.StatusCode.NOT_FOUND


def _platform_errors(cls):
    """Turns the gRPC errors of every public method into ``PlatformError``s, so callers need not know gRPC."""

    def wrap(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            try:
                return method(*args, **kwargs)
            except grpc.RpcError as e:
                raise PlatformError(e.code().name, e.details() or "") from e

        return wrapper

    for name, method in list(vars(cls).items()):
        if callable(method) and not name.startswith("_"):
            setattr(cls, name, wrap(method))
    return cls


@_platform_errors
class GogiPlatform:
    """``StudyPlatform`` implemented with the gogi-python SDK."""

    def __init__(self, settings: Settings):
        self._settings = settings
        root_certificates = None
        if settings.gogi_ca_file:
            with open(settings.gogi_ca_file, "rb") as ca_file:
                root_certificates = ca_file.read()
        self._gogi = Gogi(
            gateway_url=settings.gateway_url,
            logger=logger,
            api_key=settings.gogi_api_key,
            root_certificates=root_certificates,
        )

    def health(self) -> PlatformHealth:
        health = self._gogi.health.status()
        result = PlatformHealth(
            reachable=health.reachable,
            services={name: str(status) for name, status in health.services.items()},
            error=health.error,
        )
        if health.reachable:
            # gogi answers its health without a key, so a call that needs the app's key tells whether gogi takes it
            try:
                self._gogi.credentials.list()
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAUTHENTICATED:
                    result.authenticated = False
                    result.error = f"gogi does not take the app's key: {e.details()}"
        return result

    # the app's credentials

    def store_credential(self, name: str, value: str) -> None:
        self._gogi.credentials.store(name, value)

    def list_credentials(self) -> list[str]:
        return [credential.name for credential in self._gogi.credentials.list()]

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
        self,
        index_name: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
        store_only: bool = False,
    ) -> IngestJob:
        job = self._gogi.documents.ingest_document(
            IngestDocumentRequest(
                index_name=index_name,
                filename=filename,
                content=content,
                content_type=content_type,
                metadata=metadata,
                chunk_strategy=self._settings.chunk_strategy,
                # a stored file, e.g. a video, is not embedded
                embedding_models=[] if store_only else [self._settings.embedding_model],
            )
        )
        return IngestJob(job_id=job.job_id, document_id=job.document_id or "", status=_STATUSES[job.status])

    def replace_document(
        self,
        index_name: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> IngestJob:
        job = self._gogi.documents.ingest_document(
            IngestDocumentRequest(
                index_name=index_name,
                document_id=document_id,
                filename=filename,
                content=content,
                content_type=content_type,
                metadata=metadata,
                chunk_strategy=self._settings.chunk_strategy,
                embedding_models=[self._settings.embedding_model],
                replace=True,
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

    @staticmethod
    def _document(document) -> DocumentInfo:
        return DocumentInfo(
            document_id=document.document_id,
            index_name=document.index_name,
            filename=document.filename,
            metadata=document.custom_metadata or {},
            status=_STATUSES.get(document.status or "", IngestStatus.PENDING),
            content_type=document.content_type or "",
            size_bytes=document.size_bytes,
            version=document.job_id or "",
        )

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]:
        return [
            self._document(document)
            for document in self._gogi.documents.list_documents(index_name, metadata_filter=metadata_filter)
        ]

    def get_document(self, index_name: str, document_id: str) -> DocumentInfo | None:
        try:
            return self._document(self._gogi.documents.get_document(index_name, document_id))
        except grpc.RpcError as e:
            if _not_found(e):
                return None
            raise

    @staticmethod
    def _section(section) -> Section:
        return Section(
            position=section.position,
            title=section.title,
            level=section.level,
            page_start=section.page_start,
            page_end=section.page_end,
        )

    def list_sections(self, index_name: str, document_id: str) -> list[Section]:
        return [self._section(section) for section in self._gogi.documents.list_sections(index_name, document_id)]

    def read_section(self, index_name: str, document_id: str, position: int) -> list[SectionText] | None:
        try:
            parts = self._gogi.documents.get_section(index_name, document_id, position, include_subsections=True)
        except grpc.RpcError as e:
            if _not_found(e):
                return None
            raise
        return [SectionText(section=self._section(part.section), content=part.content) for part in parts]

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile | None:
        try:
            document, content = self._gogi.documents.download_document(index_name, document_id, offset, length)
        except grpc.RpcError as e:
            if _not_found(e):
                return None
            raise
        return DownloadedFile(
            filename=document.filename,
            content_type=document.content_type or "application/octet-stream",
            content=content,
            size=document.size_bytes,
        )

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
                embedding_model=self._settings.embedding_model,
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

    # the AI

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
        response = self._gogi.llm_clients.run(
            LLMRunRequest(
                config=LLMRunRequestConfig(
                    provider=self._settings.llm_provider,
                    model=self._settings.llm_model,
                    max_tokens=self._settings.llm_max_tokens,
                ),
                messages=[
                    LLMMessage(role="system", content=system),
                    *(LLMMessage(role=message.role, content=message.content) for message in history or []),
                    LLMMessage(role="user", content=prompt),
                ],
                response_format=(
                    LLMResponseFormat(response_type="json_schema", response_schema_json=json.dumps(json_schema))
                    if json_schema
                    else None
                ),
            )
        )
        return response.content

    # conversations: gogi's sessions

    def start_conversation(self, user: str, conversation_id: str) -> None:
        self._gogi.llm_session.get_or_create_session(CreateLLMSessionRequest(user_id=user, session_id=conversation_id))

    def add_to_conversation(self, conversation_id: str, messages: list[Message]) -> None:
        self._gogi.llm_session.add_messages_to_session(
            AddMessagesToLLMSessionRequest(
                session_id=conversation_id,
                messages=[LLMMessage(role=message.role, content=message.content) for message in messages],
            )
        )

    def conversation_context(self, conversation_id: str) -> list[Message]:
        response = self._gogi.llm_session.get_messages(
            GetMessagesFromLLMSessionRequest(
                session_id=conversation_id, strategy="truncate", token_budget=self._settings.conversation_tokens
            )
        )
        return [
            Message(role=message.role, content=message.content or "")
            for message in response.messages
            if message.role in ("user", "assistant")
        ]

    def end_conversation(self, conversation_id: str) -> bool:
        try:
            return self._gogi.llm_session.delete_session(DeleteLLMSessionRequest(session_id=conversation_id)).success
        except grpc.RpcError as e:
            if _not_found(e):
                return False
            raise

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        self._gogi.llm_session.save_memory(SaveLLMSessionMemoryRequest(user_id=user, key=key, value=value))

    def get_memories(self, user: str) -> dict[str, Any]:
        return dict(self._gogi.llm_session.get_memory(GetLLMSessionMemoryRequest(user_id=user)).memories)

    def delete_memory(self, user: str, key: str) -> bool:
        response = self._gogi.llm_session.delete_memory(DeleteLLMSessionMemoryRequest(user_id=user, key=key))
        return response.count > 0
