import time
import uuid

from fastapi.testclient import TestClient
from httpx import Response

DEFAULT_CONTENT = {
    ".pdf": b"%PDF-1.4\n% minimal\n",
}


class Students:
    """The students of a scenario, and the API client to act as each of them.

    Student names get a suffix unique to the scenario, so scenarios run against a shared gogi platform don't
    see each other's courses or memories.
    """

    def __init__(self, client: TestClient, ingest_timeout_seconds: float):
        self.client = client
        self.suffix = uuid.uuid4().hex[:8]
        self.me = ""
        self.seen: set[str] = set()
        self._ingest_timeout_seconds = ingest_timeout_seconds

    def id(self, name: str) -> str:
        student_id = f"{name}-{self.suffix}"
        self.seen.add(student_id)
        return student_id

    def name(self, student_id: str) -> str:
        return student_id.removesuffix(f"-{self.suffix}")

    def headers(self, name: str | None = None) -> dict[str, str]:
        return {"X-Student-Id": self.id(name or self.me)}

    # actions

    def upload(self, location: str, filename: str, content: bytes | None = None, *, name: str | None = None):
        if content is None:
            content = DEFAULT_CONTENT.get(filename[filename.rfind(".") :], f"Notes on {location}.".encode())
        return self.client.post(
            "/api/materials",
            headers=self.headers(name),
            data={"location": location},
            files={"file": (filename, content)},
        )

    def wait_until_ingested(self, upload: Response) -> dict:
        assert upload.status_code == 202, upload.text
        deadline = time.monotonic() + self._ingest_timeout_seconds
        while True:
            job = self.client.get(f"/api/uploads/{upload.json()['job_id']}", headers=self.headers()).json()
            if job["status"] in ("completed", "failed") or time.monotonic() > deadline:
                assert job["status"] == "completed", job
                return job
            time.sleep(0.5)

    def upload_and_wait(self, location: str, filename: str, *, name: str | None = None) -> dict:
        return self.wait_until_ingested(self.upload(location, filename, name=name))

    def materials(self, course: str, *, name: str | None = None, subject: str = "", topic: str = "") -> list[dict]:
        params = {key: value for key, value in (("subject", subject), ("topic", topic)) if value}
        response = self.client.get(f"/api/courses/{course}/materials", headers=self.headers(name), params=params)
        assert response.status_code == 200, response.text
        return response.json()

    def courses(self, *, name: str | None = None) -> list[dict]:
        response = self.client.get("/api/courses", headers=self.headers(name))
        assert response.status_code == 200, response.text
        return response.json()

    def share(self, course: str, with_name: str, role: str, *, name: str | None = None) -> Response:
        return self.client.put(
            f"/api/courses/{course}/members",
            headers=self.headers(name),
            json={"student": self.id(with_name), "role": role},
        )

    def delete(self, location: str, filename: str, *, name: str | None = None) -> Response:
        course, subject, topic = location.split("/")
        return self.client.delete(
            f"/api/courses/{course}/materials/{subject}/{topic}/{filename}", headers=self.headers(name)
        )
