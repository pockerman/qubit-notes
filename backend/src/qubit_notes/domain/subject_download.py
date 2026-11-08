"""A subject as a zip: its material, topic by topic in the order it is read, and the student's flashcards of it
(features/subject_download.feature).

The zip is written to a temporary file, not kept in memory, as a subject may have videos; whoever asked for it deletes
the file once it is sent.
"""

import csv
import io
import re
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

from qubit_notes.domain.conversions import Conversions
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import NotFound
from qubit_notes.domain.images import Images
from qubit_notes.domain.materials import Material, Materials
from qubit_notes.domain.reviews import ReviewCard, Reviews
from qubit_notes.domain.topics import Topics
from qubit_notes.platform.port import StudyPlatform

# what can't be in the name of a file or a folder, on any system the zip is opened on
_UNSAFE = re.compile(r'[\x00-\x1f<>:"/\\|?*]+')


@dataclass
class SubjectZip:
    filename: str
    # the temporary file it was written to
    path: Path


def _safe(name: str, otherwise: str) -> str:
    """a name for a file or a folder: what can't be in one replaced, and not hidden"""
    cleaned = _UNSAFE.sub(" ", name).strip(" .")
    return cleaned or otherwise


class _Folder:
    """the names in a folder of the zip, each once"""

    def __init__(self, path: str):
        self.path = path
        self._taken: set[str] = set()

    def name(self, wanted: str) -> str:
        stem, suffix = PurePosixPath(wanted).stem, PurePosixPath(wanted).suffix
        name, n = wanted, 1
        while name.lower() in self._taken:
            n += 1
            name = f"{stem} ({n}){suffix}"
        self._taken.add(name.lower())
        return f"{self.path}/{name}" if self.path else name


class SubjectDownload:
    def __init__(
        self,
        platform: StudyPlatform,
        courses: Courses,
        topics: Topics,
        materials: Materials,
        conversions: Conversions,
        images: Images,
        reviews: Reviews,
    ):
        self._platform = platform
        self._courses = courses
        self._topics = topics
        self._materials = materials
        self._conversions = conversions
        self._images = images
        self._reviews = reviews

    def zip(self, student: str, course_name: str, subject: str) -> SubjectZip:
        course = self._courses.get(student, course_name)
        found = next((s for s in self._topics.subjects_of(course) if s.subject == subject), None)
        if found is None:
            raise NotFound(f"no subject {subject!r} in {course_name!r}")
        topics = [t for t in self._topics.of_course(course) if t.subject == subject]
        materials = self._materials.list_of(course, subject)
        names = {t.topic: t.name or t.topic for t in topics}
        cards = [card for card in self._reviews.cards(student, course.id) if card.subject == subject]

        file = tempfile.NamedTemporaryFile(prefix="qubit-notes-", suffix=".zip", delete=False)
        file.close()
        path = Path(file.name)
        try:
            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                root = _Folder("")
                missing: list[str] = []
                contents: list[tuple[str, list[str]]] = []
                for number, topic in enumerate(topics, start=1):
                    folder = _Folder(root.name(f"{number} {_safe(names[topic.topic], topic.topic)}"))
                    of_topic = [m for m in materials if m.topic == topic.topic]
                    written = []
                    for material in of_topic:
                        if self._write_material(archive, course.id, folder, material):
                            written.append(material.filename)
                        else:
                            missing.append(material.filename)
                    contents.append((folder.path, written))
                archive.writestr(root.name("flashcards.csv"), _csv(cards, materials, names))
                archive.writestr(root.name("flashcards.md"), _markdown(found.name, cards, materials, names))
                archive.writestr(root.name("README.md"), _readme(found.name, course.name, contents, cards, missing))
        except BaseException:
            path.unlink(missing_ok=True)
            raise
        return SubjectZip(filename=f"{_safe(found.name, subject)}.zip", path=path)

    def _write_material(self, archive: zipfile.ZipFile, course_id: str, folder: _Folder, material: Material) -> bool:
        """the material as it is now, with its images or its original beside it; False if it has no file"""
        downloaded = self._platform.download_document(course_id, material.document_id)
        if downloaded is None:
            return False
        images = self._images.contents(course_id, material.document_id) if material.kind == "text" else {}
        filename = _safe(material.filename, material.document_id)
        # a material converted from a PDF or an EPUB keeps its original's name, but is Markdown now
        if downloaded.content_type == "text/markdown" and PurePosixPath(filename).suffix.lower() != ".md":
            filename = f"{PurePosixPath(filename).stem}.md"
        # with images, in a folder of its own, so they are where it refers to them and no other material's are
        beside = _Folder(folder.name(PurePosixPath(filename).stem)) if images else folder
        archive.writestr(beside.name(filename), downloaded.content)
        for image_path, content in images.items():
            parts = [_safe(part, "image") for part in PurePosixPath(image_path).parts if part not in ("", ".", "..")]
            if parts:
                archive.writestr(f"{beside.path}/{'/'.join(parts)}", content)
        document = self._platform.get_document(course_id, material.document_id)
        original = self._conversions.original(course_id, document) if document else None
        if original is not None and original.document_id != material.document_id:
            kept = self._platform.download_document(course_id, original.document_id)
            if kept is not None:
                archive.writestr(beside.name(_safe(kept.filename, "original")), kept.content)
        return True


def _in_order(cards: list[ReviewCard], materials: list[Material]) -> list[ReviewCard]:
    """the cards in the order their material and section are read"""
    order = {m.document_id: i for i, m in enumerate(materials)}
    return sorted(cards, key=lambda c: (order.get(c.source.document_id, len(order)), c.source.section))


def _topic_of(card: ReviewCard, materials: list[Material], names: dict[str, str]) -> str:
    topic = next((m.topic for m in materials if m.document_id == card.source.document_id), "")
    return names.get(topic, topic)


def _csv(cards: list[ReviewCard], materials: list[Material], names: dict[str, str]) -> str:
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["front", "back", "topic", "material", "section"])
    for card in _in_order(cards, materials):
        writer.writerow(
            [card.front, card.back, _topic_of(card, materials, names), card.source.filename, card.source.title]
        )
    return out.getvalue()


def _markdown(subject: str, cards: list[ReviewCard], materials: list[Material], names: dict[str, str]) -> str:
    lines = [f"# Flashcards of {subject}", ""]
    if not cards:
        lines += ["No flashcards yet.", ""]
    topic = None
    for card in _in_order(cards, materials):
        of = _topic_of(card, materials, names)
        if of != topic:
            topic = of
            lines += [f"## {of}", ""]
        lines += [f"**{card.front}**", "", card.back, "", f"*{card.source.filename} › {card.source.title}*", ""]
    return "\n".join(lines)


def _readme(
    subject: str, course: str, contents: list[tuple[str, list[str]]], cards: list[ReviewCard], missing: list[str]
) -> str:
    on = datetime.now(UTC).strftime("%Y-%m-%d")
    lines = [f"# {subject}", "", f"From the course {course}, downloaded from Qubit Notes on {on}.", ""]
    lines += ["Each topic is a folder, numbered in the order the topics are read, with its material in its order.", ""]
    for folder, filenames in contents:
        lines.append(f"- {folder}: {', '.join(filenames) if filenames else 'no material'}")
    lines += [
        "",
        f"Your {len(cards)} flashcard{'' if len(cards) == 1 else 's'} of the subject are in flashcards.csv (front,"
        " back, topic, material, section), to import into a flashcard app, and in flashcards.md, to read.",
    ]
    if missing:
        lines += ["", f"These couldn't be included, as their files weren't there: {', '.join(missing)}."]
    return "\n".join(lines) + "\n"
