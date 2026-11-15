"""The prompts the app gives the AI, one folder each: prompts/<name>/prompt.md.

A prompt can take values, written in it as {name}; load fills in only the ones it is given, so braces and dollar signs
elsewhere in a prompt are kept as they are.
"""

from functools import cache
from importlib.resources import files


@cache
def _text(name: str) -> str:
    return (files(__package__) / name / "prompt.md").read_text(encoding="utf-8").rstrip("\n")


def load(name: str, **values: object) -> str:
    """The prompt called name, with its {placeholders} filled in from values."""
    text = _text(name)
    for key, value in values.items():
        placeholder = "{" + key + "}"
        if placeholder not in text:
            raise KeyError(f"the {name} prompt has no {placeholder}")
        text = text.replace(placeholder, str(value))
    return text
