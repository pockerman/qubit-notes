import uuid

from pydantic import BaseModel

from study_assistant.platform.port import StudyPlatform

# the platform's memories are a user's key-value store; the assistant's notes about a student use this prefix
KEY_PREFIX = "note:"


class Note(BaseModel):
    """Something the assistant remembers about a student, and the documents it learned it from."""

    key: str
    text: str
    sources: list[str] = []


class StudentMemory:
    def __init__(self, platform: StudyPlatform):
        self._platform = platform

    def remember(self, student: str, text: str, sources: list[str]) -> Note:
        note = Note(key=f"{KEY_PREFIX}{uuid.uuid4().hex}", text=text, sources=sources)
        self._platform.save_memory(student, note.key, note.model_dump(include={"text", "sources"}))
        return note

    def notes(self, student: str) -> list[Note]:
        return [
            Note(key=key, **value)
            for key, value in self._platform.get_memories(student).items()
            if key.startswith(KEY_PREFIX)
        ]

    def forget_source(self, student: str, document_id: str) -> int:
        """Forget everything learned from the document; returns how many notes were forgotten."""
        forgotten = 0
        for note in self.notes(student):
            if document_id in note.sources:
                self._platform.delete_memory(student, note.key)
                forgotten += 1
        return forgotten
