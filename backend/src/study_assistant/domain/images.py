"""The images of Markdown material. An image is kept in gogi beside its material, as a file that is stored but not
processed, like a video; its metadata says which material it belongs to and the path the material refers to it by."""

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from pydantic import BaseModel

from study_assistant.domain.courses import Courses
from study_assistant.domain.errors import InvalidRequest, NotFound, TooLarge
from study_assistant.platform.port import DocumentInfo, StudyPlatform

MB = 1024 * 1024
MAX_IMAGE_MB = 10
IMAGE_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

# metadata of an image's document
KIND = "kind"
IMAGE = "image"
MATERIAL = "material"
PATH = "path"

# ![alt](path) or ![alt](path "title"), the path optionally in <…>
REFERENCE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")


class MaterialImages(BaseModel):
    """The images a material refers to: those it has, and those still to be added."""

    images: list[str]
    missing: list[str]


@dataclass(frozen=True)
class Image:
    filename: str
    content_type: str
    content: bytes


def is_image(document: DocumentInfo) -> bool:
    return document.metadata.get(KIND) == IMAGE


def references(text: str) -> list[str]:
    """the paths of the images the Markdown refers to, in order and once each; images on the web are not kept"""
    paths: list[str] = []
    for match in REFERENCE.finditer(text):
        path = _normal(match.group(1))
        if not re.match(r"^[a-z][a-z0-9+.-]*:", path, re.IGNORECASE) and path not in paths:
            paths.append(path)
    return paths


def _normal(path: str) -> str:
    return str(PurePosixPath(path.strip().removeprefix("./")))


def image_type(filename: str, content: bytes) -> str:
    """the image's content type, checked against what the bytes are"""
    content_type = IMAGE_TYPES.get(PurePosixPath(filename).suffix.lower())
    signatures = {
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/gif": content[:6] in (b"GIF87a", b"GIF89a"),
        "image/webp": content[:4] == b"RIFF" and content[8:12] == b"WEBP",
    }
    if content_type is None:
        raise InvalidRequest(f"{filename!r} is not an image: add PNG, JPEG, GIF or WebP images")
    if not signatures[content_type]:
        raise InvalidRequest(f"{filename!r} is not a {content_type.removeprefix('image/').upper()} image")
    return content_type


class Images:
    def __init__(self, platform: StudyPlatform, courses: Courses):
        self._platform = platform
        self._courses = courses

    def of(self, student: str, course_id: str, document_id: str) -> MaterialImages:
        course = self._courses.get_by_id(student, course_id)
        text = self._markdown(course.id, document_id)
        kept = {d.metadata[PATH] for d in self._documents(course.id, document_id)}
        referred = references(text)
        return MaterialImages(images=[p for p in referred if p in kept], missing=[p for p in referred if p not in kept])

    def add(
        self, student: str, course_id: str, document_id: str, filename: str, content: bytes, path: str | None = None
    ) -> MaterialImages:
        """keeps the image under the path the material refers to it by: ``path``, or the one ending in its file
        name. An image already kept under that path is replaced."""
        course = self._courses.get_by_id(student, course_id)
        self._courses.require_owner(student, course)
        material = self._material(course.id, document_id)
        content_type = image_type(filename, content)
        if len(content) > MAX_IMAGE_MB * MB:
            raise TooLarge(f"{filename!r} is {len(content) / MB:.1f} MB; images are up to {MAX_IMAGE_MB} MB")

        referred = references(self._markdown(course.id, document_id))
        if path is not None:
            target = _normal(path)
            if target not in referred:
                raise InvalidRequest(f"{material.filename!r} does not refer to {PurePosixPath(target).name!r}")
        else:
            named = [p for p in referred if PurePosixPath(p).name == PurePosixPath(filename).name]
            if not named:
                raise InvalidRequest(f"{material.filename!r} does not refer to {PurePosixPath(filename).name!r}")
            if len(named) > 1:
                raise InvalidRequest(
                    f"{material.filename!r} has several images called {filename!r}: {', '.join(named)}"
                )
            target = named[0]

        for kept in self._documents(course.id, document_id, target):
            self._platform.delete_document(course.id, kept.document_id)
        metadata = {KIND: IMAGE, MATERIAL: document_id, PATH: target, "uploaded_by": student}
        self._platform.ingest_document(
            course.id, PurePosixPath(target).name, content, content_type, metadata=metadata, store_only=True
        )
        return self.of(student, course_id, document_id)

    def get(self, student: str, course_id: str, document_id: str, path: str) -> Image:
        course = self._courses.get_by_id(student, course_id)
        kept = self._documents(course.id, document_id, _normal(path))
        downloaded = self._platform.download_document(course.id, kept[0].document_id) if kept else None
        if downloaded is None:
            raise NotFound(f"no image {path!r}")
        return Image(filename=downloaded.filename, content_type=downloaded.content_type, content=downloaded.content)

    def forget(self, course_id: str, document_id: str) -> None:
        """deletes the images of a deleted material"""
        for image in self._documents(course_id, document_id):
            self._platform.delete_document(course_id, image.document_id)

    def _documents(self, index: str, document_id: str, path: str | None = None) -> list[DocumentInfo]:
        metadata = {KIND: IMAGE, MATERIAL: document_id, **({PATH: path} if path else {})}
        return self._platform.list_documents(index, metadata)

    def _material(self, index: str, document_id: str) -> DocumentInfo:
        material = self._platform.get_document(index, document_id)
        if material is None or is_image(material):
            raise NotFound(f"no material {document_id!r}")
        if material.content_type != "text/markdown":
            raise InvalidRequest("only Markdown material has images of its own; a PDF's images are part of it")
        return material

    def _markdown(self, index: str, document_id: str) -> str:
        self._material(index, document_id)
        downloaded = self._platform.download_document(index, document_id)
        if downloaded is None:
            raise NotFound(f"no material {document_id!r}")
        return downloaded.content.decode("utf-8", errors="replace")
