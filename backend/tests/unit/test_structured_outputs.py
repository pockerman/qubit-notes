"""What the app asks Anthropic's models for when it needs JSON, e.g. a quiz: the answer as JSON of the schema, with
structured outputs, never by forcing a tool, which Claude Sonnet 5.5 and Opus 5.5 refuse."""

import json
from types import SimpleNamespace as Shape

import anthropic
import pytest

from qubit_notes.domain.assistant import Understood
from qubit_notes.domain.quizzes import WrittenQuiz
from qubit_notes.platform.port import PlatformError
from qubit_notes.platform.standalone.ai import ProviderAI
from qubit_notes.settings import Settings

QUIZ = {"questions": [{"question": "Why?", "choices": ["a", "b", "c", "d"], "answer": 1, "source": "S1"}]}


def _ai() -> ProviderAI:
    return ProviderAI(Settings(llm_provider="anthropic", anthropic_api_key="a-key"))


def _anthropic(monkeypatch, response) -> list[dict]:
    """Anthropic's client, answering with the response; what it was asked"""
    asked: list[dict] = []

    class Client:
        def __init__(self, api_key):
            self.messages = self

        def create(self, **arguments):
            asked.append(arguments)
            return response

    monkeypatch.setattr(anthropic, "Anthropic", Client)
    return asked


def _response(text: str | None, stop_reason: str = "end_turn"):
    content = [Shape(type="text", text=text)] if text is not None else []
    return Shape(content=content, stop_reason=stop_reason, usage=Shape(input_tokens=10, output_tokens=20))


def _objects(schema):
    """every object of a schema, its definitions' included"""
    if isinstance(schema, dict):
        if schema.get("type") == "object":
            yield schema
        for value in schema.values():
            yield from _objects(value)
    elif isinstance(schema, list):
        for value in schema:
            yield from _objects(value)


def test_json_is_asked_for_with_structured_outputs_not_a_forced_tool(monkeypatch):
    asked = _anthropic(monkeypatch, _response(json.dumps(QUIZ)))
    completion = _ai().complete("System", "Write a quiz", json_schema=WrittenQuiz.model_json_schema())
    assert json.loads(completion.text) == QUIZ
    (arguments,) = asked
    assert "tools" not in arguments and "tool_choice" not in arguments
    assert arguments["output_config"]["format"]["type"] == "json_schema"


@pytest.mark.parametrize("model", [WrittenQuiz, Understood])
def test_the_schema_is_one_the_api_takes(monkeypatch, model):
    asked = _anthropic(monkeypatch, _response(json.dumps(QUIZ)))
    _ai().complete("System", "Write it", json_schema=model.model_json_schema())
    schema = asked[0]["output_config"]["format"]["schema"]
    objects = list(_objects(schema))
    assert objects and all(o.get("additionalProperties") is False for o in objects)
    # defaults aren't taken: they're told in the field's description instead
    assert '"default"' not in json.dumps(schema)


def test_text_is_asked_for_as_text(monkeypatch):
    asked = _anthropic(monkeypatch, _response("An answer."))
    assert _ai().complete("System", "Ask").text == "An answer."
    assert "output_config" not in asked[0]


@pytest.mark.parametrize(
    "response, said",
    [
        (_response(None, stop_reason="refusal"), "declined"),
        (_response('{"questions": [', stop_reason="max_tokens"), "ran out of tokens"),
        (_response(None), "gave no answer"),
    ],
)
def test_an_answer_that_isnt_whole_json_is_a_failure(monkeypatch, response, said):
    _anthropic(monkeypatch, response)
    with pytest.raises(PlatformError, match=said):
        _ai().complete("System", "Write a quiz", json_schema=WrittenQuiz.model_json_schema())
