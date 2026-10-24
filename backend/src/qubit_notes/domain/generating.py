"""New material the AI writes from materials the student chooses (features/generating.feature). The AI cites the
sections it drew on by labels, [S1], [S2], …, which are then made references to the sections, so they are links in
the new material whatever the model makes of the reference syntax. What it writes is not saved here: the student
saves it as material they wrote."""

import re
from typing import Literal

from pydantic import BaseModel

from qubit_notes.domain.conversions import is_original
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import Conflict, InvalidRequest, NotFound
from qubit_notes.domain.images import is_image
from qubit_notes.domain.materials import is_video
from qubit_notes.domain.reading import Reading
from qubit_notes.platform.port import IngestStatus, StudyPlatform

Kind = Literal["revision notes", "cheat sheet", "combined notes", "worked examples"]

# what the AI is asked to write, and what the material is called, by kind
ASKED: dict[str, str] = {
    "revision notes": "revision notes",
    "cheat sheet": "a cheat sheet",
    "combined notes": "the materials combined into one set of notes",
    "worked examples": "worked examples",
}
NAMED: dict[str, str] = {kind: kind.capitalize() for kind in ASKED}
UNNAMED = "Generated notes"

# the most text generated from at once
MAX_CHARACTERS = 60_000

SYSTEM = """You write new study material for a student, in Markdown, from their own material. Use only the material
you are given. Use headings, lists and tables where they help. After each statement drawn from the material, cite the
part it came from by its label in square brackets, e.g. [S2], or [S1][S3] for several. Write nothing before or after
the material itself."""

LABEL = re.compile(r"\[(S\d+)\]")


class Generated(BaseModel):
    # what the material is called until the student names it
    name: str
    # Markdown, citing its sources with references to them
    text: str


class Generator:
    def __init__(self, platform: StudyPlatform, courses: Courses, reading: Reading):
        self._platform = platform
        self._courses = courses
        self._reading = reading
        self.max_characters = MAX_CHARACTERS

    def generate(
        self, student: str, course_id: str, document_ids: list[str], kind: Kind | None, instructions: str
    ) -> Generated:
        course = self._courses.get_by_id(student, course_id)
        self._courses.require_owner(student, course)
        if not document_ids:
            raise InvalidRequest("choose at least one material to generate from")
        instructions = instructions.strip()
        if kind is None and not instructions:
            raise InvalidRequest("choose a kind of material, or write instructions, or both")

        # each section of each material, labelled for the AI to cite, with the reference it is cited by
        labelled: list[tuple[str, str, str]] = []
        for document_id in dict.fromkeys(document_ids):
            document = self._platform.get_document(course.id, document_id)
            if document is None or is_image(document) or is_original(document):
                raise NotFound(f"no material {document_id!r} in {course.name!r}")
            if is_video(document.content_type):
                raise InvalidRequest(f"{document.filename!r} is a video, with no text to generate from")
            if document.status != IngestStatus.COMPLETED:
                raise Conflict(f"{document.filename!r} is not ready yet; try again once it has been processed")
            subject, topic = document.metadata.get("subject", ""), document.metadata.get("topic", "")
            path = f"{subject}/{topic}/{document.filename}"
            for part in self._reading.contents(student, course.id, document_id):
                title = part.section.title.strip()
                reference = f"[[{path}#{title}]]" if title else f"[[{path}]]"
                labelled.append((f"{document.filename} › {title or document.filename}", part.content, reference))

        if sum(len(content) for _, content, _ in labelled) > self.max_characters:
            raise InvalidRequest(
                f"the material chosen is too long to generate from at once: choose less, up to "
                f"{self.max_characters:,} characters in all"
            )

        material = "\n\n".join(
            f"[S{i}] {heading}\n{content}" for i, (heading, content, _) in enumerate(labelled, start=1)
        )
        asked = f"Write {ASKED[kind]}." if kind else "Write what the student asks for."
        if instructions:
            asked += f"\n\nThe student asks: {instructions}"
        text = self._platform.complete(SYSTEM, f"{asked}\n\nThe material:\n\n{material}").strip()

        references = {f"S{i}": reference for i, (_, _, reference) in enumerate(labelled, start=1)}
        # a label the material doesn't have is dropped
        text = LABEL.sub(lambda match: references.get(match.group(1), ""), text)
        return Generated(name=NAMED[kind] if kind else UNNAMED, text=text)
