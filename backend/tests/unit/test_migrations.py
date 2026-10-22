"""The migrations make the tables of storage.py, on SQLite and on Postgres, and a database made before there were
migrations is taken over without losing its data.

The Postgres tests run when QUBIT_NOTES_TEST_POSTGRES_URL names an empty database they may clear, e.g.
postgresql+psycopg://gogi:gogi@localhost:5432/qubit_notes_test
"""

import os
from datetime import UTC, datetime

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, insert, inspect, select, text

from qubit_notes import storage

POSTGRES = os.environ.get("QUBIT_NOTES_TEST_POSTGRES_URL")


def _cleared(url: str) -> str:
    engine = create_engine(url)
    with engine.begin() as connection:
        for table in inspect(connection).get_table_names():
            connection.execute(text(f'DROP TABLE IF EXISTS "{table}" CASCADE'))
    engine.dispose()
    return url


@pytest.fixture(params=["sqlite", "postgres"])
def database_url(request, tmp_path):
    if request.param == "sqlite":
        return f"sqlite:///{tmp_path / 'qubit-notes.db'}"
    if not POSTGRES:
        pytest.skip("QUBIT_NOTES_TEST_POSTGRES_URL is not set")
    return _cleared(POSTGRES)


def _head() -> str:
    return ScriptDirectory.from_config(storage.migrations_config()).get_current_head()


def _revision(engine) -> str | None:
    with engine.connect() as connection:
        return MigrationContext.configure(connection).get_current_revision()


def _differences(engine) -> list:
    with engine.connect() as connection:
        return compare_metadata(MigrationContext.configure(connection), storage.metadata)


def test_the_migrations_make_the_tables_of_storage(database_url):
    engine = storage.connect(database_url)

    assert _revision(engine) == _head()
    # a change to storage.py without a migration shows here
    assert _differences(engine) == []


def test_migrating_again_changes_nothing(database_url):
    storage.connect(database_url).dispose()
    engine = storage.connect(database_url)

    assert _revision(engine) == _head()


def test_a_database_made_before_migrations_keeps_its_data(database_url):
    engine = create_engine(database_url)
    # as the app made its tables before there were migrations, which were all but its own platform's
    before = [table for table in storage.metadata.sorted_tables if not table.name.startswith("platform_")]
    storage.metadata.create_all(engine, tables=before)
    now = datetime.now(UTC)
    note = {
        "id": "n1",
        "student": "maria",
        "course_id": "maria--aeronautics",
        "document_id": "d1",
        "text": "Mesh",
        "created_at": now,
        "updated_at": now,
    }
    with engine.begin() as connection:
        connection.execute(insert(storage.notes).values(**note))
    engine.dispose()

    engine = storage.connect(database_url)

    assert _revision(engine) == _head()
    with engine.connect() as connection:
        assert connection.execute(select(storage.notes.c.text)).scalars().all() == ["Mesh"]


def test_the_migrations_can_be_undone(database_url):
    engine = storage.connect(database_url)
    config = storage.migrations_config()
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.downgrade(config, "base")
    assert set(inspect(engine).get_table_names()) <= {"alembic_version"}

    storage.migrate(engine)
    assert _differences(engine) == []


def test_the_migrate_command(database_url, monkeypatch, capsys):
    from qubit_notes import cli

    monkeypatch.setenv("QUBIT_NOTES_DATABASE_URL", database_url)

    assert cli.main(["migrate"]) == 0
    assert _revision(create_engine(database_url)) == _head()
    assert "up to date" in capsys.readouterr().out
