"""The prompts the app gives the AI, one folder each: prompts/<name>/prompt.md.

A prompt can take values, written in it as {name}; load fills in only the ones it is given, so braces and dollar signs
elsewhere in a prompt are kept as they are.

A loaded prompt is a ``Prompt``: its text, which is a str, with its name and its version, which every call to the AI
is traced with (features/tracing.feature). The version is the start of the SHA-256 of the prompt's file, so any change
to the file is a new version.
"""

import hashlib
from functools import cache
from importlib.resources import files


class Prompt(str):
    """a prompt's text, with the name and the version of the prompt it is"""

    name: str
    version: str

    def __new__(cls, text: str, name: str, version: str) -> "Prompt":
        prompt = super().__new__(cls, text)
        prompt.name = name
        prompt.version = version
        return prompt


@cache
def _text(name: str) -> str:
    return (files(__package__) / name / "prompt.md").read_text(encoding="utf-8").rstrip("\n")


def version(name: str) -> str:
    """the version of the prompt called name"""
    return hashlib.sha256(_text(name).encode()).hexdigest()[:12]


def load(name: str, **values: object) -> Prompt:
    """The prompt called name, with its {placeholders} filled in from values."""
    text = _text(name)
    for key, value in values.items():
        placeholder = "{" + key + "}"
        if placeholder not in text:
            raise KeyError(f"the {name} prompt has no {placeholder}")
        text = text.replace(placeholder, str(value))
    return Prompt(text, name, version(name))
