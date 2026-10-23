"""PDF and EPUB material as Markdown (features/converting.feature).

An uploaded PDF or EPUB is kept twice by the platform: as the material, at first the file as it is, stored but not
processed, and as its original, beside it. In the background, the original is converted to Markdown, its pictures are
kept as the material's images, and the material is given the Markdown as its content, which the platform then
processes like any Markdown's. Its metadata says what it was converted from and which document is its original.

A conversion is a job of the app's own, with an id of its own, which the student follows as they follow an upload:
once the Markdown is the material's, the job is the platform's processing of it. Conversions left unfinished when the
app stopped are done when it starts again.
"""

import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import delete, insert, select, update
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.conversion import CONVERTIBLE, NotConvertible, export, to_markdown
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound
from qubit_notes.domain.images import KIND, MATERIAL, Images
from qubit_notes.domain.reference_text import as_text
from qubit_notes.platform.port import DocumentInfo, DownloadedFile, IngestJob, IngestStatus, StudyPlatform

# metadata of a material converted from a PDF or an EPUB: the content type it was converted from, and its original's
# document; of one being converted, its conversion
CONVERTED_FROM = "converted_from"
ORIGINAL = "original"
CONVERTING = "converting"
# metadata of an original's document
ORIGINAL_KIND = "original"
JOB_PREFIX = "conversion-"

table = storage.conversions


def is_original(document: DocumentInfo) -> bool:
    return document.metadata.get(KIND) == ORIGINAL_KIND


def converted_from(document: DocumentInfo) -> str | None:
    """ "pdf" or "epub" for a material converted from one"""
    content_type = document.metadata.get(CONVERTED_FROM) or (
        document.content_type if document.metadata.get(CONVERTING) else None
    )
    return {"application/pdf": "pdf", "application/epub+zip": "epub"}.get(content_type or "")


