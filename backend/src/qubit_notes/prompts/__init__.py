"""The prompts the app gives the AI, and their versions (features/prompt_versions.feature).

Each prompt is a folder, prompts/<name>/, with a file for each of its versions, v1.md, v2.md, …, and a prompt.toml that
names the version in use, e.g. ``active = 2``. A prompt is changed by adding a version; the version in use is changed
in prompt.toml, or by the app's admins from the app (``chosen``), which wins over prompt.toml.

A version once released never changes: versions.lock has the SHA-256 of every released version, and ``check`` tells
which versions differ from it, or aren't in it yet; ``lock`` adds the new versions to it (``qubit-notes prompts lock``).

A prompt can take values, written in it as {name}; load fills in only the ones it is given, so braces and dollar signs
elsewhere in a prompt are kept as they are. A loaded prompt is a ``Prompt``: its text, which is a str, with its name,
its version and the SHA-256 of its version's file, which what it produces is recorded with.

The app's prompts are those of ``use``: the package's own folder unless the app is given another.
"""

import hashlib
import re
import tomllib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from loguru import logger

DIRECTORY = Path(__file__).parent
LOCK = "versions.lock"
_VERSION = re.compile(r"^v(\d+)\.md$")


class Prompt(str):
    """a prompt's text, with the name, the version and the SHA-256 of the prompt it is"""

    name: str
    version: int
    sha256: str

    def __new__(cls, text: str, name: str, version: int, sha256: str) -> "Prompt":
        prompt = super().__new__(cls, text)
        prompt.name = name
        prompt.version = version
        prompt.sha256 = sha256
        return prompt

    @property
    def ref(self) -> str:
        """the prompt and its version, as what it produced is kept with, e.g. quiz@2"""
        return f"{self.name}@{self.version}"


class PromptsError(ValueError):
    """the prompts can't be used as they are, e.g. a prompt.toml names a version that doesn't exist"""


class NoSuchPrompt(LookupError):
    pass


@dataclass(frozen=True)
class Problem:
    """a version that is not as it was released, or not released"""

    prompt: str
    version: int
    kind: Literal["changed", "not released"]

    def __str__(self) -> str:
        if self.kind == "changed":
            return f"{self.prompt} v{self.version} has changed since it was released: add a new version instead"
        return f"{self.prompt} v{self.version} is not released: run qubit-notes prompts lock"


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


class Prompts:
    """The prompts of a folder. ``chosen`` tells the version of a prompt the admins chose, if any."""

    def __init__(self, directory: Path = DIRECTORY, chosen: Callable[[str], int | None] | None = None):
        self.directory = Path(directory)
        self._chosen = chosen or (lambda name: None)

    # the prompts and their versions

    def names(self) -> list[str]:
        return sorted(path.parent.name for path in self.directory.glob("*/prompt.toml"))

    def _folder(self, name: str) -> Path:
        folder = self.directory / name
        if "/" in name or name.startswith((".", "_")) or not (folder / "prompt.toml").is_file():
            raise NoSuchPrompt(f"there is no prompt {name!r}")
        return folder

    def versions(self, name: str) -> list[int]:
        """the prompt's versions, oldest first"""
        found = (_VERSION.match(path.name) for path in self._folder(name).iterdir())
        return sorted(int(match.group(1)) for match in found if match)

    def configured(self, name: str) -> int:
        """the version prompt.toml names"""
        with (self._folder(name) / "prompt.toml").open("rb") as file:
            active = tomllib.load(file).get("active")
        if not isinstance(active, int) or isinstance(active, bool):
            raise PromptsError(f"the prompt.toml of {name!r} names no version: write e.g. active = 1")
        return active

    def chosen(self, name: str) -> int | None:
        """the version the admins chose, if they chose one that exists"""
        version = self._chosen(name)
        if version is not None and version not in self.versions(name):
            logger.warning(f"the admins chose {name} v{version}, which doesn't exist: prompt.toml's is used")
            return None
        return version

    def active(self, name: str) -> int:
        """the version in use: the admins', else prompt.toml's"""
        chosen = self.chosen(name)
        return chosen if chosen is not None else self.configured(name)

    def text(self, name: str, version: int) -> str:
        path = self._folder(name) / f"v{version}.md"
        if not path.is_file():
            raise NoSuchPrompt(f"the prompt {name!r} has no version {version}")
        return path.read_text(encoding="utf-8").rstrip("\n")

    def validate(self) -> None:
        """raises PromptsError if a prompt.toml names a version that doesn't exist"""
        for name in self.names():
            configured = self.configured(name)
            if configured not in self.versions(name):
                raise PromptsError(
                    f"the prompt.toml of {name!r} names v{configured}: {name!r} has no version {configured}"
                )

    def load(self, name: str, **values: object) -> Prompt:
        """The prompt called name, at the version in use, with its {placeholders} filled in from values."""
        version = self.active(name)
        text = self.text(name, version)
        sha256 = _sha256(text)
        for key, value in values.items():
            placeholder = "{" + key + "}"
            if placeholder not in text:
                raise KeyError(f"the {name} prompt has no {placeholder}")
            text = text.replace(placeholder, str(value))
        return Prompt(text, name, version, sha256)

    # releasing

    def _locked(self) -> dict[str, dict[int, str]]:
        path = self.directory / LOCK
        if not path.is_file():
            return {}
        with path.open("rb") as file:
            return {name: {int(v): sha for v, sha in versions.items()} for name, versions in tomllib.load(file).items()}

    def check(self) -> list[Problem]:
        """the versions that differ from the ones released, or aren't released yet"""
        locked = self._locked()
        problems = []
        for name in self.names():
            for version in self.versions(name):
                released = locked.get(name, {}).get(version)
                if released is None:
                    problems.append(Problem(name, version, "not released"))
                elif released != _sha256(self.text(name, version)):
                    problems.append(Problem(name, version, "changed"))
        return problems

    def lock(self) -> list[tuple[str, int]]:
        """releases the versions not released yet; a released version is kept as it was released"""
        locked = self._locked()
        added = []
        for name in self.names():
            for version in self.versions(name):
                if version not in locked.setdefault(name, {}):
                    locked[name][version] = _sha256(self.text(name, version))
                    added.append((name, version))
        lines = [
            "# the SHA-256 of every released version of the prompts: written by qubit-notes prompts lock, not by hand"
        ]
        for name in sorted(locked):
            lines += ["", f'["{name}"]', *(f'{v} = "{sha}"' for v, sha in sorted(locked[name].items()))]
        (self.directory / LOCK).write_text("\n".join(lines) + "\n", encoding="utf-8")
        return added


_prompts = Prompts()


def use(prompts: Prompts) -> None:
    """the app's prompts from now on"""
    global _prompts
    _prompts = prompts


def current() -> Prompts:
    return _prompts


def load(name: str, **values: object) -> Prompt:
    """The app's prompt called name, at the version in use, with its {placeholders} filled in from values."""
    return _prompts.load(name, **values)
