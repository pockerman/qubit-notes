"""A stand-in for GitHub, for the scenarios of subject_repository.feature: repositories, what each token may do to
them, and their commits."""

import uuid
from dataclasses import dataclass, field

from qubit_notes.domain.subject_repositories import (
    Commit,
    PushRefused,
    RemoteRepository,
    RepositoryNotFound,
    blob_sha,
)


@dataclass
class FakeCommit:
    sha: str
    message: str
    # the files of the repository at this commit, by path
    files: dict[str, str]
    # the paths it wrote or removed
    changed: set[str]


@dataclass
class FakeRepository:
    name: str
    default_branch: str = "main"
    # what each token may do: "read" or "write"
    tokens: dict[str, str] = field(default_factory=dict)
    commits: list[FakeCommit] = field(default_factory=list)

    @property
    def files(self) -> dict[str, str]:
        return dict(self.commits[-1].files) if self.commits else {}

    def add_file(self, path: str, content: str) -> None:
        """a file the student committed themselves"""
        self.commits.append(FakeCommit(uuid.uuid4().hex, f"add {path}", {**self.files, path: content}, {path}))


class FakeGitHub:
    def __init__(self):
        self.repositories: dict[str, FakeRepository] = {}

    def add(self, name: str, token: str, may: str = "write") -> FakeRepository:
        repository = self.repositories.setdefault(name, FakeRepository(name))
        repository.tokens[token] = may
        return repository

    def repository(self, name: str, token: str) -> RemoteRepository:
        found = self.repositories.get(name)
        if found is None or token not in found.tokens:
            raise RepositoryNotFound(name)
        return RemoteRepository(
            name=found.name, default_branch=found.default_branch, writable=found.tokens[token] == "write"
        )

    def files(self, name: str, token: str, branch: str) -> dict[str, str]:
        found = self._found(name, token)
        assert branch == found.default_branch
        return {path: blob_sha(content) for path, content in found.files.items()}

    def commit(
        self, name: str, token: str, branch: str, write: dict[str, str], remove: list[str], message: str
    ) -> Commit:
        found = self._found(name, token)
        assert branch == found.default_branch
        if found.tokens[token] != "write":
            raise PushRefused(f"the token may not write to {name!r}")
        files = {path: content for path, content in found.files.items() if path not in remove}
        files.update(write)
        sha = uuid.uuid4().hex
        found.commits.append(FakeCommit(sha, message, files, set(write) | set(remove)))
        return Commit(sha=sha, url=f"https://github.com/{name}/commit/{sha}")

    def _found(self, name: str, token: str) -> FakeRepository:
        found = self.repositories.get(name)
        if found is None or token not in found.tokens:
            raise RepositoryNotFound(name)
        return found
