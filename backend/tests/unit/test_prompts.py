import pytest

from qubit_notes import prompts


def names() -> list[str]:
    return prompts.Prompts().names()


@pytest.mark.parametrize("name", names())
def test_every_prompt_loads(name):
    assert prompts.load(name).strip()


def test_a_prompt_takes_its_values():
    assert "exactly 4 choices" in prompts.load("quiz", choices=4)


def test_a_value_the_prompt_does_not_take_is_refused():
    with pytest.raises(KeyError):
        prompts.load("summaries", choices=4)


def test_dollar_signs_and_braces_are_kept():
    assert "$ signs" in prompts.load("writing-assistant")


def test_every_released_version_is_as_it_was_released():
    # a change to a released version fails here: add a version instead, and release it with qubit-notes prompts lock
    assert [str(problem) for problem in prompts.Prompts().check()] == []


def test_every_prompt_toml_names_a_version_that_exists():
    prompts.Prompts().validate()


def test_a_loaded_prompt_has_its_name_and_version():
    loaded = prompts.load("summaries")
    assert (loaded.name, loaded.ref) == ("summaries", f"summaries@{loaded.version}")
