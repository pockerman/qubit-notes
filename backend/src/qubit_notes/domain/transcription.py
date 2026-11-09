"""Answering by voice (features/transcription.feature): what a student says, recorded in their browser, as text heard
by one of OpenAI's transcription models. Recordings aren't kept."""

from pydantic import BaseModel

from qubit_notes.domain.errors import InvalidRequest, TooLarge, Unavailable
from qubit_notes.domain.usage import AIUsage
from qubit_notes.platform.port import StudyPlatform

# OpenAI takes recordings of at most 25 MB
MAX_RECORDING_BYTES = 25 * 1024 * 1024


class TranscriptionModel(BaseModel):
    id: str
    name: str


TRANSCRIPTION_MODELS = [
    TranscriptionModel(id="gpt-4o-mini-transcribe", name="GPT-4o mini Transcribe"),
    TranscriptionModel(id="gpt-4o-transcribe", name="GPT-4o Transcribe"),
    TranscriptionModel(id="whisper-1", name="Whisper"),
]
_MODELS = {model.id for model in TRANSCRIPTION_MODELS}


class TranscriptionModels(BaseModel):
    """the transcription models to choose from, the app's own, which hears it if none is chosen, and whether the app
    can hear"""

    models: list[TranscriptionModel]
    default: str
    available: bool


class Heard(BaseModel):
    text: str
    # the model that heard it
    model: str


class Transcription:
    def __init__(self, platform: StudyPlatform, ai: AIUsage, model: str = TRANSCRIPTION_MODELS[0].id):
        self._platform = platform
        self._ai = ai
        self._model = model if model in _MODELS else TRANSCRIPTION_MODELS[0].id

    def models(self) -> TranscriptionModels:
        return TranscriptionModels(
            models=TRANSCRIPTION_MODELS, default=self._model, available=self._platform.can_transcribe()
        )

    def transcribe(self, student: str, audio: bytes, content_type: str, model: str | None = None) -> Heard:
        """what the student said, as text"""
        model = model or self._model
        if model not in _MODELS:
            raise InvalidRequest(f"there is no transcription model {model!r}")
        if not audio:
            raise InvalidRequest("the recording is empty")
        if len(audio) > MAX_RECORDING_BYTES:
            raise TooLarge("a recording is at most 25 MB")
        if not self._platform.can_transcribe():
            raise Unavailable("answering by voice needs the app's OpenAI key, to hear what you say")
        heard = self._ai.transcribe(student, "transcription", audio, content_type or "audio/webm", model)
        return Heard(text=heard.text, model=heard.model)
