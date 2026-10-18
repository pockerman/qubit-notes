"""The app's own data: what students make while studying (notes, summaries, quizzes), as opposed to their
material, which lives in gogi."""

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

metadata = MetaData()

# a course's topics, each in a subject: they stay when all their material is deleted
topics = Table(
    "topics",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("subject", String, primary_key=True),
    Column("topic", String, primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# where the owners put a topic among its subject's topics, 0 first; topics without one come after, oldest first
topic_order = Table(
    "topic_order",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("subject", String, primary_key=True),
    Column("topic", String, primary_key=True),
    Column("position", Integer, nullable=False),
)

notes = Table(
    "notes",
    metadata,
    Column("id", String, primary_key=True),
    Column("student", String, nullable=False, index=True),
    Column("course_id", String, nullable=False),
    Column("document_id", String, nullable=False, index=True),
    # a note on a text is anchored to a passage of a section: the passage, and where it starts in the section
    Column("section", Integer),
    Column("section_title", String),
    Column("passage", Text),
    Column("passage_start", Integer),
    # a note on a video is anchored to a moment
    Column("at_seconds", Float),
    Column("text", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)


def _scope_columns() -> list[Column]:
    """what a summary or quiz is about: a section of a document, a document, or a topic"""
    return [
        Column("student", String, nullable=False, index=True),
        Column("course_id", String, nullable=False),
        Column("document_id", String, index=True),
        Column("section", Integer),
        Column("subject", String),
        Column("topic", String),
        # the sections it was written from, and the materials, document id to filename
        Column("sources", JSON, nullable=False),
        Column("documents", JSON, nullable=False),
        Column("created_at", DateTime(timezone=True), nullable=False),
    ]


summaries = Table(
    "summaries",
    metadata,
    Column("id", String, primary_key=True),
    *_scope_columns(),
    Column("content", Text, nullable=False),
)

quizzes = Table(
    "quizzes",
    metadata,
    Column("id", String, primary_key=True),
    *_scope_columns(),
    Column("count", Integer, nullable=False),
    # each question with its choices, the index of the correct one, and the section it's from
    Column("questions", JSON, nullable=False),
)

quiz_attempts = Table(
    "quiz_attempts",
    metadata,
    Column("id", String, primary_key=True),
    Column("quiz_id", String, nullable=False, index=True),
    Column("student", String, nullable=False),
    Column("answers", JSON, nullable=False),
    Column("score", Integer, nullable=False),
    Column("total", Integer, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


# a student's conversation with the assistant on a material or a topic; its id is also the platform's, which keeps
# what the AI is given of it
conversations = Table(
    "conversations",
    metadata,
    Column("id", String, primary_key=True),
    Column("student", String, nullable=False, index=True),
    Column("course_id", String, nullable=False),
    Column("document_id", String, index=True),
    Column("subject", String),
    Column("topic", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# what the student asked in a conversation and what the assistant replied: an answer citing sections, or a summary or
# a quiz, which are saved with the others
conversation_turns = Table(
    "conversation_turns",
    metadata,
    Column("id", String, primary_key=True),
    Column("conversation_id", String, nullable=False, index=True),
    Column("question", Text, nullable=False),
    Column("kind", String, nullable=False),
    Column("answer", Text, nullable=False),
    Column("covered", Boolean, nullable=False),
    Column("sources", JSON, nullable=False),
    Column("summary_id", String),
    Column("quiz_id", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
)


def connect(database_url: str) -> Engine:
    """The database, with its tables created if they don't exist yet."""
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        # one in-memory database, shared by every thread that serves requests
        engine = create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        engine = create_engine(database_url)
    metadata.create_all(engine)
    return engine
