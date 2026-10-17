"""The app's own data: what students make while studying (notes, summaries, quizzes), as opposed to their
material, which lives in gogi."""

from sqlalchemy import Column, DateTime, Float, Integer, MetaData, String, Table, Text, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

metadata = MetaData()

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


def connect(database_url: str) -> Engine:
    """The database, with its tables created if they don't exist yet."""
    if database_url in ("sqlite://", "sqlite:///:memory:"):
        # one in-memory database, shared by every thread that serves requests
        engine = create_engine(database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool)
    else:
        engine = create_engine(database_url)
    metadata.create_all(engine)
    return engine
