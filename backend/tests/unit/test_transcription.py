"""What a student says, heard by OpenAI's transcription models (features/transcription.feature), as its SDK gives it."""

from types import SimpleNamespace as Shape

import openai
import pytest

from qubit_notes.platform.port import PlatformError
from qubit_notes.platform.standalone.ai import ProviderAI
from qubit_notes.settings import Settings


def _openai(monkeypatch, heard) -> list[dict]:
    asked: list[dict] = []

    class Client:
        def __init__(self, api_key):
            assert api_key == "o-key"
            self.audio = Shape(transcriptions=self)

        def create(self, **arguments):
            asked.append(arguments)
            return heard

    monkeypatch.setattr(openai, "OpenAI", Client)
    return asked


def _ai(openai_key="o-key") -> ProviderAI:
    return ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key="a-key", openai_api_key=openai_key))


def test_heard_with_the_tokens_it_took(monkeypatch):
    asked = _openai(
        monkeypatch, Shape(text=" Shape functions interpolate. ", usage=Shape(input_tokens=7, output_tokens=3))
    )
    transcript = _ai().transcribe(b"recorded", "audio/webm;codecs=opus", "gpt-4o-mini-transcribe")

    assert transcript.text == "Shape functions interpolate."
    assert (transcript.provider, transcript.model) == ("openai", "gpt-4o-mini-transcribe")
    assert (transcript.input_tokens, transcript.output_tokens) == (7, 3)
    # OpenAI tells the recording's format by its name
    assert asked[0]["file"] == ("answer.webm", b"recorded", "audio/webm;codecs=opus")
    assert asked[0]["model"] == "gpt-4o-mini-transcribe"


def test_whisper_tells_no_tokens(monkeypatch):
    _openai(monkeypatch, Shape(text="Heard.", usage=Shape(type="duration", seconds=4)))
    transcript = _ai().transcribe(b"recorded", "audio/ogg", "whisper-1")

    assert (transcript.text, transcript.input_tokens, transcript.output_tokens) == ("Heard.", 0, 0)


def test_without_the_openai_key():
    with pytest.raises(PlatformError, match="FAILED_PRECONDITION"):
        _ai(openai_key=None).transcribe(b"recorded", "audio/webm", "whisper-1")