class Conversions:
    def __init__(self, database: Engine, platform: StudyPlatform, courses: Courses, images: Images, workers: int = 2):
        self._engine = database
        self._platform = platform
        self._courses = courses
        self._images = images
        # inline where the database is in memory, as in tests: its one connection can't be shared by threads
        in_memory = database.dialect.name == "sqlite" and database.url.database in (None, "", ":memory:")
        self._executor = None if in_memory else ThreadPoolExecutor(workers, thread_name_prefix="conversion")

    @staticmethod
    def convertible(content_type: str) -> bool:
        return content_type in CONVERTIBLE

    def start(
        self, course_id: str, filename: str, content: bytes, content_type: str, metadata: dict[str, str]
    ) -> IngestJob:
        """keeps the file as the material and as its original, and converts it in the background"""
        job_id = f"{JOB_PREFIX}{uuid.uuid4().hex}"
        material = self._platform.ingest_document(
            course_id, filename, content, content_type, metadata={**metadata, CONVERTING: job_id}, store_only=True
        )
        original = self._platform.ingest_document(
            course_id,
            filename,
            content,
            content_type,
            metadata={KIND: ORIGINAL_KIND, MATERIAL: material.document_id},
            store_only=True,
        )
        now = datetime.now(UTC)
        with self._engine.begin() as connection:
            connection.execute(
                insert(table).values(
                    id=job_id,
                    course_id=course_id,
                    document_id=material.document_id,
                    original_id=original.document_id,
                    status=IngestStatus.PENDING.value,
                    created_at=now,
                    updated_at=now,
                )
            )
        self._submit(job_id)
        return IngestJob(job_id=job_id, document_id=material.document_id, status=IngestStatus.PENDING)

    def resume(self) -> None:
        with self._engine.connect() as connection:
            unfinished = (
                connection.execute(
                    select(table.c.id).where(
                        table.c.status.in_([IngestStatus.PENDING.value, IngestStatus.RUNNING.value])
                    )
                )
                .scalars()
                .all()
            )
        for job_id in unfinished:
            self._submit(job_id)

    def stop(self) -> None:
        if self._executor is not None:
            self._executor.shutdown(wait=True, cancel_futures=True)

    def _submit(self, job_id: str) -> None:
        if self._executor is None:
            self._convert(job_id)
        else:
            self._executor.submit(self._convert, job_id)

    def _set(self, job_id: str, **values) -> None:
        with self._engine.begin() as connection:
            connection.execute(update(table).where(table.c.id == job_id).values(updated_at=datetime.now(UTC), **values))

    def _convert(self, job_id: str) -> None:
        with self._engine.connect() as connection:
            row = connection.execute(select(table).where(table.c.id == job_id)).first()
        if row is None:
            return
        try:
            self._set(job_id, status=IngestStatus.RUNNING.value)
            material = self._platform.get_document(row.course_id, row.document_id)
            original = self._platform.download_document(row.course_id, row.original_id)
            if material is None or original is None:
                # the material was deleted meanwhile
                self._set(job_id, status=IngestStatus.FAILED.value, error="the material was deleted")
                return
            converted = to_markdown(material.filename, material.content_type, original.content)
            for path, content in converted.images.items():
                self._images.keep(row.course_id, row.document_id, path, content)
            metadata = {key: value for key, value in material.metadata.items() if key != CONVERTING}
            job = self._platform.replace_document(
                row.course_id,
                row.document_id,
                material.filename,
                converted.markdown.encode(),
                "text/markdown",
                metadata={**metadata, CONVERTED_FROM: material.content_type, ORIGINAL: row.original_id},
            )
            self._set(job_id, status=IngestStatus.COMPLETED.value, ingest_job_id=job.job_id)
        except NotConvertible as e:
            self._set(job_id, status=IngestStatus.FAILED.value, error=str(e))
        except Exception as e:
            logger.exception(f"the conversion {job_id} failed")
            self._set(job_id, status=IngestStatus.FAILED.value, error=f"the conversion failed: {e}")

    def _row(self, job_id: str):
        with self._engine.connect() as connection:
            return connection.execute(select(table).where(table.c.id == job_id)).first()

    def job(self, job_id: str) -> IngestJob | None:
        """the conversion as an upload's job: once converted, it is the platform's processing of the Markdown"""
        row = self._row(job_id)
        if row is None:
            return None
        if row.status == IngestStatus.COMPLETED.value and row.ingest_job_id:
            ingestion = self._platform.get_ingest_job(row.ingest_job_id)
            if ingestion is not None:
                return ingestion.model_copy(update={"job_id": job_id, "document_id": row.document_id})
        status = IngestStatus.RUNNING if row.status == IngestStatus.COMPLETED.value else IngestStatus(row.status)
        return IngestJob(job_id=job_id, document_id=row.document_id, status=status, error=row.error)

    def as_it_is(self, document: DocumentInfo) -> DocumentInfo:
        """the document with the status of its conversion, while it's being converted or failed to be"""
        job_id = document.metadata.get(CONVERTING)
        if not job_id:
            return document
        row = self._row(job_id)
        status = IngestStatus(row.status) if row else IngestStatus.FAILED
        if status == IngestStatus.COMPLETED:
            status = IngestStatus.RUNNING
        return document.model_copy(update={"status": status})

    def error(self, document: DocumentInfo) -> str | None:
        job_id = document.metadata.get(CONVERTING)
        row = self._row(job_id) if job_id else None
        return row.error if row else None

    def original(self, course_id: str, document: DocumentInfo) -> DocumentInfo:
        """the document whose file is the material's original: its original's, if it was converted"""
        original_id = document.metadata.get(ORIGINAL)
        found = self._platform.get_document(course_id, original_id) if original_id else None
        return found or document

    def export(self, student: str, course_id: str, document_id: str) -> DownloadedFile:
        """the converted material as it is now, as a PDF or an EPUB like its original"""
        course = self._courses.get_by_id(student, course_id)
        document = self._platform.get_document(course.id, document_id)
        if document is None or is_original(document):
            raise NotFound(f"no material {document_id!r} in {course.name!r}")
        content_type = document.metadata.get(CONVERTED_FROM)
        if not content_type:
            raise InvalidRequest(f"{document.filename!r} was not converted from a PDF or an EPUB")
        downloaded = self._platform.download_document(course.id, document_id)
        if downloaded is None:
            raise NotFound(f"no material {document_id!r}")
        # a reference to another part of the course is its label, as text: the file isn't in the course
        markdown = as_text(downloaded.content.decode("utf-8", errors="replace"))
        images = self._images.contents(course.id, document_id)
        content = export(content_type, document.filename.rsplit(".", 1)[0], markdown, images)
        return DownloadedFile(filename=document.filename, content_type=content_type, content=content, size=len(content))

    def forget(self, course_id: str, document_id: str) -> None:
        """deletes a deleted material's original and conversion"""
        for original in self._platform.list_documents(course_id, {KIND: ORIGINAL_KIND, MATERIAL: document_id}):
            self._platform.delete_document(course_id, original.document_id)
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.document_id == document_id))
