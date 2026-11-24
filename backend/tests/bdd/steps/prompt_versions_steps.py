"""Steps of prompt_versions.feature: the prompts' versions, the one in use, and what they are recorded with."""

import hashlib
from pathlib import Path

import pytest
from pytest_bdd import given, parsers, then, when

from qubit_notes import cli
from qubit_notes.app import create_app
from qubit_notes.prompts import Problem, Prompts, PromptsError

# the prompts the app uses
PROMPTS = [
    "audio-narration",
    "comprehension-check",
    "flashcards",
    "generating",
    "quiz",
    "study-assistant",
    "summaries",
    "writing-assistant",
]
# what the scenarios' version 2 of a prompt changes of its version 1: its first line, and a line added at the end
FIRST_LINE = "You write quizzes that test understanding rather than recall."
ADDED_LINE = "Write each question so that it can be answered in one sentence."


def _dir(app) -> Path:
    return Path(app.state.settings.prompts_dir)


def _prompts(app) -> Prompts:
    return Prompts(_dir(app))


def _file(app, name: str, version: int) -> Path:
    return _dir(app) / name / f"v{version}.md"


def _set_active(app, name: str, version: int) -> None:
    (_dir(app) / name / "prompt.toml").write_text(f"active = {version}\n", encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").rstrip("\n").encode()).hexdigest()


def _answering_ai(app):
    """the AI that answers the app's calls; a restart gives the app another platform, but not its calls"""
    return app.state.ai_usage._platform.ai


def _admin(students, context, name: str, method: str, path: str, **kwargs):
    context["response"] = students.client.request(
        method, f"/api/prompts{path}", headers=students.headers(name), **kwargs
    )
    return context["response"]


def _ok(context) -> dict | list:
    assert context["response"].status_code == 200, context["response"].text
    return context["response"].json()


# the prompts and their versions


@given(parsers.parse('the prompt "{name}" has the versions 1 and 2, with 2 in use'))
def has_two_versions(app, name):
    first, *rest = _file(app, name, 1).read_text(encoding="utf-8").rstrip("\n").split("\n")
    _file(app, name, 2).write_text("\n".join([FIRST_LINE, *rest, "", ADDED_LINE]) + "\n", encoding="utf-8")
    _set_active(app, name, 2)
    assert cli.main(["prompts", "lock", "--dir", str(_dir(app))]) == 0


@given(parsers.parse('prompt.toml of "{name}" names the version {version:d}'))
def names_version(app, name, version):
    _set_active(app, name, version)


@given(parsers.parse('the version {version:d} of the prompt "{name}" has been edited'))
def edited(app, name, version):
    path = _file(app, name, version)
    path.write_text(path.read_text(encoding="utf-8") + "\nAn edit after it was released.\n", encoding="utf-8")


@given(parsers.parse('the prompt "{name}" has a new version {version:d}'))
def new_version(app, name, version):
    text = _file(app, name, version - 1).read_text(encoding="utf-8")
    _file(app, name, version).write_text(text + f"\nVersion {version}.\n", encoding="utf-8")


@when("I lock the prompts")
def lock(app, context):
    context["locked"] = cli.main(["prompts", "lock", "--dir", str(_dir(app))])


@then(parsers.parse('the prompt "{name}" has a version in use, which is released'))
def in_use_and_released(app, name):
    prompts = _prompts(app)
    assert prompts.configured(name) in prompts.versions(name)
    assert [p for p in prompts.check() if p.prompt == name] == []


@then(parsers.parse('the AI was given the version {version:d} of the prompt "{name}"'))
def given_version(app, name, version):
    systems = [s for s in _answering_ai(app).systems if getattr(s, "name", None) == name]
    assert systems, f"the AI was given no {name} prompt"
    assert (systems[-1].version, systems[-1].sha256) == (version, _sha256(_file(app, name, version)))


@then(parsers.parse('the app refuses its prompts, as "{name}" has no version {version:d}'))
def refuses(app, platform, name, version):
    with pytest.raises(PromptsError, match=f"{name!r} has no version {version}"):
        create_app(platform=platform, settings=app.state.settings)


@then("the check of the prompts passes")
def check_passes(app):
    assert cli.main(["prompts", "check", "--dir", str(_dir(app))]) == 0


@then(parsers.parse('the check of the prompts fails, naming the version {version:d} of "{name}" as {kind}'))
def check_fails(app, capsys, name, version, kind):
    capsys.readouterr()
    assert cli.main(["prompts", "check", "--dir", str(_dir(app))]) == 1
    assert Problem(name, version, kind) in _prompts(app).check()
    assert str(Problem(name, version, kind)) in capsys.readouterr().err


@then(parsers.parse('the version {version:d} of "{name}" is released'))
def released(app, name, version):
    assert Problem(name, version, "not released") not in _prompts(app).check()
    assert f'["{name}"]' in (_dir(app) / "versions.lock").read_text(encoding="utf-8")


# what the prompts produce


@then(parsers.parse('its trace records the prompt "{name}" at the version {version:d}, with the SHA-256 of its text'))
def trace_records(app, students, context, name, version):
    me = students.id(students.me)
    traces = [t for t in context["tracer"].traces if t.info.student == me]
    calls = [step for t in traces for step in t.steps if step.prompt == name]
    assert calls
    assert (calls[-1].prompt_version, calls[-1].prompt_sha256) == (version, _sha256(_file(app, name, version)))


@then(parsers.parse('it is kept as written with the prompt "{name}" at the version in use'))
def kept_with_version(app, students, context, name):
    written = context["response"].json()
    in_use = _prompts(app).configured(name)
    assert written["prompt"] == f"{name}@{in_use}", written
    if context["asked_ai"] == "a question answered":
        # and kept with the conversation
        from tests.bdd.steps.assistant_steps import _conversation

        turns = _conversation(students, "fem-notes.md")["turns"]
        assert turns[-1]["prompt"] == f"{name}@{in_use}"


@then(parsers.parse('my quiz is kept as written with the prompt "{name}" at the version {version:d}'))
def quiz_kept(students, context, name, version):
    from tests.bdd.steps.study_steps import _document_scope

    written = context["quiz"] if "quiz" in context else None
    scope = _document_scope(students, "fem-notes.md")
    # the saved quiz, as it is given again
    response = students.client.post("/api/quizzes", headers=students.headers(), json={**scope, "questions": 1})
    assert response.status_code == 200, response.text
    assert response.json()["prompt"] == f"{name}@{version}"
    if written:
        assert response.json()["id"] == written["id"]


@given("I have asked the AI for a quiz, which is kept")
def asked_quiz(students, context):
    from tests.bdd.steps.usage_steps import _ask_ai

    context["quiz"] = _ask_ai(students, "a quiz").json()


# the admins


@when(parsers.parse('the admin "{name}" looks at the prompts'))
@when(parsers.parse('the student "{name}" looks at the prompts'))
def looks(students, context, name):
    _admin(students, context, name, "GET", "")


@then(
    parsers.parse(
        'they see the prompt "{prompt}" with the versions {first:d} and {second:d}, and {active:d} in use, '
        "as prompt.toml names it"
    )
)
def sees_prompt(context, prompt, first, second, active):
    found = next(p for p in _ok(context) if p["name"] == prompt)
    assert found["versions"] == [first, second]
    assert (found["active"], found["chosen_by"], found["configured"]) == (active, "prompt.toml", active)
    assert found["released"] == [first, second]


@then("they see every prompt the app uses")
def sees_every_prompt(context):
    assert [p["name"] for p in _ok(context)] == PROMPTS


@when(parsers.parse('the admin "{name}" reads the version {version:d} of the prompt "{prompt}"'))
def reads(students, context, name, version, prompt):
    _admin(students, context, name, "GET", f"/{prompt}/versions/{version}")


@then(parsers.parse('they see the text of the version {version:d} of "{prompt}"'))
def sees_text(app, context, version, prompt):
    read = _ok(context)
    assert (read["name"], read["version"]) == (prompt, version)
    assert read["text"] == _file(app, prompt, version).read_text(encoding="utf-8").rstrip("\n")


@when(parsers.parse('the admin "{name}" compares the versions {old:d} and {new:d} of the prompt "{prompt}"'))
def compares(students, context, name, old, new, prompt):
    _admin(students, context, name, "GET", f"/{prompt}/comparison", params={"old": old, "new": new})


@then(
    parsers.parse("they see the lines of the version {old:d} that the version {new:d} removes, and the lines it adds")
)
def sees_comparison(app, context, old, new):
    compared = _ok(context)
    first_line = _file(app, compared["name"], old).read_text(encoding="utf-8").split("\n")[0]
    assert compared["removed"] == [first_line]
    assert compared["added"] == [FIRST_LINE, "", ADDED_LINE]
    assert compared["diff"].startswith(f"--- {compared['name']} v{old}\n+++ {compared['name']} v{new}")


@when(parsers.parse('the admin "{name}" chooses the version {version:d} of the prompt "{prompt}"'))
@when(parsers.parse('the student "{name}" chooses the version {version:d} of the prompt "{prompt}"'))
def chooses(students, context, name, version, prompt):
    _admin(students, context, name, "PUT", f"/{prompt}/choice", json={"version": version})


@given(parsers.parse('the admin "{name}" has chosen the version {version:d} of the prompt "{prompt}"'))
def has_chosen(students, context, name, version, prompt):
    chooses(students, context, name, version, prompt)
    _ok(context)


@when(parsers.parse('the admin "{name}" chooses prompt.toml\'s version of the prompt "{prompt}"'))
def chooses_prompt_toml(students, context, name, prompt):
    _admin(students, context, name, "PUT", f"/{prompt}/choice", json={"version": None})
    assert _ok(context)["chosen_by"] == "prompt.toml"


@then(parsers.parse('the admin "{name}" sees the version {version:d} of "{prompt}" in use, as an admin chose it'))
def sees_chosen(students, context, name, version, prompt):
    _admin(students, context, name, "GET", "")
    found = next(p for p in _ok(context) if p["name"] == prompt)
    assert (found["active"], found["chosen_by"]) == (version, "admin")


@then("the choice is refused as not found")
def refused_not_found(context):
    assert context["response"].status_code == 404, context["response"].text


@then("the choice is refused as not allowed")
def refused_not_allowed(context):
    assert context["response"].status_code == 403, context["response"].text


@then("I am told only the app's admins can see them")
def only_admins(context):
    assert context["response"].status_code == 403, context["response"].text
    assert "only the app's admins" in context["response"].json()["detail"]
