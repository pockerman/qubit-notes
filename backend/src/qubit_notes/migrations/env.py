"""Alembic's environment: migrates the database qubit-notes is given (storage.migrate), or, run as ``alembic`` from
backend/, the one of QUBIT_NOTES_DATABASE_URL."""

from alembic import context
from sqlalchemy import create_engine, text

from qubit_notes import storage
from qubit_notes.settings import Settings

# replicas of the app may start together; on Postgres one migrates while the others wait
MIGRATION_LOCK = 7_310_211


def run(connection) -> None:
    context.configure(connection=connection, target_metadata=storage.metadata, render_as_batch=True)
    with context.begin_transaction():
        if connection.dialect.name == "postgresql":
            connection.execute(text("SELECT pg_advisory_xact_lock(:lock)"), {"lock": MIGRATION_LOCK})
        context.run_migrations()


connection = context.config.attributes.get("connection")
if connection is not None:
    run(connection)
else:
    with create_engine(Settings().database_url).connect() as connection:
        run(connection)
