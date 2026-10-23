"""Markdown under another name, e.g. a PDF converted to Markdown, which keeps the name it was uploaded with.

Platforms choose how to read a document by its name's extension, so Markdown is given to them as "<name>.md", with
its name in its metadata; the app is shown it by its name again. Everything else passes through.
"""

from typing import Any

from qubit_notes.platform.port import Chunk, DocumentInfo, DownloadedFile, IngestJob, StudyPlatform

# the metadata of a document the platform keeps under another name: its name
NAME = "name"
MARKDOWN = "text/markdown"


def _stored(filename: str, content_type: str, metadata: dict[str, str]) -> tuple[str, dict[str, str]]:
    if content_type == MARKDOWN and not filename.lower().endswith(".md"):
        return f"{filename}.md", {**metadata, NAME: filename}
    return filename, {key: value for key, value in metadata.items() if key != NAME}


def _shown(document: DocumentInfo | None) -> DocumentInfo | None:
    if document is None or NAME not in document.metadata:
        return document
    return document.model_copy(update={"filename": document.metadata[NAME]})


class NamedDocuments:
    """``StudyPlatform`` that keeps Markdown with another name under a name ending in .md"""

    def __init__(self, platform: StudyPlatform):
        self._platform = platform

    def __getattr__(self, name: str) -> Any:
        return getattr(self._platform, name)

    def ingest_document(
        self,
        index_name: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
        store_only: bool = False,
    ) -> IngestJob:
        filename, metadata = _stored(filename, content_type, metadata)
        return self._platform.ingest_document(index_name, filename, content, content_type, metadata, store_only)

    def replace_document(
        self,
        index_name: str,
        document_id: str,
        filename: str,
        content: bytes,
        content_type: str,
        metadata: dict[str, str],
    ) -> IngestJob:
        filename, metadata = _stored(filename, content_type, metadata)
        return self._platform.replace_document(index_name, document_id, filename, content, content_type, metadata)

    def get_document(self, index_name: str, document_id: str) -> DocumentInfo | None:
        return _shown(self._platform.get_document(index_name, document_id))

    def list_documents(self, index_name: str, metadata_filter: dict[str, str] | None = None) -> list[DocumentInfo]:
        return [_shown(document) for document in self._platform.list_documents(index_name, metadata_filter)]

    def download_document(
        self, index_name: str, document_id: str, offset: int = 0, length: int = 0
    ) -> DownloadedFile | None:
        downloaded = self._platform.download_document(index_name, document_id, offset, length)
        document = self.get_document(index_name, document_id) if downloaded is not None else None
        if document is not None and NAME in document.metadata:
            return downloaded.model_copy(update={"filename": document.filename})
        return downloaded

    def search(
        self, index_name: str, query: str, top_k: int, metadata_filter: dict[str, str] | None = None
    ) -> list[Chunk]:
        return [
            chunk.model_copy(update={"metadata": {**chunk.metadata, "filename": chunk.metadata[NAME]}})
            if NAME in chunk.metadata
            else chunk
            for chunk in self._platform.search(index_name, query, top_k, metadata_filter)
        ]
