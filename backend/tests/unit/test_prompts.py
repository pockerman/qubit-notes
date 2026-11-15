from importlib.resources import files

import pytest

from qubit_notes import prompts


def names() -> list[str]:
    folders = files("qubit_notes.prompts").iterdir()
    return sorted(entry.name for entry in folders if entry.is_dir() and not entry.name.startswith("_"))


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
