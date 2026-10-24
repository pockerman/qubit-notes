import re
import uuid
from typing import Any

from qubit_notes.platform.port import (
    Chunk,
    DocumentInfo,
    DownloadedFile,
    IndexInfo,
    IngestJob,
    IngestStatus,
    MemberRole,
    Message,
    PlatformHealth,
    Section,
    SectionText,
)
from qubit_notes.platform.standalone import parsing
from tests.fakes.fake_ai import FakeAI

SERVICES = ("gateway", "documents", "indexes", "llms", "prompts", "llm-sessions", "llm-tools", "guardrails")


class FakePlatform:
    """In-memory ``StudyPlatform`` for fast scenarios that need no gogi stack or API keys.

    Ingestion completes at once, unless ``hold_ingestion`` is set, and search ranks a document's text by how many
    query words it contains. Documents are divided into sections the way gogi divides them: a Markdown file by its
    headings, a PDF by its outline or pages, and a plain text file into a single section, as the app's own platform
    divides them (``platform/standalone/parsing.py``).
    """

    def __init__(self):
        self.reachable = True
        self.down: set[str] = set()
        # whether the platform takes the app's key
        self.takes_key = True
        # the app's credentials, name to value
        self.credentials: dict[str, str] = {}
        # the model providers whose keys the platform needs, and the keys it has, provider to key
        self.needs_keys: set[str] = set()
        self.keys: dict[str, str] = {}
        # the provider and model the AI answers with, once the app says
        self.ai_model: tuple[str, str] | None = None
        self.indexes: dict[str, IndexInfo] = {}
        # index name to document id to (document, text)
        self.documents: dict[str, dict[str, tuple[DocumentInfo, str]]] = {}
        self.jobs: dict[str, IngestJob] = {}
        self.memories: dict[str, dict[str, Any]] = {}
        # document id to (its uploaded file, its sections with their own text)
        self.files: dict[str, tuple[bytes, list[SectionText]]] = {}
        # new ingestions stay pending while set
        self.hold_ingestion = False
        self.ai = FakeAI()
        # conversation id to (its user, its messages)
        self.conversations: dict[str, tuple[str, list[Message]]] = {}

    def health(self) -> PlatformHealth:
        if not self.reachable:
            return PlatformHealth(reachable=False, error="UNAVAILABLE: connection refused")
        services = {name: "NOT_SERVING" if name in self.down else "SERVING" for name in SERVICES}
        missing_keys = sorted(self.needs_keys - set(self.keys))
        if missing_keys:
            # as the app's own platform reports its AI without its key
            services["ai"] = "NOT_SERVING"
        return PlatformHealth(
            reachable=True,
            services=services,
            authenticated=self.takes_key,
            error=None if self.takes_key else "gogi does not take the app's key: UNAUTHENTICATED",
            missing_keys=missing_keys,
        )

    def store_credential(self, name: str, value: str) -> None:
        self.credentials[name] = value

    def list_credentials(self) -> list[str]:
        return sorted(self.credentials)

    # the app keeps its keys, as it does on its own platform
    keeps_keys = False

    def use_key(self, provider: str, key: str) -> None:
        self.keys[provider] = key

    def use_model(self, provider: str, model: str) -> None:
        # the fake's AI needs no key for the provider it started with, as the scenarios give none; another provider
        # it is changed to needs its key, as the app's own platform's does
        if self.ai_model and provider != self.ai_model[0]:
            self.needs_keys = (self.needs_keys - {self.ai_model[0]}) | {provider}
        self.ai_model = (provider, model)

    def has_key(self, provider: str) -> bool:
        return provider in self.keys

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
        self,
        index_name: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
        store_only: bool = False,
    ) -> IngestJob:
        document_id = uuid.uuid4().hex
        status = IngestStatus.PENDING if self.hold_ingestion and not store_only else IngestStatus.COMPLETED
        document = DocumentInfo(
            document_id=document_id,
            index_name=index_name,
            filename=filename,
            metadata=metadata,
            status=status,
            content_type=content_type,
            size_bytes=len(content),
        )
        sections = [] if store_only else parsing.sections(filename, content)
        text = "\n\n".join(part.content for part in sections)
        self.documents[index_name][document_id] = (document, text)
        self.files[document_id] = (content, sections)
        job = IngestJob(job_id=uuid.uuid4().hex, document_id=document_id, status=status)
        document.version = job.job_id
        self.jobs[job.job_id] = job
        return job

    def replace_document(
        self,
        index_name: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> IngestJob:
        document, _ = self.documents[index_name][document_id]
        sections = parsing.sections(filename, content)
        self.documents[index_name][document_id] = (document, "\n\n".join(part.content for part in sections))
        self.files[document_id] = (content, sections)
        job = IngestJob(job_id=uuid.uuid4().hex, document_id=document_id, status=IngestStatus.COMPLETED)
        document.version, document.size_bytes, document.metadata = job.job_id, len(content), metadata
        document.filename, document.content_type, document.status = filename, content_type, IngestStatus.COMPLETED
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

    def get_document(self, index_name: str, document_id: str) -> DocumentInfo | None:
        found = self.documents.get(index_name, {}).get(document_id)
        return found[0] if found else None

    def delete_document(self, index_name: str, document_id: str) -> bool:
        self.files.pop(document_id, None)
        return self.documents.get(index_name, {}).pop(document_id, None) is not None

    # reading

    def _ready_sections(self, index_name: str, document_id: str) -> list[SectionText]:
        document = self.get_document(index_name, document_id)
        if document is None or document.status != IngestStatus.COMPLETED:
            return []
        return self.files[document_id][1]

    def list_sections(self, index_name: str, document_id: str) -> list[Section]:
        return [part.section for part in self._ready_sections(index_name, document_id)]

    def read_section(self, index_name: str, document_id: str, position: int) -> list[SectionText] | None:
        sections = self._ready_sections(index_name, document_id)
        start = next((i for i, part in enumerate(sections) if part.section.position == position), None)
        if start is None:
            return None
        level = sections[start].section.level
        end = next((i for i in range(start + 1, len(sections)) if sections[i].section.level <= level), len(sections))
        return sections[start:end]

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile | None:
        document = self.get_document(index_name, document_id)
        if document is None:
            return None
        content = self.files[document_id][0]
        part = content[offset : offset + length] if length else content[offset:]
        return DownloadedFile(
            filename=document.filename, content_type=document.content_type, content=part, size=len(content)
        )

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]:
        """a chunk per section, as gogi never lets a chunk span two sections, carrying the section in its metadata"""
        words = set(re.findall(r"\w+", query.lower()))
        hits = []
        for document, _ in self.documents.get(index_name, {}).values():
            if not _matches(document.metadata, metadata_filter):
                continue
            for part in self._ready_sections(index_name, document.document_id):
                # whole words, so "a" doesn't match every text
                score = len(words & set(re.findall(r"\w+", part.content.lower())))
                if score:
                    hits.append(
                        Chunk(
                            chunk_id=f"{document.document_id}-{part.section.position}",
                            document_id=document.document_id,
                            content=part.content,
                            score=float(score),
                            metadata={
                                **document.metadata,
                                "section": str(part.section.position),
                                "section_title": part.section.title,
                            },
                        )
                    )
        return sorted(hits, key=lambda chunk: -chunk.score)[:top_k]

    # the AI

    @property
    def completions(self) -> list[str]:
        return self.ai.completions

    @property
    def histories(self) -> list[list[Message]]:
        return self.ai.histories

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
        self.conversations.setdefault(conversation_id, (user, []))

    def add_to_conversation(self, conversation_id: str, messages: list[Message]) -> None:
        self.conversations[conversation_id][1].extend(messages)

    def conversation_context(self, conversation_id: str) -> list[Message]:
        return list(self.conversations.get(conversation_id, ("", []))[1])

    def end_conversation(self, conversation_id: str) -> bool:
        return self.conversations.pop(conversation_id, None) is not None

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        self.memories.setdefault(user, {})[key] = value

    def get_memories(self, user: str) -> dict[str, Any]:
        return dict(self.memories.get(user, {}))

    def delete_memory(self, user: str, key: str) -> bool:
        return self.memories.get(user, {}).pop(key, None) is not None


def _matches(metadata: dict[str, str], metadata_filter: dict[str, str] | None) -> bool:
    return all(metadata.get(key) == value for key, value in (metadata_filter or {}).items())
