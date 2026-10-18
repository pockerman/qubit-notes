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
    Message,
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
        # what the AI was asked, so scenarios can tell whether something new was written, and the conversation it
        # was given with each prompt
        self.completions: list[str] = []
        self.histories: list[list[Message]] = []
        # conversation id to (its user, its messages)
        self.conversations: dict[str, tuple[str, list[Message]]] = {}

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
        sections = _sections(filename, content)
        self.documents[index_name][document_id] = (document, "\n\n".join(part.content for part in sections))
        self.files[document_id] = (content, sections)
        job = IngestJob(job_id=uuid.uuid4().hex, document_id=document_id, status=IngestStatus.COMPLETED)
        document.version, document.size_bytes, document.metadata = job.job_id, len(content), metadata
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

    def complete(
        self,
        system: str,
        prompt: str,
        json_schema: dict[str, Any] | None = None,
        history: list[Message] | None = None,
    ) -> str:
        """A deterministic stand-in: each answer is numbered, so no two are alike. A quiz has the questions the
        prompt asks for, each from one of the sections the prompt gives, in turn, with the first choice correct.
        The assistant understands a request by its words (see ``_understand``)."""
        self.completions.append(prompt)
        self.histories.append(list(history or []))
        number = len(self.completions)
        if json_schema is None:
            titles = re.findall(r"^## (.+)$", prompt, re.MULTILINE)
            return f"Summary {number} of {', '.join(titles) or 'the summaries'}."
        if "request" in json_schema.get("properties", {}):
            return json.dumps(_understand(prompt, number))
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


# words too common to tell whether a passage answers a question
COMMON = {
    "what",
    "which",
    "does",
    "that",
    "this",
    "with",
    "from",
    "into",
    "about",
    "have",
    "there",
    "their",
    "when",
    "where",
    "whom",
    "whose",
    "they",
    "them",
    "then",
    "than",
    "your",
    "mine",
}


def _content_words(text: str) -> set[str]:
    return {word for word in re.findall(r"\w+", text.lower()) if len(word) > 3 and word not in COMMON}


def _understand(prompt: str, number: int) -> dict:
    """The fake assistant's reading of the student's words, the last part of the prompt: "quiz" asks for a quiz,
    "summar..." for a summary, of the "topic", the "document" or else the section, "new" for a new one, "N questions"
    for its size. Anything else is a question, answered from the passages that share a word with it."""
    words = prompt.rsplit("The student says:", 1)[-1].strip()
    lowered = words.lower()
    request = "quiz" if "quiz" in lowered else "summary" if "summar" in lowered else "question"
    of = "topic" if "topic" in lowered else "document" if "document" in lowered else "section"
    count = re.search(r"(\d+) questions", lowered)
    cited = []
    if request == "question":
        passages = re.findall(
            r"^\[(P\d+)\] [^\n]+\n(.*?)(?=^\[P\d+\] |^The student says:)", prompt, re.MULTILINE | re.DOTALL
        )
        cited = [reference for reference, text in passages if _content_words(words) & _content_words(text)]
    return {
        "request": request,
        "of": of,
        "new": bool(re.search(r"\bnew\b", lowered)),
        "questions": int(count.group(1)) if count else 0,
        "answer": f"Answer {number}, from {', '.join(cited)}." if cited else "Your material does not cover this.",
        "covered": bool(cited) or request != "question",
        "cited": cited,
    }


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
