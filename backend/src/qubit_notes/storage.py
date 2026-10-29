"""The app's own data: what students make while studying (notes, summaries, quizzes, flashcards), and, where the
app is its own platform, the students' material, the conversations with the assistant and what it remembers. Where
the platform is gogi, those live in gogi and the platform's tables stay empty.

The tables are created and changed by the migrations in ``migrations/versions``, which the app runs when it starts.
A change to a table here needs a migration: from backend/, ``uv run alembic revision --autogenerate -m "..."``.
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    TypeDecorator,
    create_engine,
    inspect,
)
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

# constraints are named, so migrations can refer to them on every database
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }
)

# a course's topics, each in a subject: they stay when all their material is deleted
topics = Table(
    "topics",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("subject", String, primary_key=True),
    Column("topic", String, primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    # what the topic is called, as the student typed it; named after its id if unset
    Column("name", String),
)

# what a course is called, as its creator typed it; a course without one is titled after its name
course_titles = Table(
    "course_titles",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("title", String, nullable=False),
)

# a course's subjects: they stay when all their topics are deleted
subjects = Table(
    "subjects",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("subject", String, primary_key=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# what a subject is called, as the student typed it; a subject without one is named after its id
subject_names = Table(
    "subject_names",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("subject", String, primary_key=True),
    Column("name", String, nullable=False),
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

# the order a topic's material is meant to be read in, by its owners; a material is added last when uploaded
material_order = Table(
    "material_order",
    metadata,
    Column("course_id", String, primary_key=True),
    Column("document_id", String, primary_key=True),
    Column("subject", String, nullable=False),
    Column("topic", String, nullable=False),
    Column("position", Integer, nullable=False),
)

# what the app's admins chose for the app, by name, e.g. llm_provider: openai (domain/ai_model.py)
app_settings = Table(
    "app_settings",
    metadata,
    Column("name", String, primary_key=True),
    Column("value", String, nullable=False),
)

# the model providers' keys the admins gave the app, encrypted with its secret (domain/app_keys.py)
app_keys = Table(
    "app_keys",
    metadata,
    Column("provider", String, primary_key=True),
    Column("encrypted", Text, nullable=False),
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

flashcard_decks = Table(
    "flashcard_decks",
    metadata,
    Column("id", String, primary_key=True),
    *_scope_columns(),
    Column("count", Integer, nullable=False),
)

# a deck's cards, each with when the student is to review it next: see domain/reviews.py
flashcards = Table(
    "flashcards",
    metadata,
    Column("id", String, primary_key=True),
    Column("deck_id", String, nullable=False, index=True),
    Column("student", String, nullable=False, index=True),
    Column("course_id", String, nullable=False),
    Column("position", Integer, nullable=False),
    Column("front", Text, nullable=False),
    Column("back", Text, nullable=False),
    # the section it's from
    Column("source", JSON, nullable=False),
    Column("ease", Float, nullable=False),
    Column("interval_days", Integer, nullable=False),
    # how many times in a row it was remembered
    Column("repetitions", Integer, nullable=False),
    # None once a newer deck of its scope takes its place in the reviews
    Column("due_at", DateTime(timezone=True), index=True),
    Column("reviewed_at", DateTime(timezone=True)),
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
    Column("deck_id", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# the conversion of an uploaded PDF or EPUB to the Markdown its material is: see domain/conversions.py
conversions = Table(
    "conversions",
    metadata,
    Column("id", String, primary_key=True),
    Column("course_id", String, nullable=False),
    Column("document_id", String, nullable=False, index=True),
    Column("original_id", String, nullable=False),
    Column("status", String, nullable=False, index=True),
    Column("error", Text),
    # once converted, the platform's processing of the Markdown
    Column("ingest_job_id", String),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

# a document made into a subject's lessons, a topic of each of its headings: see domain/lessons.py
lesson_imports = Table(
    "lesson_imports",
    metadata,
    Column("id", String, primary_key=True),
    Column("student", String, nullable=False),
    Column("course_id", String, nullable=False, index=True),
    Column("subject", String, nullable=False),
    Column("filename", String, nullable=False),
    # the document, kept by the platform as the original of a PDF's or an EPUB's lessons
    Column("original_id", String),
    Column("status", String, nullable=False),
    Column("error", Text),
    # the ids of the topics made, in order
    Column("topics", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

# the courses that are collections of papers, under My Papers: see domain/papers.py
paper_collections = Table(
    "paper_collections",
    metadata,
    Column("course_id", String, primary_key=True),
)

# a paper's details, filled in from it when uploaded and changed by its collection's owners
paper_details = Table(
    "paper_details",
    metadata,
    Column("document_id", String, primary_key=True),
    Column("course_id", String, nullable=False, index=True),
    Column("title", String, nullable=False),
    # in order
    Column("authors", JSON, nullable=False),
    Column("year", Integer),
    Column("venue", String, nullable=False),
    Column("doi", String, nullable=False),
)


# the app's own platform (platform/standalone): courses are its indexes, and material is its documents


class Embedding(TypeDecorator):
    """A chunk's embedding: pgvector's vector on Postgres, which searches them; a JSON list elsewhere, e.g. SQLite,
    searched in Python. Its size is the embedding model's, so the column has none."""

    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(Vector())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        return None if value is None else [float(x) for x in value]

    def process_result_value(self, value, dialect):
        return None if value is None else [float(x) for x in value]


