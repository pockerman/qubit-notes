"""The assistant a student asks, in their own words, while reading a material or studying a topic.

Each request is understood and, if it's a question, answered in one call to the AI: it is given the conversation so
far, the passages of the course's material that a search finds for the request, and the request. A request for a
summary or a quiz gets the same saved one the student would get by asking for it directly.
"""

import json
import uuid
from datetime import datetime
from typing import Literal

from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.courses import Courses
from qubit_notes.domain.errors import InvalidRequest
from qubit_notes.domain.quizzes import AIFailed, Quiz, Quizzes
from qubit_notes.domain.reading import Reading
from qubit_notes.domain.sources import Scope, Source
from qubit_notes.domain.summaries import Summaries, Summary
from qubit_notes.domain.written import now
from qubit_notes.platform.port import Chunk, Message, StudyPlatform

# the passages of the material the AI is given to answer from
PASSAGES = 6
# the most of a passage the AI is given
PASSAGE_CHARACTERS = 2_000
# the size of a quiz asked for without saying how many questions
QUIZ_QUESTIONS = 5

SYSTEM = """You are a study assistant. A student asks you something while reading their study material.

First decide what they ask for, as "request":
- "summary" only when they ask for a summary in so many words, e.g. "Summarise this section" or "Give me a summary
  of the topic";
- "quiz" only when they ask to be quizzed or tested, e.g. "Quiz me on the whole document";
- "question" for everything else: whatever they ask about the material, e.g. "What is a shape function?", "How is a
  mesh generated?" or "Explain assembly", is a question, which you answer.
For a summary or a quiz, "of" is what it is of: "section" (the section they are reading, the default), "document"
(the whole material) or "topic" (all the material of the topic); "new" is true if they ask for a new one rather than
the one they had; "questions" is how many questions they ask for, or 0 if they don't say. Leave "answer" empty.

Answer a question only from the passages of their material you are given: never from anything else you know. Answer
clearly and concisely, in Markdown, and list in "cited" the references of the passages your answer draws on, e.g.
["P1", "P3"]. If the passages do not answer the question, say that their material does not cover it, set "covered"
to false and cite nothing."""


class Understood(BaseModel):
    """what the AI makes of a request"""

    request: Literal["question", "summary", "quiz"]
    of: Literal["section", "document", "topic"] = "section"
    new: bool = False
    questions: int = 0
    answer: str = ""
    covered: bool = True
    cited: list[str] = Field(default_factory=list)


class Turn(BaseModel):
    """what the student asked and what the assistant replied"""

    id: str
    question: str
    kind: Literal["answer", "summary", "quiz"]
    # an answer's text; for a summary or a quiz, what the assistant says of it
    answer: str
    # whether the material covers the question
    covered: bool = True
    # the sections an answer draws on
    sources: list[Source] = Field(default_factory=list)
    # None once deleted with their material
    summary: Summary | None = None
    quiz: Quiz | None = None
    created_at: datetime


class Conversation(BaseModel):
    id: str | None
    turns: list[Turn]


def _about(where: Scope) -> Scope:
    """what a conversation is about: the material being read, or the topic"""
    if where.document_id:
        return Scope(course_id=where.course_id, document_id=where.document_id)
    return Scope(course_id=where.course_id, subject=where.subject, topic=where.topic)


def _source(chunk: Chunk) -> Source:
    metadata = chunk.metadata
    filename = metadata.get("filename", "")
    return Source(
        document_id=chunk.document_id,
        filename=filename,
        section=int(metadata.get("section") or 1),
        title=metadata.get("section_title") or filename,
    )


