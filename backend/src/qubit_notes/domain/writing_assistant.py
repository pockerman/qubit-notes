"""The writing assistant (features/writing_assistant.feature): WriteMaterialAssistantAgent helps an owner of a course
write a Markdown material in one of its topics, on a subject they propose or with a section of what they are
writing, searching the web for what it needs and citing it.

Its replies aren't kept: the student's browser gives it the conversation so far with each request, and what the
student takes of its replies goes into their material.
"""

import re

from pydantic import BaseModel, Field

from qubit_notes.domain.course_titles import CourseTitles
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import InvalidRequest, NotFound
from qubit_notes.domain.topics import Topics
from qubit_notes.domain.usage import AIUsage
from qubit_notes.platform.port import Message, StudyPlatform, WebSource

# of what the student has written, what the AI is given, as for summaries
MAX_DRAFT_CHARACTERS = 60_000
MAX_REQUEST_CHARACTERS = 4_000
# of the conversation so far, the turns the AI is given, and of each reply, how much
MAX_TURNS = 10
MAX_REPLY_CHARACTERS = 12_000

SYSTEM = (
    "You are a writing assistant. You help a student write their own study material, in Markdown, to go into "
    "their notes. Write what they ask for as the material itself: headings, paragraphs, lists, tables and code "
    "blocks as they suit it, mathematics in LaTeX between $ signs ($$ for a display), with no preamble or "
    "remarks about what you wrote. Where they ask about one section of their material, write only what goes in "
    "that section, without its heading, so it can take the place of the section's text, keeping to what the rest "
    "of the material says. Search the web for what you aren't sure of and for what the material should cite, "
    "prefer reputable sources (textbooks, papers, university courses, official documentation), and never make up "
    "a source. Match the level and the style of what the student has written."
)

# a Markdown heading: its #s, and its title
HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


class Turn(BaseModel):
    """an earlier request in the conversation, and the reply to it"""

    request: str
    reply: str


class WritingRequest(BaseModel):
    """what the student asks, with what they have written so far and the section they want help with, if one"""

    request: str
    draft: str = ""
    # the title of the section of the draft, as its heading says it, e.g. "2 Shape functions"
    section: str | None = None
    history: list[Turn] = Field(default_factory=list)
    search_web: bool = True


class WritingReply(BaseModel):
    # Markdown, citing its sources by number: [1] is the first of them
    reply: str
    sources: list[WebSource] = Field(default_factory=list)
    # whether the AI searched the web for it
    searched: bool
    # the section it is about, if it was asked about one
    section: str | None = None


def sections(draft: str) -> list[tuple[str, int, int]]:
    """the draft's sections: each heading's title, and where its text starts and ends, up to the next heading of its
    level or higher"""
    lines = draft.splitlines(keepends=True)
    headings: list[tuple[int, str, int, int]] = []
    offset = 0
    fenced = False
    for line in lines:
        if line.lstrip().startswith("```"):
            fenced = not fenced
        elif not fenced and (heading := HEADING.match(line.rstrip("\n"))):
            headings.append((len(heading.group(1)), heading.group(2), offset, offset + len(line)))
        offset += len(line)
    found = []
    for i, (level, title, _, text_start) in enumerate(headings):
        end = next((start for lvl, _, start, _ in headings[i + 1 :] if lvl <= level), len(draft))
        found.append((title, text_start, end))
    return found


def section_text(draft: str, title: str) -> str | None:
    for found, start, end in sections(draft):
        if found == title:
            return draft[start:end].strip()
    return None


class WriteMaterialAssistantAgent:
    def __init__(self, platform: StudyPlatform, courses: Courses, titles: CourseTitles, topics: Topics, ai: AIUsage):
        self._platform = platform
        self._courses = courses
        self._titles = titles
        self._topics = topics
        self._ai = ai

    def ask(self, student: str, course_id: str, subject: str, topic: str, asked: WritingRequest) -> WritingReply:
        request = asked.request.strip()
        if not request:
            raise InvalidRequest("ask the writing assistant something")
        if len(request) > MAX_REQUEST_CHARACTERS:
            raise InvalidRequest(f"ask in at most {MAX_REQUEST_CHARACTERS} characters")
        course = self._courses.get_by_id(student, course_id)
        self._courses.require_owner(student, course)
        found = next((t for t in self._topics.of_course(course) if (t.subject, t.topic) == (subject, topic)), None)
        if found is None:
            raise NotFound(f"no topic {subject}/{topic} in {course.name!r}")

        title = self._titles.of([course]).get(course.id) or course.name
        prompt = [f"The material is for the course {title}, the subject {found.subject_name}, the topic {found.name}."]
        draft = asked.draft.strip()
        if draft:
            prompt.append(f"What the student has written so far:\n\n{draft[:MAX_DRAFT_CHARACTERS]}")
        section = None
        if asked.section:
            text = section_text(asked.draft, asked.section)
            if text is None:
                raise InvalidRequest(f"what you have written has no section {asked.section!r}")
            section = asked.section
            prompt.append(f"The section they want help with, {section}:\n\n{text or '(nothing yet)'}")
        if not asked.search_web or not self._platform.can_search_web():
            prompt.append("Don't search the web this time: write from what you know, and cite nothing.")
        prompt.append(f"They ask: {request}")

        history = []
        for turn in asked.history[-MAX_TURNS:]:
            history += [
                Message(role="user", content=turn.request),
                Message(role="assistant", content=turn.reply[:MAX_REPLY_CHARACTERS]),
            ]
        researched = self._ai.research(
            student,
            "writing",
            SYSTEM,
            "\n\n".join(prompt),
            history,
            search_web=asked.search_web and self._platform.can_search_web(),
        )
        return WritingReply(
            reply=researched.text,
            sources=researched.sources,
            searched=researched.searched,
            section=section,
        )