platform_indexes = Table(
    "platform_indexes",
    metadata,
    Column("name", String, primary_key=True),
    Column("owner", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# an index's members, its owner among them; role is owner or reader
platform_index_members = Table(
    "platform_index_members",
    metadata,
    Column("index_name", String, primary_key=True),
    Column("member", String, primary_key=True, index=True),
    Column("role", String, nullable=False),
)

platform_documents = Table(
    "platform_documents",
    metadata,
    Column("id", String, primary_key=True),
    Column("index_name", String, nullable=False, index=True),
    Column("filename", String, nullable=False),
    Column("content_type", String, nullable=False),
    Column("size_bytes", Integer, nullable=False),
    Column("metadata", JSON, nullable=False),
    # the status of the ingestion of its current content, and that ingestion's job: the document's version
    Column("status", String, nullable=False),
    Column("job_id", String, nullable=False),
    # a file that is kept but not ingested, e.g. a video
    Column("store_only", Boolean, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# the ingestion of a document's content; a job left pending or running when the app stopped is resumed when it starts
platform_jobs = Table(
    "platform_jobs",
    metadata,
    Column("id", String, primary_key=True),
    Column("index_name", String, nullable=False),
    Column("document_id", String, nullable=False, index=True),
    Column("status", String, nullable=False, index=True),
    Column("error", Text),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("updated_at", DateTime(timezone=True), nullable=False),
)

# a document's sections, read from it by its ingestion, each with its own text
platform_sections = Table(
    "platform_sections",
    metadata,
    Column("document_id", String, primary_key=True),
    Column("position", Integer, primary_key=True),
    Column("title", String, nullable=False),
    Column("level", Integer, nullable=False),
    Column("page_start", Integer),
    Column("page_end", Integer),
    Column("content", Text, nullable=False),
)

# the parts of the sections that search finds, embedded with a model; found only by searching with the same model
platform_chunks = Table(
    "platform_chunks",
    metadata,
    Column("id", String, primary_key=True),
    Column("index_name", String, nullable=False, index=True),
    Column("document_id", String, nullable=False, index=True),
    Column("model", String, nullable=False),
    Column("section", Integer, nullable=False),
    Column("content", Text, nullable=False),
    Column("embedding", Embedding, nullable=False),
)

platform_conversations = Table(
    "platform_conversations",
    metadata,
    Column("id", String, primary_key=True),
    Column("member", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

platform_messages = Table(
    "platform_messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("conversation_id", String, nullable=False, index=True),
    Column("role", String, nullable=False),
    Column("content", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

# what the assistant remembers of a student, key to a JSON value
platform_memories = Table(
    "platform_memories",
    metadata,
    Column("member", String, primary_key=True),
    Column("key", String, primary_key=True),
    Column("value", JSON, nullable=False),
)


MIGRATIONS = Path(__file__).parent / "migrations"
# the first migration: the tables as they were before there were migrations
BASELINE = "0001"


def migrations_config() -> Config:
    config = Config()
    config.set_main_option("script_location", str(MIGRATIONS))
    return config


def migrate(engine: Engine) -> None:
    """Brings the database's tables up to date. A database made before there were migrations has the baseline's
    tables already, and is marked as having them."""
    config = migrations_config()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        tables = set(inspect(connection).get_table_names())
        if "alembic_version" not in tables and "notes" in tables:
            command.stamp(config, BASELINE)
        command.upgrade(config, "head")


def in_memory(database_url: str) -> bool:
    return database_url in ("sqlite://", "sqlite:///:memory:")


def connect(database_url: str) -> Engine:
    """The database, migrated to the tables the app needs."""
    if in_memory(database_url):
        # one in-memory database, shared by every thread that serves requests
        engine = create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        engine = create_engine(database_url)
    migrate(engine)
    return engine
