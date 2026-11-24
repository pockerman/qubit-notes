"""The GitHub client's calls of GitHub's REST API, against a stand-in for it."""

import json

import httpx
import pytest

from qubit_notes import github
from qubit_notes.domain.subject_repositories import PushRefused, RepositoryNotFound, blob_sha


class FakeAPI:
    """GitHub's API for one repository: its branch's commits, by the requests that make them"""

    def __init__(self, empty: bool = False, may_write: bool = True):
        self.head = None if empty else "c0"
        self.may_write = may_write
        self.requests: list[tuple[str, str, dict | None]] = []

    def __call__(self, method, url, headers, timeout, params=None, json=None):
        path = url.removeprefix(github.API)
        self.requests.append((method, path, json))
        assert headers["Authorization"] == "Bearer the-token"
        repo = "/repos/maria/notes"
        if method != "GET" and not self.may_write:
            return self._answer(403, {"message": "Resource not accessible by personal access token"})
        if (method, path) == ("GET", repo):
            return self._answer(
                200, {"full_name": "maria/notes", "default_branch": "main", "permissions": {"push": True}}
            )
        if (method, path) == ("GET", f"{repo}/git/trees/main"):
            if self.head is None:
                return self._answer(409, {"message": "Git Repository is empty."})
            return self._answer(200, {"tree": [{"path": "README.md", "type": "blob", "sha": "b1"}]})
        if (method, path) == ("GET", f"{repo}/git/ref/heads/main"):
            if self.head is None:
                return self._answer(409, {"message": "Git Repository is empty."})
            return self._answer(200, {"object": {"sha": self.head}})
        if (method, path) == ("PUT", f"{repo}/contents/README.md"):
            self.head = "c1"
            return self._answer(201, {"commit": {"sha": "c1", "html_url": "https://github.com/maria/notes/commit/c1"}})
        if method == "GET" and path.startswith(f"{repo}/git/commits/"):
            return self._answer(200, {"tree": {"sha": f"tree-of-{path.rsplit('/', 1)[1]}"}})
        if (method, path) == ("POST", f"{repo}/git/trees"):
            return self._answer(201, {"sha": "t2"})
        if (method, path) == ("POST", f"{repo}/git/commits"):
            return self._answer(201, {"sha": "c2", "html_url": "https://github.com/maria/notes/commit/c2"})
        if (method, path) == ("PATCH", f"{repo}/git/refs/heads/main"):
            self.head = json["sha"]
            return self._answer(200, {})
        return self._answer(404, {"message": "Not Found"})

    @staticmethod
    def _answer(status: int, body: dict) -> httpx.Response:
        return httpx.Response(status, content=json.dumps(body).encode())


@pytest.fixture
def api(monkeypatch) -> FakeAPI:
    fake = FakeAPI()
    monkeypatch.setattr(github.httpx, "request", fake)
    return fake


def test_a_repository_the_token_may_write_to(api):
    found = github.GitHub().repository("maria/notes", "the-token")
    assert (found.name, found.default_branch, found.writable) == ("maria/notes", "main", True)


def test_a_repository_the_token_cant_see(api):
    with pytest.raises(RepositoryNotFound):
        github.GitHub().repository("maria/other", "the-token")


def test_the_files_of_a_branch(api):
    assert github.GitHub().files("maria/notes", "the-token", "main") == {"README.md": "b1"}


def test_an_empty_repository_has_no_files(api):
    api.head = None
    assert github.GitHub().files("maria/notes", "the-token", "main") == {}


def test_one_commit_writes_and_removes_files(api):
    commit = github.GitHub().commit(
        "maria/notes", "the-token", "main", {"a/notes.md": "# Notes\n"}, ["old/notes.md"], "Qubit Notes: FEM"
    )
    assert (commit.sha, api.head) == ("c2", "c2")
    tree = next(
        body for method, path, body in api.requests if (method, path) == ("POST", "/repos/maria/notes/git/trees")
    )
    assert tree == {
        "base_tree": "tree-of-c0",
        "tree": [
            {"path": "a/notes.md", "mode": "100644", "type": "blob", "content": "# Notes\n"},
            {"path": "old/notes.md", "mode": "100644", "type": "blob", "sha": None},
        ],
    }
    made = next(
        body for method, path, body in api.requests if (method, path) == ("POST", "/repos/maria/notes/git/commits")
    )
    assert made == {"message": "Qubit Notes: FEM", "tree": "t2", "parents": ["c0"]}


def test_an_empty_repository_gets_its_readme_first(api):
    api.head = None
    commit = github.GitHub().commit(
        "maria/notes", "the-token", "main", {"README.md": "# FEM\n", "a/notes.md": "# Notes\n"}, [], "Qubit Notes"
    )
    assert commit.sha == "c2"
    created = next(body for method, path, body in api.requests if method == "PUT")
    assert created["message"] == "Qubit Notes"
    tree = next(
        body for method, path, body in api.requests if (method, path) == ("POST", "/repos/maria/notes/git/trees")
    )
    assert [entry["path"] for entry in tree["tree"]] == ["a/notes.md"]
    assert tree["base_tree"] == "tree-of-c1"


def test_an_empty_repository_with_only_a_readme(api):
    api.head = None
    commit = github.GitHub().commit("maria/notes", "the-token", "main", {"README.md": "# FEM\n"}, [], "Qubit Notes")
    assert commit.sha == "c1"


def test_a_push_the_token_may_not_make_is_refused(api):
    api.may_write = False
    with pytest.raises(PushRefused, match="may not write to 'maria/notes'"):
        github.GitHub().commit("maria/notes", "the-token", "main", {"README.md": "# FEM\n"}, [], "Qubit Notes")


def test_a_blob_sha_is_gits():
    # git hash-object of a file holding "hello\n"
    assert blob_sha("hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"
