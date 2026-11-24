"""Steps of subject_repository.feature: a subject pushed to a repository on GitHub, a stand-in for which the scenarios
run against."""

import csv
import io
import re
from datetime import UTC, datetime, timedelta

from pytest_bdd import given, parsers, then, when
from sqlalchemy import select

from qubit_notes import storage
from tests.bdd.steps.app_keys_steps import SECRET
from tests.fakes.fake_github import FakeGitHub, FakeRepository


def _rows(datatable) -> list[dict]:
    header, *rows = datatable
    return [dict(zip(header, row)) for row in rows]


def _service(app):
    return app.state.subject_repositories


def _github(app) -> FakeGitHub:
    """the stand-in for GitHub, which the app pushes to, and its secret to keep the tokens with"""
    service = _service(app)
    if not isinstance(service.host, FakeGitHub):
        service.host = FakeGitHub()
        service.secret = SECRET
    return service.host


def _repository(app, name: str) -> FakeRepository:
    return _github(app).repositories[name]


def _path(course: str, subject: str) -> str:
    return f"/api/courses/{course}/subjects/{subject}/repository"


def _connect(students, context, subject, course, repository, token, name=None):
    context["response"] = students.client.put(
        _path(course, subject), headers=students.headers(name), json={"repository": repository, "token": token}
    )
    context["token"] = token
    return context["response"]


def _connection(students, subject, course, name=None) -> dict:
    response = students.client.get(_path(course, subject), headers=students.headers(name))
    assert response.status_code == 200, response.text
    return response.json()


def _push(app, students, context, subject, course, name=None):
    # the commits each repository had before, to tell the new ones
    context["commits_before"] = {n: len(r.commits) for n, r in _github(app).repositories.items()}
    context["files_before"] = {n: r.files for n, r in _github(app).repositories.items()}
    context["response"] = students.client.post(f"{_path(course, subject)}/push", headers=students.headers(name))
    return context["response"]


def _file(app, repository: str, path: str) -> str:
    files = _repository(app, repository).files
    assert path in files, sorted(files)
    return files[path]


def _new_commits(app, context, repository: str) -> list:
    return _repository(app, repository).commits[context["commits_before"].get(repository, 0) :]


def _told(context, status: int, *words: str) -> None:
    response = context["response"]
    assert response.status_code == status, response.text
    for said in words:
        assert said in response.json()["detail"], response.json()["detail"]


# GitHub


@given(parsers.parse('GitHub has the repository "{repository}", which the token "{token}" may write to'))
def repository_writable(app, repository, token):
    _github(app).add(repository, token, "write")


@given(parsers.parse('GitHub has the repository "{repository}", which the token "{token}" may only read'))
def repository_readable(app, repository, token):
    _github(app).add(repository, token, "read")


@given(parsers.parse('GitHub no longer lets the token "{token}" write to "{repository}"'))
def no_longer_writable(app, token, repository):
    _repository(app, repository).tokens[token] = "read"


@given(parsers.parse('"{repository}" has a file "{path}" that the app didn\'t write'))
def own_file(app, context, repository, path):
    _repository(app, repository).add_file(path, "My own notes, written on GitHub.\n")
    context.setdefault("own_files", {})[path] = "My own notes, written on GitHub.\n"


@given("qubit-notes is running without a secret key")
def without_secret(app):
    _github(app)
    _service(app).secret = None


# connecting


@when(parsers.parse('I connect the subject "{subject}" of "{course}" to "{repository}" with the token "{token}"'))
def connect(app, students, context, subject, course, repository, token):
    _github(app)
    _connect(students, context, subject, course, repository, token)


@when(
    parsers.parse(
        'the student "{name}" connects the subject "{subject}" of "{course}" to "{repository}" with the token "{token}"'
    )
)
def student_connects(app, students, context, name, subject, course, repository, token):
    _github(app)
    _connect(students, context, subject, course, repository, token, name)


@given(parsers.parse('I have connected the subject "{subject}" of "{course}" to "{repository}"'))
def have_connected(app, students, context, subject, course, repository):
    token = next(t for t, may in _repository(app, repository).tokens.items() if may == "write")
    response = _connect(students, context, subject, course, repository, token)
    assert response.status_code == 200, response.text


@when(parsers.parse('I disconnect the subject "{subject}" of "{course}"'))
@given(parsers.parse('I have disconnected the subject "{subject}" of "{course}"'))
def disconnect(students, context, subject, course):
    response = students.client.delete(_path(course, subject), headers=students.headers())
    assert response.status_code == 204, response.text


@then(parsers.parse('the subject "{subject}" of "{course}" is connected to "{repository}"'))
def is_connected(students, context, subject, course, repository):
    connection = _connection(students, subject, course)
    assert (connection["connected"], connection["repository"]) == (True, repository), connection
    context["connection"] = connection


