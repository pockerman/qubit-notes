import json
import re
import uuid
from io import BytesIO
from typing import Any

from pypdf import PdfReader

from study_assistant.platform.port import (
    Chunk,
    DocumentInfo,
    DownloadedFile,
    IndexInfo,
    IngestJob,
    IngestStatus,
    MemberRole,
    PlatformHealth,
    Section,
    SectionText,
)

SERVICES = ("gateway", "documents", "indexes", "llms", "prompts", "llm-sessions", "llm-tools", "guardrails")


class FakePlatform:
    """In-memory ``StudyPlatform`` for fast scenarios that need no gogi stack or API keys.

    Ingestion completes at once, unless ``hold_ingestion`` is set, and search ranks a document's text by how many
    query words it contains. Documents are divided into sections the way gogi divides them: a Markdown file by its
    headings, a PDF by its pages (the fake ignores outlines), and a plain text file into a single section.
    """

    def __init__(self):
        self.reachable = True
        self.down: set[str] = set()
        self.indexes: dict[str, IndexInfo] = {}
        # index name to document id to (document, text)
        self.documents: dict[str, dict[str, tuple[DocumentInfo, str]]] = {}
        self.jobs: dict[str, IngestJob] = {}
        self.memories: dict[str, dict[str, Any]] = {}
        # document id to (its uploaded file, its sections with their own text)
        self.files: dict[str, tuple[bytes, list[SectionText]]] = {}
        # new ingestions stay pending while set
        self.hold_ingestion = False
        # what the AI was asked, so scenarios can tell whether something new was written
        self.completions: list[str] = []

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
        sections = [] if store_only else _sections(filename, content)
        text = "\n\n".join(part.content for part in sections)
        self.documents[index_name][document_id] = (document, text)
        self.files[document_id] = (content, sections)
        job = IngestJob(job_id=uuid.uuid4().hex, document_id=document_id, status=status)
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

    # the AI

    def complete(self, system: str, prompt: str, json_schema: dict[str, Any] | None = None) -> str:
        """A deterministic stand-in: each answer is numbered, so no two are alike. A quiz has the questions the
        prompt asks for, each from one of the sections the prompt gives, in turn, with the first choice correct."""
        self.completions.append(prompt)
        number = len(self.completions)
        if json_schema is None:
            titles = re.findall(r"^## (.+)$", prompt, re.MULTILINE)
            return f"Summary {number} of {', '.join(titles) or 'the summaries'}."
        count = int(re.search(r"quiz of (\d+) questions", prompt).group(1))
        references = re.findall(r"^\[(S\d+)\] (.+)$", prompt, re.MULTILINE)
        questions = [
            {
                "question": f"Question {i + 1} of quiz {number}, on {references[i % len(references)][1]}?",
                "choices": ["right", "wrong", "also wrong", "still wrong"],
                "answer": 0,
                "source": references[i % len(references)][0],
            }
            for i in range(count)
        ]
        return json.dumps({"questions": questions})

    # memories

    def save_memory(self, user: str, key: str, value: dict[str, Any]) -> None:
        self.memories.setdefault(user, {})[key] = value

    def get_memories(self, user: str) -> dict[str, Any]:
        return dict(self.memories.get(user, {}))

    def delete_memory(self, user: str, key: str) -> bool:
        return self.memories.get(user, {}).pop(key, None) is not None


def _matches(metadata: dict[str, str], metadata_filter: dict[str, str] | None) -> bool:
    return all(metadata.get(key) == value for key, value in (metadata_filter or {}).items())


HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


def _sections(filename: str, content: bytes) -> list[SectionText]:
    def section(position: int, title: str, level: int, text: str, page: int | None = None) -> SectionText:
        return SectionText(
            section=Section(position=position, title=title, level=level, page_start=page, page_end=page),
            content=text.strip(),
        )

    if content.startswith(b"%PDF-"):
        try:
            pages = [(page.extract_text() or "") for page in PdfReader(BytesIO(content)).pages]
        except Exception:
            return []
        return [section(n, f"Page {n}", 1, text, n) for n, text in enumerate(pages, start=1)]

    text = content.decode(errors="ignore")
    if not filename.lower().endswith(".md"):
        return [section(1, "", 1, text)] if text.strip() else []

    sections, title, level, lines = [], None, 1, []
    for line in text.splitlines() + ["# end"]:
        match = HEADING.match(line)
        if not match:
            lines.append(line)
            continue
        if title is not None or "".join(lines).strip():
            sections.append(section(len(sections) + 1, title or "", level, "\n".join(lines)))
        title, level, lines = match.group(2), len(match.group(1)), []
    return sections
