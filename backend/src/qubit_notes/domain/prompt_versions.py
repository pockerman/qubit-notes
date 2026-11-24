"""The prompts' versions, as the app's admins see and choose them (features/prompt_versions.feature).

The admins see every prompt, its versions and the one in use, read a version and compare two, line by line. The
version they choose of a prompt is kept in the app's settings in its database, and used rather than prompt.toml's
from then on, for everyone, until they choose prompt.toml's again.
"""

import difflib

from pydantic import BaseModel
from sqlalchemy import delete, insert, select
from sqlalchemy.engine import Engine

from qubit_notes import storage
from qubit_notes.domain.errors import NotAllowed, NotFound
from qubit_notes.prompts import NoSuchPrompt, Prompts

table = storage.app_settings
_KEY = "prompt:"


class PromptInUse(BaseModel):
    name: str
    versions: list[int]
    # the version in use, and whether an admin chose it, rather than prompt.toml
    active: int
    chosen_by: str
    # the version prompt.toml names
    configured: int
    # the versions released, so never changed (prompts/versions.lock)
    released: list[int]


class PromptVersion(BaseModel):
    name: str
    version: int
    text: str


class Comparison(BaseModel):
    """how one version of a prompt differs from another, line by line"""

    name: str
    old: int
    new: int
    removed: list[str]
    added: list[str]
    # the whole difference, as a unified diff
    diff: str


class PromptVersions:
    def __init__(self, engine: Engine, prompts: Prompts | None = None):
        self._engine = engine
        self.prompts = prompts or Prompts(chosen=self.chosen)

    def chosen(self, name: str) -> int | None:
        """the version of the prompt an admin chose, if they chose one"""
        with self._engine.connect() as connection:
            value = connection.execute(select(table.c.value).where(table.c.name == _KEY + name)).scalar()
        return int(value) if value is not None else None

    def overview(self, admin: bool) -> list[PromptInUse]:
        _only_admins(admin)
        not_released = self._not_released()
        return [self._in_use(name, not_released) for name in self.prompts.names()]

    def _not_released(self) -> set[tuple[str, int]]:
        return {(problem.prompt, problem.version) for problem in self.prompts.check()}

    def _in_use(self, name: str, not_released: set[tuple[str, int]]) -> PromptInUse:
        versions = self.prompts.versions(name)
        chosen = self.prompts.chosen(name)
        configured = self.prompts.configured(name)
        return PromptInUse(
            name=name,
            versions=versions,
            active=chosen if chosen is not None else configured,
            chosen_by="admin" if chosen is not None else "prompt.toml",
            configured=configured,
            released=[v for v in versions if (name, v) not in not_released],
        )

    def read(self, admin: bool, name: str, version: int) -> PromptVersion:
        _only_admins(admin)
        return PromptVersion(name=name, version=version, text=self._text(name, version))

    def compare(self, admin: bool, name: str, old: int, new: int) -> Comparison:
        _only_admins(admin)
        before, after = self._text(name, old).splitlines(), self._text(name, new).splitlines()
        diff = list(difflib.unified_diff(before, after, f"{name} v{old}", f"{name} v{new}", lineterm=""))
        changed = [line for line in diff[2:] if not line.startswith("@@")]
        return Comparison(
            name=name,
            old=old,
            new=new,
            removed=[line[1:] for line in changed if line.startswith("-")],
            added=[line[1:] for line in changed if line.startswith("+")],
            diff="\n".join(diff),
        )

    def choose(self, admin: bool, name: str, version: int | None) -> PromptInUse:
        """the version used of the prompt from now on; None for prompt.toml's again"""
        _only_admins(admin)
        if version is not None and version not in self._versions(name):
            raise NotFound(f"the prompt {name!r} has no version {version}")
        if version is None:
            # the prompt must exist all the same
            self._versions(name)
        with self._engine.begin() as connection:
            connection.execute(delete(table).where(table.c.name == _KEY + name))
            if version is not None:
                connection.execute(insert(table).values(name=_KEY + name, value=str(version)))
        return self._in_use(name, self._not_released())

    def _versions(self, name: str) -> list[int]:
        try:
            return self.prompts.versions(name)
        except NoSuchPrompt as e:
            raise NotFound(str(e)) from e

    def _text(self, name: str, version: int) -> str:
        try:
            return self.prompts.text(name, version)
        except NoSuchPrompt as e:
            raise NotFound(str(e)) from e


def _only_admins(admin: bool) -> None:
    if not admin:
        raise NotAllowed("only the app's admins can see and choose the prompts")