@then(parsers.parse('the subject "{subject}" of "{course}" is not connected'))
def not_connected(students, subject, course):
    connection = _connection(students, subject, course)
    assert (connection["connected"], connection["repository"]) == (False, None), connection


@then(parsers.parse('the subject "{subject}" of "{course}" is not connected, as the student "{name}" sees it'))
def not_connected_for(students, subject, course, name):
    connection = _connection(students, subject, course, name)
    assert connection["connected"] is False, connection


@then("it has never been pushed")
def never_pushed(context):
    connection = context["connection"]
    assert (connection["pushed_at"], connection["commit_sha"]) == (None, None), connection


@then(parsers.parse('the subject "{subject}" of "{course}" has never been pushed'))
def subject_never_pushed(students, subject, course):
    connection = _connection(students, subject, course)
    assert (connection["pushed_at"], connection["commit_sha"]) == (None, None), connection


@then("the token is never shown back")
def token_not_shown(app, students, context):
    token = context["token"]
    assert token not in context["response"].text
    me = students.id(students.me)
    with app.state.database.connect() as connection:
        kept = connection.execute(
            select(storage.subject_repositories.c.token).where(storage.subject_repositories.c.student == me)
        ).scalar_one()
    # kept encrypted
    assert token not in kept


@then("the app keeps no token for it")
def no_token_kept(app, students):
    me = students.id(students.me)
    table = storage.subject_repositories
    with app.state.database.connect() as connection:
        assert connection.execute(select(table).where(table.c.student == me)).all() == []


@then(parsers.parse('I am told the token may not write to "{repository}"'))
def told_not_writable(context, repository):
    _told(context, 403, "may not write to", repository)


@then(parsers.parse('I am told GitHub has no repository "{repository}" that the token can see'))
def told_no_repository(context, repository):
    _told(context, 404, f"GitHub has no repository '{repository}' that the token can see")


@then("I am told the app can't keep the token without its secret")
def told_no_secret(context):
    _told(context, 409, "without its secret", "QUBIT_NOTES_SECRET_KEY")


@then("the connection is refused as not found")
def connection_not_found(context):
    assert context["response"].status_code == 404, context["response"].text


# pushing


@when(parsers.parse('I push the subject "{subject}" of "{course}"'))
def push(app, students, context, subject, course):
    _push(app, students, context, subject, course)


@when(parsers.parse('the student "{name}" pushes the subject "{subject}" of "{course}"'))
def student_pushes(app, students, context, name, subject, course):
    _push(app, students, context, subject, course, name)


@given(parsers.parse('I have pushed the subject "{subject}" of "{course}"'))
def have_pushed(app, students, context, subject, course):
    response = _push(app, students, context, subject, course)
    assert response.status_code == 200, response.text
    context["pushed_files"] = {n: r.files for n, r in _github(app).repositories.items()}


@then(parsers.parse('"{repository}" has one new commit on its default branch, with the files:'))
@then(parsers.parse('"{repository}" has one new commit, with the files:'))
def one_new_commit(app, context, repository, datatable):
    assert context["response"].status_code == 200, context["response"].text
    commits = _new_commits(app, context, repository)
    assert len(commits) == 1, commits
    assert sorted(commits[0].files) == sorted(row["file"] for row in _rows(datatable))
    context["commit"] = commits[0]


@then(parsers.parse('the subject "{subject}" of "{course}" was pushed just now, with that commit'))
def pushed_with_commit(students, context, subject, course):
    connection = _connection(students, subject, course)
    assert connection["commit_sha"] == context["commit"].sha
    assert connection["commit_url"].endswith(context["commit"].sha)
    pushed_at = datetime.fromisoformat(connection["pushed_at"])
    assert datetime.now(UTC) - pushed_at < timedelta(minutes=1)


@then(parsers.parse('"{repository}" has one new commit, changing only "{path}"'))
def one_commit_changing(app, context, repository, path):
    assert context["response"].status_code == 200, context["response"].text
    commits = _new_commits(app, context, repository)
    assert len(commits) == 1, commits
    assert commits[0].changed == {path}


@then(parsers.parse('"{repository}" has no new commit'))
def no_new_commit(app, context, repository):
    assert _new_commits(app, context, repository) == []


@then("I am told there is nothing new to push")
def nothing_new(context):
    response = context["response"]
    assert response.status_code == 200, response.text
    assert response.json()["pushed"] is False


@then("I am told the subject isn't connected to a repository")
def told_not_connected(context):
    _told(context, 409, "isn't connected to a repository")


@then(parsers.parse('I am told GitHub refused the push: the token may not write to "{repository}"'))
def told_refused(context, repository):
    _told(context, 403, "GitHub refused the push", "may not write to", repository)


@then(parsers.parse('"{repository}" has the file "{path}"'))
def has_file(app, repository, path):
    _file(app, repository, path)


