"""GitHub, where students push their subjects to (domain/subject_repositories.py), through its REST API: one commit of
many files is a tree on the branch's last commit, a commit of it, and the branch moved to that commit."""

import base64

import httpx

from qubit_notes.domain.errors import Unavailable
from qubit_notes.domain.subject_repositories import Commit, PushRefused, RemoteRepository, RepositoryNotFound

API = "https://api.github.com"


class GitHub:
    def __init__(self, api: str = API, timeout: float = 30.0):
        self._api = api
        self._timeout = timeout

    def repository(self, name: str, token: str) -> RemoteRepository:
        response = self._request("GET", f"/repos/{name}", token)
        if response.status_code in (401, 403, 404):
            raise RepositoryNotFound(name)
        self._check(response)
        found = response.json()
        return RemoteRepository(
            name=found["full_name"],
            default_branch=found.get("default_branch") or "main",
            # what the token's owner may do; a fine-grained token that may only read is refused when it pushes
            writable=bool(found.get("permissions", {}).get("push")),
        )

    def files(self, name: str, token: str, branch: str) -> dict[str, str]:
        response = self._request("GET", f"/repos/{name}/git/trees/{branch}", token, params={"recursive": "1"})
        # an empty repository has no branch yet
        if response.status_code in (404, 409):
            return {}
        self._check(response)
        return {entry["path"]: entry["sha"] for entry in response.json()["tree"] if entry["type"] == "blob"}

    def commit(
        self, name: str, token: str, branch: str, write: dict[str, str], remove: list[str], message: str
    ) -> Commit:
        parent = self._head(name, token, branch)
        if parent is None:
            # the Git data API can't write to an empty repository: its first file makes its first commit
            path = "README.md" if "README.md" in write else next(iter(write))
            content = base64.b64encode(write[path].encode()).decode()
            created = self._write(
                "PUT", f"/repos/{name}/contents/{path}", token, {"message": message, "content": content}
            )
            write = {p: c for p, c in write.items() if p != path}
            if not write and not remove:
                return Commit(sha=created["commit"]["sha"], url=created["commit"]["html_url"])
            parent = self._head(name, token, branch)
        base = self._write("GET", f"/repos/{name}/git/commits/{parent}", token)["tree"]["sha"]
        entries = [{"path": p, "mode": "100644", "type": "blob", "content": c} for p, c in write.items()]
        entries += [{"path": p, "mode": "100644", "type": "blob", "sha": None} for p in remove]
        tree = self._write("POST", f"/repos/{name}/git/trees", token, {"base_tree": base, "tree": entries})
        commit = self._write(
            "POST", f"/repos/{name}/git/commits", token, {"message": message, "tree": tree["sha"], "parents": [parent]}
        )
        self._write("PATCH", f"/repos/{name}/git/refs/heads/{branch}", token, {"sha": commit["sha"]})
        return Commit(sha=commit["sha"], url=commit["html_url"])

    def _head(self, name: str, token: str, branch: str) -> str | None:
        response = self._request("GET", f"/repos/{name}/git/ref/heads/{branch}", token)
        if response.status_code in (404, 409):
            return None
        self._check(response)
        return response.json()["object"]["sha"]

    def _write(self, method: str, path: str, token: str, body: dict | None = None) -> dict:
        response = self._request(method, path, token, json=body)
        if response.status_code in (401, 403, 404):
            repository = "/".join(path.split("/")[2:4])
            raise PushRefused(f"the token may not write to {repository!r}")
        self._check(response)
        return response.json()

    def _request(self, method: str, path: str, token: str, **kwargs) -> httpx.Response:
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        try:
            return httpx.request(method, f"{self._api}{path}", headers=headers, timeout=self._timeout, **kwargs)
        except httpx.HTTPError as error:
            raise Unavailable(f"GitHub can't be reached: {error}") from None

    @staticmethod
    def _check(response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise Unavailable(f"GitHub answered {response.status_code}: {response.text[:200]}")