class Assistant:
    def __init__(
        self,
        engine: Engine,
        platform: StudyPlatform,
        courses: Courses,
        reading: Reading,
        summaries: Summaries,
        quizzes: Quizzes,
    ):
        self._engine = engine
        self._platform = platform
        self._courses = courses
        self._reading = reading
        self._summaries = summaries
        self._quizzes = quizzes

    def ask(self, student: str, where: Scope, question: str) -> Turn:
        """answers the student's request, made while reading ``where``: a section of a material, or a topic"""
        question = question.strip()
        if not question:
            raise InvalidRequest("ask the assistant something")
        course = self._courses.get_by_id(student, where.course_id)
        reading = self._describe(student, where)
        conversation_id = self._conversation_id(student, where, create=True)

        passages = self._passages(course.id, question)
        understood = self._understand(conversation_id, reading, passages, question)

        turn = {"id": uuid.uuid4().hex, "question": question, "created_at": now()}
        if understood.request == "question":
            cited = [passages[ref][0] for ref in dict.fromkeys(understood.cited) if ref in passages]
            covered = understood.covered and bool(cited)
            answer = understood.answer.strip() or "Your material does not cover this."
            turn |= {"kind": "answer", "answer": answer, "covered": covered, "sources": cited if covered else []}
        elif understood.request == "summary":
            summary = self._summaries.get(student, self._scope(student, where, understood.of), understood.new)
            turn |= {"kind": "summary", "answer": summary.content, "sources": summary.sources, "summary": summary}
        else:
            count = understood.questions or QUIZ_QUESTIONS
            quiz = self._quizzes.get(student, self._scope(student, where, understood.of), count, understood.new)
            what = f"a quiz of {len(quiz.questions)} questions"
            turn |= {"kind": "quiz", "answer": f"Here is {what}.", "sources": quiz.sources, "quiz": quiz}
        turn = Turn(**turn)

        self._platform.add_to_conversation(
            conversation_id,
            [Message(role="user", content=question), Message(role="assistant", content=turn.answer)],
        )
        with self._engine.begin() as connection:
            connection.execute(
                insert(storage.conversation_turns).values(
                    id=turn.id,
                    conversation_id=conversation_id,
                    question=turn.question,
                    kind=turn.kind,
                    answer=turn.answer,
                    covered=turn.covered,
                    sources=[source.model_dump() for source in turn.sources],
                    summary_id=turn.summary.id if turn.summary else None,
                    quiz_id=turn.quiz.id if turn.quiz else None,
                    created_at=turn.created_at,
                )
            )
        return turn

    def conversation(self, student: str, where: Scope) -> Conversation:
        """the student's conversation on the material or the topic, oldest turn first"""
        self._courses.get_by_id(student, where.course_id)
        conversation_id = self._conversation_id(student, where, create=False)
        if conversation_id is None:
            return Conversation(id=None, turns=[])
        turns = storage.conversation_turns
        with self._engine.connect() as connection:
            rows = connection.execute(
                select(turns).where(turns.c.conversation_id == conversation_id).order_by(turns.c.created_at)
            ).all()
        return Conversation(id=conversation_id, turns=[self._turn(student, row) for row in rows])

    def start_again(self, student: str, where: Scope) -> Conversation:
        """forgets the student's conversation on the material or the topic, so the next request starts a new one"""
        self._courses.get_by_id(student, where.course_id)
        conversation_id = self._conversation_id(student, where, create=False)
        if conversation_id is not None:
            self._forget([conversation_id])
        return Conversation(id=None, turns=[])

    def forget_material(self, document_id: str) -> None:
        """forgets every student's conversation on the deleted material"""
        table = storage.conversations
        with self._engine.connect() as connection:
            ids = [row.id for row in connection.execute(select(table.c.id).where(table.c.document_id == document_id))]
        self._forget(ids)

    def forget_course(self, course_id: str) -> None:
        """forgets every student's conversations in the deleted course"""
        table = storage.conversations
        with self._engine.connect() as connection:
            ids = [row.id for row in connection.execute(select(table.c.id).where(table.c.course_id == course_id))]
        self._forget(ids)

    def forget_student(self, student: str) -> None:
        table = storage.conversations
        with self._engine.connect() as connection:
            ids = [row.id for row in connection.execute(select(table.c.id).where(table.c.student == student))]
        self._forget(ids)

    # understanding

    def _understand(
        self, conversation_id: str, reading: str, passages: dict[str, tuple[Source, str]], question: str
    ) -> Understood:
        material = "\n\n".join(
            f"[{reference}] {source.filename} › {source.title}\n{text}"
            for reference, (source, text) in passages.items()
        )
        prompt = (
            f"The student is {reading}.\n\n"
            f"Passages of their material:\n\n{material or '(none found)'}\n\n"
            f"The student says:\n{question}"
        )
        history = self._platform.conversation_context(conversation_id)
        for _ in range(2):
            reply = self._platform.complete(SYSTEM, prompt, json_schema=Understood.model_json_schema(), history=history)
            try:
                return Understood.model_validate(json.loads(reply))
            except (ValueError, ValidationError) as e:
                logger.warning(f"the AI's reply is not valid: {e}")
        raise AIFailed("the assistant could not understand that; try asking another way")

    def _passages(self, course_id: str, question: str) -> dict[str, tuple[Source, str]]:
        """the passages of the course's material a search finds for the question, with their sections, by
        reference, e.g. P1"""
        chunks = self._platform.search(course_id, question, top_k=PASSAGES)
        return {
            f"P{i}": (_source(chunk), chunk.content[:PASSAGE_CHARACTERS]) for i, chunk in enumerate(chunks, start=1)
        }

    def _describe(self, student: str, where: Scope) -> str:
        if not where.document_id:
            return f"studying the topic {where.subject} › {where.topic}"
        opened = self._reading.open(student, where.course_id, where.document_id)
        title = next((s.title for s in opened.sections if s.position == where.section), "")
        section = f'the section "{title}" of ' if title else ""
        return f'reading {section}"{opened.filename}", of the topic {opened.subject} › {opened.topic}'

    def _scope(self, student: str, where: Scope, of: str) -> Scope:
        """what a summary or a quiz asked for is of, given where the student is"""
        if not where.document_id or of == "topic":
            if where.document_id:
                opened = self._reading.open(student, where.course_id, where.document_id)
                return Scope(course_id=where.course_id, subject=opened.subject, topic=opened.topic)
            return Scope(course_id=where.course_id, subject=where.subject, topic=where.topic)
        if of == "section" and where.section is not None:
            return Scope(course_id=where.course_id, document_id=where.document_id, section=where.section)
        return Scope(course_id=where.course_id, document_id=where.document_id)

    # conversations

    def _conversation_id(self, student: str, where: Scope, create: bool) -> str | None:
        about = _about(where)
        table = storage.conversations
        conditions = [table.c.student == student, table.c.course_id == about.course_id]
        for column in ("document_id", "subject", "topic"):
            value = getattr(about, column)
            conditions.append(table.c[column].is_(None) if value is None else table.c[column] == value)
        with self._engine.connect() as connection:
            row = connection.execute(select(table.c.id).where(*conditions)).first()
        if row or not create:
            return row.id if row else None

        conversation_id = f"study-{uuid.uuid4().hex}"
        self._platform.start_conversation(student, conversation_id)
        with self._engine.begin() as connection:
            connection.execute(
                insert(table).values(
                    id=conversation_id,
                    student=student,
                    course_id=about.course_id,
                    document_id=about.document_id,
                    subject=about.subject,
                    topic=about.topic,
                    created_at=now(),
                )
            )
        return conversation_id

    def _forget(self, ids: list[str]) -> None:
        for conversation_id in ids:
            self._platform.end_conversation(conversation_id)
        with self._engine.begin() as connection:
            connection.execute(
                delete(storage.conversation_turns).where(storage.conversation_turns.c.conversation_id.in_(ids))
            )
            connection.execute(delete(storage.conversations).where(storage.conversations.c.id.in_(ids)))

    def _turn(self, student: str, row) -> Turn:
        return Turn(
            id=row.id,
            question=row.question,
            kind=row.kind,
            answer=row.answer,
            covered=row.covered,
            sources=[Source(**source) for source in row.sources],
            summary=self._summaries.by_id(student, row.summary_id) if row.summary_id else None,
            quiz=self._quizzes.by_id(student, row.quiz_id) if row.quiz_id else None,
            created_at=row.created_at,
        )