@then(parsers.parse('"{repository}" has no file "{path}"'))
def has_no_file(app, context, repository, path):
    assert context["response"].status_code == 200, context["response"].text
    assert path not in _repository(app, repository).files, sorted(_repository(app, repository).files)


@then(parsers.parse('"{repository}" still has the files it was pushed'))
def still_has_pushed(app, context, repository):
    assert _repository(app, repository).files == context["pushed_files"][repository]


@then(parsers.parse('"{repository}" still has the file "{path}" as it was'))
def still_has_file(app, context, repository, path):
    assert context["response"].status_code == 200, context["response"].text
    assert _new_commits(app, context, repository), "nothing was pushed"
    assert _file(app, repository, path) == context["own_files"][path]


# what is pushed


def _notes(markdown: str) -> list[dict]:
    """the notes of a notes.md, as the app writes them: under their section's heading, each passage quoted, then its
    note unless it is a highlight; or, of a video, each note under its moment's heading"""
    notes, heading, quoted = [], None, None
    for line in markdown.splitlines():
        if line.startswith("## "):
            heading, quoted = line[3:], None
        elif line.startswith("> "):
            quoted = {"section": heading, "passage": line[2:], "note": ""}
            notes.append(quoted)
        elif line.strip() and heading is not None:
            if quoted is not None:
                quoted["note"], quoted = line, None
            else:
                notes.append({"at": heading, "note": line})
    return notes


@then(parsers.parse('"{path}" in "{repository}" has the notes:'))
def has_notes(app, path, repository, datatable):
    expected = _rows(datatable)
    found = _notes(_file(app, repository, path))
    assert [{key: note.get(key, "") for key in expected[0]} for note in found] == expected, found


@then(parsers.parse('"{path}" in "{repository}" has {count:d} notes'))
def has_count_notes(app, path, repository, count):
    assert len(_notes(_file(app, repository, path))) == count


@then(parsers.parse('"{path}" in "{repository}" has {count:d} summaries, newest first, each with what it summarises'))
def has_summaries(app, students, path, repository, count):
    headings = [line for line in _file(app, repository, path).splitlines() if line.startswith("## Summary of ")]
    assert len(headings) == count, headings
    # the section's summary was asked for last
    assert headings[0].startswith("## Summary of the section 2 Shape functions, ")
    assert all(h.startswith("## Summary of the whole material, ") for h in headings[1:]), headings


@then(
    parsers.parse(
        '"{path}" in "{repository}" has the quiz\'s {count:d} questions, each with its choices, the correct one'
        " and the section it cites"
    )
)
def has_quiz(app, context, path, repository, count):
    markdown = _file(app, repository, path)
    context["quiz_file"] = markdown
    questions = re.findall(r"^\d+\. (.+) \*\((.+) › (.+)\)\*$", markdown, flags=re.M)
    assert len(questions) == count, markdown
    asked = context["got"][-1]["questions"]
    assert [q for q, _, _ in questions] == [q["question"] for q in asked]
    assert [(f, t) for _, f, t in questions] == [(q["source"]["filename"], q["source"]["title"]) for q in asked]
    choices = re.findall(r"^   - \[( |x)\] (.+)$", markdown, flags=re.M)
    assert [c for _, c in choices] == [choice for q in asked for choice in q["choices"]]
    assert [ticked for ticked, _ in choices].count("x") == count


@then(parsers.parse("it has my score of {score:d} out of {total:d}"))
def has_score(context, score, total):
    assert re.search(rf"^- {score} out of {total}, ", context["quiz_file"], flags=re.M), context["quiz_file"]


@then(parsers.parse('flashcards.csv in "{repository}" has {first:d} cards from "{one}" and {second:d} from "{other}"'))
def csv_cards(app, repository, first, one, second, other):
    cards = list(csv.DictReader(io.StringIO(_file(app, repository, "flashcards.csv"))))
    assert [card["material"] for card in cards].count(one) == first
    assert [card["material"] for card in cards].count(other) == second
    assert len(cards) == first + second


# what the student did


@given(parsers.parse('I have deleted the material "{filename}"'))
def have_deleted_material(students, filename):
    material = students.find_material(filename)
    response = students.delete(f"{material['course']}/{material['subject']}/{material['topic']}", filename)
    assert response.status_code in (200, 202, 204), response.text


@given(parsers.parse('I have deleted my note "{text}" of "{filename}"'))
def have_deleted_note(students, text, filename):
    material = students.find_material(filename)
    path = f"/api/courses/{material['course_id']}/materials/{material['document_id']}/notes"
    notes = students.client.get(path, headers=students.headers()).json()
    note = next(note for note in notes if note["text"] == text)
    response = students.client.delete(f"/api/notes/{note['id']}", headers=students.headers())
    assert response.status_code == 204, response.text
